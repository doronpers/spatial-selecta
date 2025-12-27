"""
Background job scheduler for periodic spatial audio detection.

Uses APScheduler to run periodic jobs that check for new spatial audio releases.
Runs every 48 hours as recommended in the research.
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.orm import Session
from datetime import datetime
import logging
import json

from backend.database import SessionLocal
from backend.models import Track
from backend.apple_music_client import AppleMusicClient
from backend.schemas import RefreshResponse

logger = logging.getLogger(__name__)

# Global scheduler instance
scheduler = None


def start_scheduler():
    """
    Start the background scheduler for periodic spatial audio detection.
    """
    global scheduler
    
    if scheduler is not None:
        logger.warning("Scheduler already running")
        return
    
    scheduler = BackgroundScheduler()
    
    # Schedule spatial audio detection every 48 hours
    scheduler.add_job(
        func=scheduled_spatial_audio_scan,
        trigger=IntervalTrigger(hours=48),
        id='spatial_audio_scan',
        name='Scan for new spatial audio releases',
        replace_existing=True
    )
    
    # Start the scheduler
    scheduler.start()
    logger.info("Background scheduler started - scanning every 48 hours")


def stop_scheduler():
    """Stop the background scheduler."""
    global scheduler
    
    if scheduler is not None:
        scheduler.shutdown()
        scheduler = None
        logger.info("Background scheduler stopped")


def scheduled_spatial_audio_scan():
    """
    Scheduled job to scan for new spatial audio releases.
    This runs every 48 hours automatically.
    """
    logger.info("Starting scheduled spatial audio scan...")
    
    db = SessionLocal()
    try:
        result = sync_spatial_audio_tracks(db)
        logger.info(f"Scheduled scan complete: {result['tracks_added']} added, {result['tracks_updated']} updated")
    except Exception as e:
        logger.error(f"Error during scheduled scan: {e}", exc_info=True)
        # Don't raise - allow scheduler to continue running
    finally:
        db.close()


async def trigger_manual_refresh(db: Session) -> RefreshResponse:
    """
    Manually trigger a refresh of spatial audio data.
    
    Args:
        db: Database session
        
    Returns:
        Refresh response with statistics
    """
    logger.info("Manual refresh triggered")
    result = sync_spatial_audio_tracks(db)
    
    return RefreshResponse(
        status="success",
        message=f"Refresh completed: {result['tracks_added']} tracks added, {result['tracks_updated']} updated",
        tracks_added=result['tracks_added'],
        tracks_updated=result['tracks_updated'],
        timestamp=datetime.now()
    )


def sync_spatial_audio_tracks(db: Session) -> dict:
    """
    Sync spatial audio tracks from Apple Music API to database.
    
    Args:
        db: Database session
        
    Returns:
        Dictionary with sync statistics
    """
    tracks_added = 0
    tracks_updated = 0
    
    # Initialize Apple Music client
    apple_client = AppleMusicClient()
    
    # Discover spatial audio tracks from Apple Music
    logger.info("Discovering spatial audio tracks from Apple Music...")
    discovered_tracks = apple_client.discover_spatial_audio_tracks()
    
    # Process each discovered track
    for track_data in discovered_tracks:
        try:
            # Check if track already exists by Apple Music ID
            existing_track = db.query(Track).filter(
                Track.apple_music_id == track_data["apple_music_id"]
            ).first()
            
            if existing_track:
                # Update existing track
                existing_track.title = track_data["title"]
                existing_track.artist = track_data["artist"]
                existing_track.album = track_data["album"]
                existing_track.format = track_data["format"]
                existing_track.release_date = track_data["release_date"]
                existing_track.extra_metadata = json.dumps(track_data.get("metadata", {}))
                existing_track.updated_at = datetime.now()
                tracks_updated += 1
                logger.debug(f"Updated track: {track_data['title']} by {track_data['artist']}")
            else:
                # Add new track
                new_track = Track(
                    title=track_data["title"],
                    artist=track_data["artist"],
                    album=track_data["album"],
                    format=track_data["format"],
                    platform=track_data["platform"],
                    release_date=track_data["release_date"],
                    album_art=track_data.get("album_art", "🎵"),
                    apple_music_id=track_data.get("apple_music_id"),
                    extra_metadata=json.dumps(track_data.get("metadata", {})),
                    discovered_at=datetime.now()
                )
                db.add(new_track)
                tracks_added += 1
                logger.debug(f"Added new track: {track_data['title']} by {track_data['artist']}")
        
        except Exception as e:
            logger.error(f"Error processing track {track_data.get('title', 'Unknown')}: {e}")
            continue
    
    # Commit all changes
    try:
        db.commit()
        logger.info(f"Database sync complete: {tracks_added} added, {tracks_updated} updated")
    except Exception as e:
        db.rollback()
        logger.error(f"Error committing changes to database: {e}")
        raise
    
    return {
        "tracks_added": tracks_added,
        "tracks_updated": tracks_updated
    }


def import_existing_data_json(db: Session, data_json_path: str = "data.json"):
    """
    Import existing tracks from data.json into the database.
    This is a one-time migration function.
    
    Args:
        db: Database session
        data_json_path: Path to data.json file
    """
    import json
    
    try:
        with open(data_json_path, 'r') as f:
            tracks_data = json.load(f)
        
        for track_data in tracks_data:
            # Check if track already exists by title and artist
            existing_track = db.query(Track).filter(
                Track.title == track_data["title"],
                Track.artist == track_data["artist"]
            ).first()
            
            if not existing_track:
                new_track = Track(
                    title=track_data["title"],
                    artist=track_data["artist"],
                    album=track_data["album"],
                    format=track_data["format"],
                    platform=track_data["platform"],
                    release_date=datetime.fromisoformat(track_data["releaseDate"]),
                    album_art=track_data.get("albumArt", "🎵"),
                    discovered_at=datetime.now()
                )
                db.add(new_track)
        
        db.commit()
        logger.info(f"Imported {len(tracks_data)} tracks from data.json")
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error importing data.json: {e}")
        raise
