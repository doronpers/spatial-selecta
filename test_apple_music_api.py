#!/usr/bin/env python3
"""
Apple Music API Connection Test

Quick test to verify your Apple Music developer token works
and can fetch spatial audio data.

Usage:
    python test_apple_music_api.py

Requires:
    - .env file with APPLE_MUSIC_DEVELOPER_TOKEN set
    - pip install requests python-dotenv
"""

import os
import sys
import json

try:
    import requests
    from dotenv import load_dotenv
except ImportError:
    print("Missing dependencies. Run:")
    print("  pip install requests python-dotenv")
    sys.exit(1)

# Load environment
load_dotenv()

BASE_URL = "https://api.music.apple.com/v1"

# Test playlists (verified December 2024)
TEST_PLAYLISTS = [
    ("pl.ba2404fbc4464b8ba2d60399189cf24e", "Hits in Spatial Audio"),
    ("pl.cc74a5aec23942da9cf083c6c4344aee", "Pop in Spatial Audio"),
    ("pl.efbd24628ff04ff3b5e416a6e237d753", "Jazz in Spatial Audio"),
]


def test_token():
    """Test if the token is configured."""
    token = os.getenv("APPLE_MUSIC_DEVELOPER_TOKEN")
    
    if not token:
        print("❌ APPLE_MUSIC_DEVELOPER_TOKEN not found in environment")
        print("   Make sure your .env file exists and contains the token")
        return None
    
    if len(token) < 100:
        print(f"⚠️  Token seems short ({len(token)} chars) - JWT tokens are usually 300+ chars")
    else:
        print(f"✓ Token found ({len(token)} characters)")
    
    return token


def test_api_connection(token):
    """Test basic API connectivity."""
    headers = {
        "Authorization": f"Bearer {token}",
    }
    
    # Try to fetch a known playlist
    url = f"{BASE_URL}/catalog/us/playlists/pl.ba2404fbc4464b8ba2d60399189cf24e"
    
    print("\nTesting API connection...")
    
    try:
        response = requests.get(url, headers=headers, params={"limit": 1}, timeout=10)
        
        if response.status_code == 200:
            print("✓ API connection successful")
            return True
        elif response.status_code == 401:
            print("❌ Authentication failed (401)")
            print("   Your token may be expired or invalid")
            print("   Tokens expire after 180 days")
            return False
        elif response.status_code == 403:
            print("❌ Access forbidden (403)")
            print("   Your MusicKit key may not have proper permissions")
            return False
        else:
            print(f"❌ Unexpected response: {response.status_code}")
            print(f"   {response.text[:200]}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
        return False


def test_playlist_fetch(token):
    """Test fetching tracks from spatial audio playlists."""
    headers = {
        "Authorization": f"Bearer {token}",
    }
    
    print("\nTesting playlist access...")
    
    results = []
    
    for playlist_id, playlist_name in TEST_PLAYLISTS:
        url = f"{BASE_URL}/catalog/us/playlists/{playlist_id}"
        params = {
            "include": "tracks",
            "extend": "audioVariants",
            "limit[tracks]": 5  # Just get a few for testing
        }
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                # Count tracks
                tracks = []
                if "data" in data and len(data["data"]) > 0:
                    playlist_data = data["data"][0]
                    if "relationships" in playlist_data and "tracks" in playlist_data["relationships"]:
                        tracks = playlist_data["relationships"]["tracks"].get("data", [])
                
                # Check for spatial audio
                spatial_count = 0
                for track in tracks:
                    attrs = track.get("attributes", {})
                    variants = attrs.get("audioVariants", [])
                    if any("atmos" in v.lower() for v in variants):
                        spatial_count += 1
                
                print(f"  ✓ {playlist_name}: {len(tracks)} tracks fetched, {spatial_count} with Atmos")
                results.append((playlist_name, len(tracks), spatial_count))
            else:
                print(f"  ❌ {playlist_name}: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ {playlist_name}: {e}")
    
    return results


def test_track_details(token):
    """Fetch a single track and show its spatial audio metadata."""
    headers = {
        "Authorization": f"Bearer {token}",
    }
    
    print("\nFetching sample track details...")
    
    # First, get a track from a playlist
    url = f"{BASE_URL}/catalog/us/playlists/pl.ba2404fbc4464b8ba2d60399189cf24e"
    params = {
        "include": "tracks",
        "extend": "audioVariants",
        "limit[tracks]": 1
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            
            if "data" in data and len(data["data"]) > 0:
                tracks = data["data"][0].get("relationships", {}).get("tracks", {}).get("data", [])
                
                if tracks:
                    track = tracks[0]
                    attrs = track.get("attributes", {})
                    
                    print(f"\n  Sample Track:")
                    print(f"    Title:    {attrs.get('name', 'Unknown')}")
                    print(f"    Artist:   {attrs.get('artistName', 'Unknown')}")
                    print(f"    Album:    {attrs.get('albumName', 'Unknown')}")
                    print(f"    Released: {attrs.get('releaseDate', 'Unknown')}")
                    print(f"    Genres:   {', '.join(attrs.get('genreNames', []))}")
                    
                    variants = attrs.get("audioVariants", [])
                    if variants:
                        print(f"    Audio:    {', '.join(variants)}")
                        if any("atmos" in v.lower() for v in variants):
                            print("    ✓ Dolby Atmos CONFIRMED")
                    else:
                        print("    Audio:    (no variants listed)")
                    
                    return True
                    
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    return False


def main():
    print("=" * 60)
    print("Apple Music API Connection Test")
    print("=" * 60)
    print()
    
    # Test 1: Token exists
    token = test_token()
    if not token:
        sys.exit(1)
    
    # Test 2: API connection
    if not test_api_connection(token):
        print("\n⛔ API connection failed. Check your token.")
        sys.exit(1)
    
    # Test 3: Playlist access
    results = test_playlist_fetch(token)
    
    # Test 4: Track details
    test_track_details(token)
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    total_tracks = sum(r[1] for r in results)
    total_spatial = sum(r[2] for r in results)
    
    if total_tracks > 0:
        print(f"✓ API connection: Working")
        print(f"✓ Playlists accessible: {len(results)}/{len(TEST_PLAYLISTS)}")
        print(f"✓ Sample tracks fetched: {total_tracks}")
        print(f"✓ Dolby Atmos tracks: {total_spatial}")
        print()
        print("🚀 Ready to deploy to Render!")
        print()
        print("Next step: Follow RENDER_DEPLOYMENT_CHECKLIST.md")
    else:
        print("⚠️  Connected but no tracks fetched")
        print("   Playlists may have changed or API response format differs")


if __name__ == "__main__":
    main()
