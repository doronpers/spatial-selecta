"""
Main FastAPI application for SpatialSelects.com.
Provides API endpoints for spatial audio track management and automatic detection.
"""
from fastapi import FastAPI, Depends, HTTPException, Header, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from starlette.requests import Request as StarletteRequest
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime, timedelta
import logging
import os
import time
import hmac
import hashlib

from backend.database import get_db, init_db
from backend.models import Track, CommunityRating, Engineer, TrackCredit
from backend.schemas import TrackResponse, RefreshResponse, RatingRequest, RatingResponse, EngineerResponse
from backend.scheduler import start_scheduler, trigger_manual_refresh

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="SpatialSelects.com API",
    description="API for tracking spatial audio releases from Apple Music",
    version="1.0.0",
    docs_url="/docs" if not os.getenv("ENVIRONMENT") == "production" else None,
    redoc_url="/redoc" if not os.getenv("ENVIRONMENT") == "production" else None,
)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add security headers to all responses."""
    
    async def dispatch(self, request: StarletteRequest, call_next):
        # Check request size (basic protection)
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                size = int(content_length)
                if size > MAX_REQUEST_SIZE:
                    return Response(
                        content="Request too large",
                        status_code=413,
                        headers={"Content-Type": "text/plain"}
                    )
            except ValueError:
                pass  # Invalid content-length, let it through
        
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # HSTS (only in production with HTTPS)
        if IS_PRODUCTION:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
            response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self';"
        # Remove server header (information disclosure)
        if "server" in response.headers:
            del response.headers["server"]
        
        return response

# Add security headers middleware
app.add_middleware(SecurityHeadersMiddleware)

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
RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "60"))  # seconds
RATE_LIMIT_MAX_REQUESTS = int(os.getenv("RATE_LIMIT_MAX_REQUESTS", "100"))  # per window per IP
_last_cleanup_time = time.time()
CLEANUP_INTERVAL = 300  # Clean up old entries every 5 minutes

# Request size limits (prevent DoS via large payloads)
MAX_REQUEST_SIZE = 1024 * 1024  # 1MB


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
    # Prevent rate limit store from growing unbounded
    if len(rate_limit_store) > 10000:  # Max 10k unique IPs
        logger.warning("Rate limit store size exceeded threshold, performing aggressive cleanup")
        _cleanup_rate_limit_store()
        # If still too large, clear oldest entries
        if len(rate_limit_store) > 10000:
            sorted_ips = sorted(
                rate_limit_store.items(),
                key=lambda x: max(x[1], default=0),
                reverse=True
            )
            # Keep only top 5000 most recent IPs
            rate_limit_store.clear()
            rate_limit_store.update(dict(sorted_ips[:5000]))
    
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
        logger.warning(f"Rate limit exceeded for IP: {client_ip[:8]}...")
        return False
    
    # Add current request
    rate_limit_store[client_ip].append(current_time)
    return True


def get_client_ip(request: Request) -> str:
    """
    Extract client IP from request.
    Handles various proxy headers securely.
    """
    # Priority order for IP extraction (most trusted first)
    # X-Real-IP is typically set by reverse proxies (nginx, etc.)
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        # Validate IP format (basic check)
        ip_parts = real_ip.strip().split(".")
        if len(ip_parts) == 4 and all(part.isdigit() and 0 <= int(part) <= 255 for part in ip_parts):
            return real_ip.strip()
    
    # X-Forwarded-For can be spoofed, so we take the first (original) IP
    # Only trust if we're behind a known proxy (check via environment)
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded and os.getenv("TRUST_PROXY", "false").lower() == "true":
        # Take first IP in chain (original client)
        first_ip = forwarded.split(",")[0].strip()
        # Basic validation
        if first_ip and not first_ip.startswith("unknown"):
            return first_ip
    
    # Fallback to direct connection IP
    if request.client:
        return request.client.host
    
    return "unknown"


# Authentication for sensitive endpoints
def verify_refresh_token(authorization: Optional[str] = Header(None)) -> bool:
    """
    Verify refresh token for /api/refresh endpoint.
    Uses constant-time comparison to prevent timing attacks.
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
    
    # Use constant-time comparison to prevent timing attacks
    # This ensures the comparison takes the same time regardless of where the mismatch occurs
    if len(token) != len(refresh_token):
        return False
    
    # Use hmac.compare_digest for constant-time comparison
    return hmac.compare_digest(token.encode('utf-8'), refresh_token.encode('utf-8'))


