"""
Background job scheduler for periodic spatial audio detection.

Uses APScheduler to run periodic jobs that check for new spatial audio releases.
Runs every 48 hours as recommended in the research.
"""
import json
import logging
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.orm import Session

from backend.apple_music_client import AppleMusicClient
from backend.database import SessionLocal
from backend.models import Engineer, RegionAvailability, Track, TrackCredit
from backend.schemas import RefreshResponse
from backend.utils.credits_scraper import CreditsScraper

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

    # Schedule silent upgrade check (Weekly)
    scheduler.add_job(
        func=scheduled_silent_upgrade_check,
        trigger=IntervalTrigger(days=7),
        id='silent_upgrade_check',
        name='Check for silent Dolby Atmos upgrades',
        replace_existing=True
    )

    # Schedule credits fetching (Slow drip: every 5 minutes process a batch)
    scheduler.add_job(
        func=scheduled_credits_fetch,
        trigger=IntervalTrigger(minutes=5),
        id='credits_fetch',
        name='Fetch deep metadata credits',
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


def scheduled_silent_upgrade_check():
    """
    Weekly job to check for silent upgrades (tracks becoming Atmos later).
    """
    logger.info("Starting silent upgrade check...")
    db = SessionLocal()
    try:
        # Find tracks that are NOT currently Atmos
        potential_upgrades = db.query(Track).filter(Track.format != "Dolby Atmos").all()
        logger.info(f"Checking {len(potential_upgrades)} tracks for silent upgrades")

        apple_client = AppleMusicClient()
        upgraded_count = 0

        for track in potential_upgrades:
            if not track.apple_music_id:
                continue

            try:
                # Re-fetch track info
                tracks = apple_client.get_catalog_tracks(storefront="us", ids=[track.apple_music_id])
                if not tracks:
                    continue

                track_data = tracks[0]
                spatial_info = apple_client.check_spatial_audio_support(track_data)

                if spatial_info["has_dolby_atmos"]:
                    logger.info(f"SILENT UPGRADE DETECTED: {track.title} by {track.artist}")
                    track.format = "Dolby Atmos"
                    track.atmos_release_date = datetime.now()
                    track.updated_at = datetime.now()
                    upgraded_count += 1
            except Exception as e:
                logger.error(f"Error checking upgrade for {track.title}: {e}")

        db.commit()
        logger.info(f"Silent upgrade check complete: {upgraded_count} tracks upgraded")

    except Exception as e:
        logger.error(f"Error during silent upgrade check: {e}")
    finally:
        db.close()


def scheduled_credits_fetch():
    """
    Background job to fetch credits for tracks.
    Runs frequently but processes few tracks to respect rate limits.
    """
    logger.info("Starting credits fetch job...")
    db = SessionLocal()
    scraper = CreditsScraper()

    try:
        # Find Atmos tracks that don't have credits yet
        # (This is a simplified check, ideally specific to 'has processed credits')
        # We can use a joining query or just check if credits relationship is empty
        # For efficiency, let's pick 5 random Atmos tracks without credits

        # Subquery to find tracks with credits
        # This might be slow on large DBs, but fine for now
        tracks_needing_credits = db.query(Track).outerjoin(TrackCredit).filter(
            Track.format == "Dolby Atmos",
            TrackCredit.id == None,
            Track.music_link != None
        ).limit(5).all()

        if not tracks_needing_credits:
            logger.debug("No tracks found needing credits")
            return

        logger.info(f"Fetching credits for {len(tracks_needing_credits)} tracks")

        for track in tracks_needing_credits:
            if not track.music_link:
                continue

            credits_data = scraper.fetch_credits(track.music_link)

            if credits_data:
                for credit in credits_data:
                    # Find or create Engineer
                    engineer = db.query(Engineer).filter(Engineer.name == credit['name']).first()
                    if not engineer:
                        engineer = Engineer(
                            name=credit['name'],
                            slug=credit['slug']
                        )
                        db.add(engineer)
                        db.flush() # get ID

                    # Create Credit linking
                    existing_credit = db.query(TrackCredit).filter(
                        TrackCredit.track_id == track.id,
                        TrackCredit.engineer_id == engineer.id,
                        TrackCredit.role == credit['role']
                    ).first()

                    if not existing_credit:
                        new_credit = TrackCredit(
                            track_id=track.id,
                            engineer_id=engineer.id,
                            role=credit['role']
                        )
                        db.add(new_credit)

                logger.info(f"Added {len(credits_data)} credits for {track.title}")

            # Commit per track to save progress
            db.commit()

    except Exception as e:
        logger.error(f"Error during credits fetch job: {e}")
        db.rollback()
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


def sync_spatial_audio_tracks(db: Session, comprehensive: bool = True) -> dict:
    """
    Sync spatial audio tracks from Apple Music API to database.

    Args:
        db: Database session
        comprehensive: If True, use all discovery sources (playlists, charts, albums, search).
                      If False, only scan curated Spatial Audio playlists.

    Returns:
        Dictionary with sync statistics
    """
    tracks_added = 0
    tracks_updated = 0

    # Initialize Apple Music client
    apple_client = AppleMusicClient()

    # Discover spatial audio tracks from Apple Music
    if comprehensive:
        logger.info("Starting COMPREHENSIVE spatial audio discovery (all sources)...")
        discovered_tracks = apple_client.discover_all_spatial_audio_tracks()
    else:
        logger.info("Discovering spatial audio tracks from curated playlists only...")
        discovered_tracks = apple_client.discover_spatial_audio_tracks()

    # Process each discovered track
    for track_data in discovered_tracks:
        try:
            # Check if track already exists by Apple Music ID
            track = db.query(Track).filter(
                Track.apple_music_id == track_data["apple_music_id"]
            ).first()

            if track:
                # Update existing track
                track.title = track_data["title"]
                track.artist = track_data["artist"]
                track.album = track_data["album"]
                track.format = track_data["format"]
                track.release_date = track_data["release_date"]
                track.atmos_release_date = track_data.get("atmos_release_date")
                track.music_link = track_data.get("music_link")
                track.extra_metadata = json.dumps(track_data.get("metadata", {}))
                track.updated_at = datetime.now()
                tracks_updated += 1
                logger.debug(f"Updated track: {track_data['title']} by {track_data['artist']}")
            else:
                # Add new track
                track = Track(
                    title=track_data["title"],
                    artist=track_data["artist"],
                    album=track_data["album"],
                    format=track_data["format"],
                    platform=track_data["platform"],
                    release_date=track_data["release_date"],
                    atmos_release_date=track_data.get("atmos_release_date"),
                    album_art=track_data.get("album_art", "🎵"),
                    music_link=track_data.get("music_link"),
                    apple_music_id=track_data.get("apple_music_id"),
                    extra_metadata=json.dumps(track_data.get("metadata", {})),
                    discovered_at=datetime.now()
                )
                db.add(track)
                tracks_added += 1
                logger.debug(f"Added new track: {track_data['title']} by {track_data['artist']}")

            # Flush to get track ID for new tracks
            db.flush()

            # Process region availability if present
            if "region_availability" in track_data:
                # Clear existing availability
                db.query(RegionAvailability).filter(
                    RegionAvailability.track_id == track.id
                ).delete()

                # Add new availability records
                for region_data in track_data["region_availability"]:
                    avail = RegionAvailability(
                        track_id=track.id,
                        storefront=region_data["storefront"],
                        is_available=region_data["is_available"],
                        format=region_data["format"]
                    )
                    db.add(avail)

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
