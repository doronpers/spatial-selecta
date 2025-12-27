"""
Main FastAPI application for Spatial Selecta.
Provides API endpoints for spatial audio track management and automatic detection.
"""
from fastapi import FastAPI, Depends, HTTPException, Header, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import logging
import os
import time

from backend.database import get_db, init_db
from backend.models import Track
from backend.schemas import TrackResponse, RefreshResponse
from backend.scheduler import start_scheduler, trigger_manual_refresh

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Spatial Selecta API",
    description="API for tracking spatial audio releases from Apple Music",
    version="1.0.0"
)

# Security Configuration
# In production, NEVER use "*" - specify exact origins
ALLOWED_ORIGINS_ENV = os.getenv("ALLOWED_ORIGINS", "")
IS_PRODUCTION = os.getenv("ENVIRONMENT", "development").lower() == "production"

if IS_PRODUCTION:
    if not ALLOWED_ORIGINS_ENV or ALLOWED_ORIGINS_ENV == "*":
        logger.warning("SECURITY WARNING: CORS is set to '*' in production. This is insecure!")
        logger.warning("Set ALLOWED_ORIGINS environment variable to specific origins.")
        # In production, default to empty list (no CORS) if not configured
        ALLOWED_ORIGINS = []
    else:
        ALLOWED_ORIGINS = [origin.strip() for origin in ALLOWED_ORIGINS_ENV.split(",") if origin.strip()]
else:
    # Development: allow localhost origins
    if ALLOWED_ORIGINS_ENV and ALLOWED_ORIGINS_ENV != "*":
        ALLOWED_ORIGINS = [origin.strip() for origin in ALLOWED_ORIGINS_ENV.split(",") if origin.strip()]
    else:
        ALLOWED_ORIGINS = ["http://localhost:8080", "http://localhost:3000", "http://127.0.0.1:8080"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Rate limiting storage (in-memory, simple implementation)
# NOTE: This is a basic implementation suitable for single-instance deployments.
# For production with multiple instances, use Redis or similar distributed cache.
rate_limit_store = {}
RATE_LIMIT_WINDOW = 60  # seconds
RATE_LIMIT_MAX_REQUESTS = 100  # per window per IP
_last_cleanup_time = time.time()
CLEANUP_INTERVAL = 300  # Clean up old entries every 5 minutes


def _cleanup_rate_limit_store():
    """Periodically clean up old rate limit entries to prevent memory leaks."""
    global _last_cleanup_time
    current_time = time.time()
    
    # Only cleanup every CLEANUP_INTERVAL seconds
    if current_time - _last_cleanup_time < CLEANUP_INTERVAL:
        return
    
    _last_cleanup_time = current_time
    cutoff_time = current_time - RATE_LIMIT_WINDOW
    
    # Remove IPs with no recent requests
    ips_to_remove = [
        ip for ip, req_times in rate_limit_store.items()
        if not req_times or max(req_times, default=0) < cutoff_time
    ]
    for ip in ips_to_remove:
        del rate_limit_store[ip]
    
    # Clean old requests from remaining IPs
    for ip in list(rate_limit_store.keys()):
        rate_limit_store[ip] = [
            req_time for req_time in rate_limit_store[ip]
            if req_time >= cutoff_time
        ]


# Rate limiting function
def check_rate_limit(client_ip: str) -> bool:
    """
    Check if client has exceeded rate limit.
    
    Args:
        client_ip: Client IP address
        
    Returns:
        True if within limit, False if exceeded
    """
    current_time = time.time()
    
    # Periodic cleanup to prevent memory leaks
    _cleanup_rate_limit_store()
    
    # Initialize IP entry if not exists
    if client_ip not in rate_limit_store:
        rate_limit_store[client_ip] = []
    
    # Clean old entries for this IP
    cutoff_time = current_time - RATE_LIMIT_WINDOW
    rate_limit_store[client_ip] = [
        req_time for req_time in rate_limit_store[client_ip]
        if req_time >= cutoff_time
    ]
    
    # Check limit
    if len(rate_limit_store[client_ip]) >= RATE_LIMIT_MAX_REQUESTS:
        return False
    
    # Add current request
    rate_limit_store[client_ip].append(current_time)
    return True


def get_client_ip(request: Request) -> str:
    """Extract client IP from request."""
    # Check for forwarded IP (when behind proxy)
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


# Authentication for sensitive endpoints
def verify_refresh_token(authorization: Optional[str] = Header(None)) -> bool:
    """
    Verify refresh token for /api/refresh endpoint.
    Uses simple token-based auth. In production, use proper JWT or API keys.
    """
    refresh_token = os.getenv("REFRESH_API_TOKEN")
    
    if not refresh_token:
        # If no token configured, allow in development but warn
        if not IS_PRODUCTION:
            logger.warning("REFRESH_API_TOKEN not set - allowing refresh in development mode")
            return True
        else:
            logger.error("REFRESH_API_TOKEN not set in production - denying access")
            return False
    
    if not authorization or not authorization.startswith("Bearer "):
        return False
    
    token = authorization.replace("Bearer ", "").strip()
    return token == refresh_token


@app.on_event("startup")
async def startup_event():
    """Initialize database and start background scheduler on app startup."""
    logger.info("Starting Spatial Selecta API...")
    init_db()
    start_scheduler()
    logger.info("Application started successfully")
    
    # Security warnings
    if IS_PRODUCTION:
        if not os.getenv("REFRESH_API_TOKEN"):
            logger.warning("SECURITY WARNING: REFRESH_API_TOKEN not set in production")
        if not ALLOWED_ORIGINS_ENV or ALLOWED_ORIGINS_ENV == "*":
            logger.warning("SECURITY WARNING: CORS allows all origins in production")


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Spatial Selecta API",
        "version": "1.0.0",
        "description": "Automatic tracking of spatial audio releases"
    }