@app.on_event("startup")
async def startup_event():
    """Initialize database and start background scheduler on app startup."""
    logger.info("Starting SpatialSelects.com API...")
    init_db()
    start_scheduler()
    logger.info("Application started successfully")
    
    # Security warnings
    if IS_PRODUCTION:
        if not os.getenv("REFRESH_API_TOKEN"):
            logger.warning("SECURITY WARNING: REFRESH_API_TOKEN not set in production")
        if not ALLOWED_ORIGINS_ENV or ALLOWED_ORIGINS_ENV == "*":
            logger.warning("SECURITY WARNING: CORS allows all origins in production")
        if os.getenv("RATING_IP_SALT", "default-salt-change-in-production") == "default-salt-change-in-production":
            logger.warning("SECURITY WARNING: Using default RATING_IP_SALT in production - set a secure random value")


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "SpatialSelects.com API",
        "version": "1.0.0",
        "description": "Automatic tracking of spatial audio releases"
    }


@app.get("/api/tracks", response_model=List[TrackResponse])
async def get_tracks(
    request: Request,
    platform: Optional[str] = Query(None, max_length=50, description="Filter by platform"),
    format: Optional[str] = Query(None, max_length=50, description="Filter by audio format"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of tracks to return"),
    offset: int = Query(0, ge=0, le=10000, description="Number of tracks to skip"),
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
    valid_platforms = ["Apple Music", "Amazon Music"]
    valid_formats = ["Dolby Atmos", "360 Reality Audio"]
    
    query = db.query(Track).options(
        joinedload(Track.credits).joinedload(TrackCredit.engineer)
    )
    
    if platform:
        if platform not in valid_platforms:
            raise HTTPException(status_code=400, detail=f"Invalid platform. Must be one of: {', '.join(valid_platforms)}")
        query = query.filter(Track.platform == platform)
    
    if format:
        if format not in valid_formats:
            raise HTTPException(status_code=400, detail=f"Invalid format. Must be one of: {', '.join(valid_formats)}")
        query = query.filter(Track.format == format)
    
    # Order by Atmos release date descending (newest first), fallback to release_date
    # Use nullslast() to put tracks without atmos_release_date at the end
    from sqlalchemy import desc, nullslast
    query = query.order_by(
        nullslast(desc(Track.atmos_release_date)),
        desc(Track.release_date)
    )
    
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
        tracks = db.query(Track).options(
            joinedload(Track.credits).joinedload(TrackCredit.engineer)
        ).filter(
            Track.release_date >= cutoff_date
        ).order_by(Track.release_date.desc()).all()
        
        return tracks
    except Exception as e:
        logger.error(f"Error fetching new tracks: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error while fetching tracks. Please try again later."
        )


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
        track = db.query(Track).options(
            joinedload(Track.credits).joinedload(TrackCredit.engineer)
        ).filter(Track.id == track_id).first()
        if not track:
            raise HTTPException(status_code=404, detail="Track not found")
        return track
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching track {track_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error while fetching track. Please try again later."
        )


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
        # Log without sensitive information
        logger.info(f"Manual refresh triggered by IP: {client_ip[:8]}...")
        return result
    except HTTPException:
        raise
    except Exception as e:
        # Log full error internally but don't expose details to client
        logger.error(f"Error during manual refresh: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error during refresh. Please try again later."
        )


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


# Public refresh rate limiting - much stricter (1 per hour per IP)
# NOTE: This is in-memory only and will be lost on server restart.
# For production with multiple instances or persistent rate limiting,
# consider using Redis or database-backed storage.
# This is acceptable for single-instance deployments where occasional
# rate limit resets on restart are acceptable.
public_refresh_store = {}
PUBLIC_REFRESH_COOLDOWN = 3600  # 1 hour in seconds


def check_public_refresh_limit(client_ip: str) -> tuple[bool, int]:
    """
    Check if client can trigger a public refresh.

    Returns:
        Tuple of (allowed, seconds_remaining)
    """
    current_time = time.time()

    if client_ip in public_refresh_store:
        last_refresh = public_refresh_store[client_ip]
        elapsed = current_time - last_refresh
        if elapsed < PUBLIC_REFRESH_COOLDOWN:
            return False, int(PUBLIC_REFRESH_COOLDOWN - elapsed)

    return True, 0


@app.post("/api/refresh/sync", response_model=RefreshResponse)
async def public_refresh_data(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Public endpoint to trigger a refresh of spatial audio data.
    Rate limited to once per hour per IP address.

    This allows website visitors to manually trigger a data sync
    without requiring authentication.

    Returns:
        Refresh status and statistics
    """
    client_ip = get_client_ip(request)

    # Check public refresh rate limit
    allowed, seconds_remaining = check_public_refresh_limit(client_ip)
    if not allowed:
        minutes_remaining = seconds_remaining // 60
        raise HTTPException(
            status_code=429,
            detail=f"Refresh limit reached. Please try again in {minutes_remaining} minutes.",
            headers={"Retry-After": str(seconds_remaining)}
        )

    try:
        # Record this refresh
        public_refresh_store[client_ip] = time.time()

        result = await trigger_manual_refresh(db)
        logger.info(f"Public refresh triggered by {client_ip}: {result.tracks_added} added, {result.tracks_updated} updated")
        return result
    except Exception as e:
        # Remove the record if refresh failed so they can retry
        if client_ip in public_refresh_store:
            del public_refresh_store[client_ip]
        logger.error(f"Error during public refresh: {e}")
        raise HTTPException(status_code=500, detail="Error refreshing data. Please try again later.")


@app.get("/api/refresh/status")
async def get_refresh_status(request: Request):
    """
    Check if a public refresh is available for this client.

    Returns:
        Whether refresh is available and time until next refresh
    """
    client_ip = get_client_ip(request)
    allowed, seconds_remaining = check_public_refresh_limit(client_ip)

    return {
        "can_refresh": allowed,
        "seconds_until_available": seconds_remaining,
        "cooldown_minutes": PUBLIC_REFRESH_COOLDOWN // 60
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


# Phase 3: Community & Quality API
@app.post("/api/tracks/{track_id}/rate", response_model=RatingResponse)
async def rate_track(
    request: Request,
    track_id: int,
    rating: RatingRequest,
    db: Session = Depends(get_db)
):
    """
    Submit a community rating used for "Hall of Shame" or quality score.
    """
    client_ip = get_client_ip(request)
    if not check_rate_limit(client_ip):
         raise HTTPException(status_code=429, detail="Rate limit exceeded.")
    
    # Check if track exists
    track = db.query(Track).filter(Track.id == track_id).first()
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")
        
    # Create simple IP hash with consistent salt from environment
    # This allows detecting duplicate votes from same IP while maintaining privacy
    salt = os.getenv("RATING_IP_SALT", "default-salt-change-in-production")
    ip_hash = hashlib.sha256(f"{client_ip}{salt}".encode()).hexdigest()
    
    # Save rating
    new_rating = CommunityRating(
        track_id=track_id,
        immersiveness_score=rating.score,
        is_fake_atmos=rating.is_fake,
        user_ip_hash=ip_hash
    )
    db.add(new_rating)
    db.commit()
    
    # Calculate new averages
    # (In high scale, do this async/background, but here inline is fine)
    avg_score = db.query(func.avg(CommunityRating.immersiveness_score)).filter(CommunityRating.track_id == track_id).scalar()
    fake_count = db.query(CommunityRating).filter(CommunityRating.track_id == track_id, CommunityRating.is_fake_atmos).count()
    total = db.query(CommunityRating).filter(CommunityRating.track_id == track_id).count()
    avg_value = float(avg_score) if avg_score is not None else 0.0

    # Update track cache via SQLAlchemy's update method since direct attribute assignment to Column[Unknown] is not allowed.
    update_data = {}
    update_data['avg_immersiveness'] = avg_value

    # Determine hall of shame threshold (e.g., >30% fake reports with >5 votes)
    if total > 5 and (fake_count / total) > 0.3:
        update_data['hall_of_shame'] = True

    if update_data:
        db.query(Track).filter(Track.id == track_id).update(update_data, synchronize_session=False)

    db.commit()
    
    return {
        "track_id": track_id,
        "avg_immersiveness": avg_value,
        "is_fake_atmos_ratio": fake_count / total if total > 0 else 0.0
    }


@app.get("/api/engineers", response_model=List[EngineerResponse])
async def get_engineers(
    request: Request,
    limit: int = 50,
    min_mixes: int = 1,
    db: Session = Depends(get_db)
):
    """
    Get list of engineers sorted by mix count.
    """
    # Group by engineer and count track credits
    # This query might need optimization for large datasets
    results = db.query(
        Engineer, 
        func.count(TrackCredit.id).label('count')
    ).join(TrackCredit).group_by(Engineer.id).having(func.count(TrackCredit.id) >= min_mixes).order_by(func.count(TrackCredit.id).desc()).limit(limit).all()
    
    response = []
    for eng, count in results:
        resp = EngineerResponse.model_validate(eng)
        resp.mix_count = count
        response.append(resp)
        
    return response


@app.get("/api/engineers/{engineer_id}", response_model=EngineerResponse)
async def get_engineer_details(
    request: Request,
    engineer_id: int,
    db: Session = Depends(get_db)
):
    """
    Get detailed profile of an engineer.
    """
    engineer = db.query(Engineer).filter(Engineer.id == engineer_id).first()
    if not engineer:
        raise HTTPException(status_code=404, detail="Engineer not found")
        
    mix_count = db.query(TrackCredit).filter(TrackCredit.engineer_id == engineer_id).count()
    
    resp = EngineerResponse.model_validate(engineer)
    resp.mix_count = mix_count
    return resp
