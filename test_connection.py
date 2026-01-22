import logging
import sys

from backend.apple_music_client import AppleMusicClient

# Configure logging to stdout so we see the output
logging.basicConfig(level=logging.INFO)

def test():
    print("Testing Apple Music API connection...")
    client = AppleMusicClient()
    success = client.test_connection()
    if success:
        print("SUCCESS: Connection established.")
        sys.exit(0)
    else:
        print("FAILURE: Could not connect to Apple Music API.")
        sys.exit(1)

if __name__ == "__main__":
    test()
