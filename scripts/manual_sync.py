#!/usr/bin/env python3
"""
Script to manually trigger spatial audio sync.
Bypasses the scheduler and runs the sync logic immediately.
"""
import logging
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from backend.database import SessionLocal
from backend.scheduler import sync_spatial_audio_tracks

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    print("Starting manual synchronization...")
    print("This may take a minute or two depending on network speed.")

    db = SessionLocal()
    try:
        # Run the sync
        result = sync_spatial_audio_tracks(db, comprehensive=True)

        print("\n" + "="*50)
        print("SYNC COMPLETE")
        print(f"Tracks Added:   {result['tracks_added']}")
        print(f"Tracks Updated: {result['tracks_updated']}")
        print("="*50 + "\n")

    except Exception as e:
        print(f"\nERROR: Sync failed: {e}")
        logger.error("Sync failed", exc_info=True)
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    main()