@app.get("/api/tracks", response_model=List[TrackResponse])
async def get_tracks(
    request: Request,
    platform: Optional[str] = Query(None, max_length=50),
    format: Optional[str] = Query(None, max_length=50),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0, le=10000),
    db: Session = Depends(get_db)
):
    """
    Get all spatial audio tracks with optional filtering.
    
    Args:
        platform: Filter by platform (Apple Music, Amazon Music)
        format: Filter by audio format (Dolby Atmos, 360 Reality Audio)
        limit: Maximum number of tracks to return (1-1000)
        offset: Number of tracks to skip (0-10000)
        db: Database session
    
    Returns:
        List of tracks matching the filters
    """
    # Rate limiting
    client_ip = get_client_ip(request)
    if not check_rate_limit(client_ip):
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Please try again later.")
    
    # Validate platform and format values to prevent injection
    valid_platforms = ["Apple Music"]
    valid_formats = ["Dolby Atmos"]
    
    query = db.query(Track)
    
    if platform:
        if platform not in valid_platforms:
            raise HTTPException(status_code=400, detail=f"Invalid platform. Must be one of: {', '.join(valid_platforms)}")
        query = query.filter(Track.platform == platform)
    
    if format:
        if format not in valid_formats:
            raise HTTPException(status_code=400, detail=f"Invalid format. Must be one of: {', '.join(valid_formats)}")
        query = query.filter(Track.format == format)
    
    # Order by release date descending (newest first)
    query = query.order_by(Track.release_date.desc())
    
    tracks = query.offset(offset).limit(limit).all()
    return tracks


@app.get("/api/tracks/new", response_model=List[TrackResponse])
async def get_new_tracks(
    request: Request,
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """
    Get tracks released within the specified number of days.
    
    Args:
        days: Number of days to look back (1-365, default: 30)
        db: Database session
    
    Returns:
        List of recently released tracks
    """
    # Rate limiting
    client_ip = get_client_ip(request)
    if not check_rate_limit(client_ip):
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Please try again later.")
    
    try:
        cutoff_date = datetime.now() - timedelta(days=days)
        tracks = db.query(Track).filter(
            Track.release_date >= cutoff_date
        ).order_by(Track.release_date.desc()).all()
        
        return tracks
    except Exception as e:
        logger.error(f"Error fetching new tracks: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while fetching tracks")


@app.get("/api/tracks/{track_id}", response_model=TrackResponse)
async def get_track(
    request: Request,
    track_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific track by ID.
    
    Args:
        track_id: Track ID (must be positive integer)
        db: Database session
    
    Returns:
        Track details
    """
    # Rate limiting
    client_ip = get_client_ip(request)
    if not check_rate_limit(client_ip):
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Please try again later.")
    
    # Validate track_id is positive
    if track_id <= 0 or track_id > 2147483647:
        raise HTTPException(status_code=400, detail="Track ID must be a positive integer")
    
    try:
        track = db.query(Track).filter(Track.id == track_id).first()
        if not track:
            raise HTTPException(status_code=404, detail="Track not found")
        return track
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching track {track_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while fetching track")


@app.post("/api/refresh", response_model=RefreshResponse)
async def refresh_data(
    request: Request,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Manually trigger a refresh of spatial audio data.
    Requires authentication via Bearer token.
    
    Args:
        authorization: Bearer token in Authorization header
        db: Database session
    
    Returns:
        Refresh status and statistics
    """
    # Rate limiting (stricter for authenticated endpoint)
    client_ip = get_client_ip(request)
    if not check_rate_limit(client_ip):
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Please try again later.")
    
    # Authentication check
    if not verify_refresh_token(authorization):
        raise HTTPException(
            status_code=401,
            detail="Unauthorized. Valid Bearer token required.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        result = await trigger_manual_refresh(db)
        logger.info(f"Manual refresh triggered by {client_ip}")
        return result
    except Exception as e:
        logger.error(f"Error during manual refresh: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during refresh")


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/stats")
async def get_stats(request: Request, db: Session = Depends(get_db)):
    """
    Get statistics about the spatial audio database.
    
    Args:
        db: Database session
    
    Returns:
        Statistics including total tracks, tracks by platform, etc.
    """
    # Rate limiting
    client_ip = get_client_ip(request)
    if not check_rate_limit(client_ip):
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Please try again later.")
    
    total_tracks = db.query(Track).count()
    dolby_atmos_tracks = db.query(Track).filter(Track.format == "Dolby Atmos").count()

    cutoff_date = datetime.now() - timedelta(days=30)
    new_tracks = db.query(Track).filter(Track.release_date >= cutoff_date).count()

    return {
        "total_tracks": total_tracks,
        "by_platform": {
            "Apple Music": total_tracks
        },
        "by_format": {
            "Dolby Atmos": dolby_atmos_tracks
        },
        "new_tracks_last_30_days": new_tracks
    }
