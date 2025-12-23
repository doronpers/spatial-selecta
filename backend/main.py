"""
Main FastAPI application for Spatial Selecta.
Provides API endpoints for spatial audio track management and automatic detection.
"""
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import logging

from backend.database import get_db, init_db
from backend.models import Track
from backend.schemas import TrackResponse, TrackCreate, RefreshResponse
from backend.apple_music_client import AppleMusicClient
from backend.scheduler import start_scheduler, trigger_manual_refresh

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Spatial Selecta API",
    description="API for tracking spatial audio releases from Apple Music and Amazon Music",
    version="1.0.0"
)

# Configure CORS to allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize database and start background scheduler on app startup."""
    logger.info("Starting Spatial Selecta API...")
    init_db()
    start_scheduler()
    logger.info("Application started successfully")


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
    platform: Optional[str] = None,
    format: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    Get all spatial audio tracks with optional filtering.
    
    Args:
        platform: Filter by platform (Apple Music, Amazon Music)
        format: Filter by audio format (Dolby Atmos, 360 Reality Audio)
        limit: Maximum number of tracks to return
        offset: Number of tracks to skip
        db: Database session
    
    Returns:
        List of tracks matching the filters
    """
    query = db.query(Track)
    
    if platform:
        query = query.filter(Track.platform == platform)
    if format:
        query = query.filter(Track.format == format)
    
    # Order by release date descending (newest first)
    query = query.order_by(Track.release_date.desc())
    
    tracks = query.offset(offset).limit(limit).all()
    return tracks


@app.get("/api/tracks/new", response_model=List[TrackResponse])
async def get_new_tracks(
    days: int = 30,
    db: Session = Depends(get_db)
):
    """
    Get tracks released within the specified number of days.
    
    Args:
        days: Number of days to look back (default: 30)
        db: Database session
    
    Returns:
        List of recently released tracks
    """
    cutoff_date = datetime.now() - timedelta(days=days)
    tracks = db.query(Track).filter(
        Track.release_date >= cutoff_date
    ).order_by(Track.release_date.desc()).all()
    
    return tracks


@app.get("/api/tracks/{track_id}", response_model=TrackResponse)
async def get_track(track_id: int, db: Session = Depends(get_db)):
    """
    Get a specific track by ID.
    
    Args:
        track_id: Track ID
        db: Database session
    
    Returns:
        Track details
    """
    track = db.query(Track).filter(Track.id == track_id).first()
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")
    return track


@app.post("/api/refresh", response_model=RefreshResponse)
async def refresh_data(db: Session = Depends(get_db)):
    """
    Manually trigger a refresh of spatial audio data.
    
    Args:
        db: Database session
    
    Returns:
        Refresh status and statistics
    """
    try:
        result = await trigger_manual_refresh(db)
        return result
    except Exception as e:
        logger.error(f"Error during manual refresh: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/stats")
async def get_stats(db: Session = Depends(get_db)):
    """
    Get statistics about the spatial audio database.
    
    Args:
        db: Database session
    
    Returns:
        Statistics including total tracks, tracks by platform, etc.
    """
    total_tracks = db.query(Track).count()
    apple_music_tracks = db.query(Track).filter(Track.platform == "Apple Music").count()
    amazon_music_tracks = db.query(Track).filter(Track.platform == "Amazon Music").count()
    dolby_atmos_tracks = db.query(Track).filter(Track.format == "Dolby Atmos").count()
    
    cutoff_date = datetime.now() - timedelta(days=30)
    new_tracks = db.query(Track).filter(Track.release_date >= cutoff_date).count()
    
    return {
        "total_tracks": total_tracks,
        "by_platform": {
            "Apple Music": apple_music_tracks,
            "Amazon Music": amazon_music_tracks
        },
        "by_format": {
            "Dolby Atmos": dolby_atmos_tracks,
            "360 Reality Audio": total_tracks - dolby_atmos_tracks
        },
        "new_tracks_last_30_days": new_tracks
    }
