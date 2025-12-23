"""
Apple Music API client for detecting spatial audio tracks.

This client uses Apple Music API's audioVariants extended attribute (available since WWDC 2022)
to query whether tracks/albums support Spatial Audio (Dolby Atmos).

Reference: https://developer.apple.com/documentation/applemusicapi
"""
import os
import requests
import logging
from typing import List, Dict, Optional
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class AppleMusicClient:
    """
    Client for interacting with Apple Music API to detect spatial audio content.
    """
    
    BASE_URL = "https://api.music.apple.com/v1"
    
    # Curated Apple Spatial Audio playlists to monitor
    SPATIAL_AUDIO_PLAYLISTS = [
        "pl.567c7ad7094d4c6e9b687d5fd058e689",  # Made for Spatial Audio
        "pl.4a3d8e6e5f3f4a6dbe5e3e6c5d5e5e5e",  # Hits in Spatial Audio
        "pl.jazz-spatial-audio",  # Jazz in Spatial Audio
        # Add more playlist IDs as discovered
    ]
    
    def __init__(self):
        """Initialize Apple Music client with API credentials."""
        self.developer_token = os.getenv("APPLE_MUSIC_DEVELOPER_TOKEN")
        self.music_user_token = os.getenv("APPLE_MUSIC_USER_TOKEN", "")
        
        if not self.developer_token:
            logger.warning("Apple Music Developer Token not configured. API calls will fail.")
        
        self.headers = {
            "Authorization": f"Bearer {self.developer_token}",
            "Music-User-Token": self.music_user_token
        }
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """
        Make a request to Apple Music API.
        
        Args:
            endpoint: API endpoint (relative to BASE_URL)
            params: Query parameters
            
        Returns:
            JSON response or None if request fails
        """
        if not self.developer_token:
            logger.error("Cannot make API request: Developer token not configured")
            return None
        
        url = f"{self.BASE_URL}/{endpoint}"
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Apple Music API request failed: {e}")
            return None
    
    def get_catalog_tracks(self, storefront: str = "us", ids: List[str] = None, 
                          include_audio_variants: bool = True) -> Optional[List[Dict]]:
        """
        Get catalog tracks with audio variants information.
        
        Args:
            storefront: Apple Music storefront (country code)
            ids: List of track IDs to query
            include_audio_variants: Whether to include audioVariants in response
            
        Returns:
            List of track data with spatial audio information
        """
        if not ids:
            return []
        
        endpoint = f"catalog/{storefront}/songs"
        params = {
            "ids": ",".join(ids)
        }
        
        if include_audio_variants:
            params["extend"] = "audioVariants"
        
        response = self._make_request(endpoint, params)
        
        if response and "data" in response:
            return response["data"]
        
        return []
    
    def get_playlist_tracks(self, playlist_id: str, storefront: str = "us") -> Optional[List[Dict]]:
        """
        Get tracks from a specific playlist.
        
        Args:
            playlist_id: Apple Music playlist ID
            storefront: Apple Music storefront (country code)
            
        Returns:
            List of tracks in the playlist
        """
        endpoint = f"catalog/{storefront}/playlists/{playlist_id}"
        params = {
            "extend": "audioVariants",
            "include": "tracks"
        }
        
        response = self._make_request(endpoint, params)
        
        if response and "data" in response:
            data = response["data"][0]
            if "relationships" in data and "tracks" in data["relationships"]:
                return data["relationships"]["tracks"]["data"]
        
        return []
    
    def check_spatial_audio_support(self, track_data: Dict) -> Dict:
        """
        Check if a track supports spatial audio from its API data.
        
        Args:
            track_data: Track data from Apple Music API
            
        Returns:
            Dictionary with spatial audio information
        """
        result = {
            "has_spatial_audio": False,
            "has_dolby_atmos": False,
            "audio_variants": []
        }
        
        if "attributes" not in track_data:
            return result
        
        attributes = track_data["attributes"]
        
        # Check audioVariants field (most reliable method)
        if "audioVariants" in attributes:
            audio_variants = attributes["audioVariants"]
            result["audio_variants"] = audio_variants
            
            # Check for Dolby Atmos in variants
            if "dolby-atmos" in audio_variants or "atmos" in audio_variants:
                result["has_dolby_atmos"] = True
                result["has_spatial_audio"] = True
        
        # Fallback: Check audioTraits (older method)
        if "audioTraits" in attributes:
            audio_traits = attributes["audioTraits"]
            if "spatial" in audio_traits or "atmos" in audio_traits:
                result["has_spatial_audio"] = True
                result["has_dolby_atmos"] = True
        
        return result
    
    def discover_spatial_audio_tracks(self, storefront: str = "us") -> List[Dict]:
        """
        Discover new spatial audio tracks by monitoring curated playlists.
        
        Args:
            storefront: Apple Music storefront (country code)
            
        Returns:
            List of spatial audio tracks discovered
        """
        discovered_tracks = []
        
        logger.info(f"Discovering spatial audio tracks from {len(self.SPATIAL_AUDIO_PLAYLISTS)} playlists")
        
        for playlist_id in self.SPATIAL_AUDIO_PLAYLISTS:
            try:
                tracks = self.get_playlist_tracks(playlist_id, storefront)
                
                if not tracks:
                    logger.warning(f"No tracks found in playlist {playlist_id}")
                    continue
                
                for track in tracks:
                    spatial_info = self.check_spatial_audio_support(track)
                    
                    if spatial_info["has_spatial_audio"]:
                        track_info = self._extract_track_info(track, spatial_info)
                        discovered_tracks.append(track_info)
                
                logger.info(f"Found {len(tracks)} tracks in playlist {playlist_id}")
                
            except Exception as e:
                logger.error(f"Error processing playlist {playlist_id}: {e}")
        
        logger.info(f"Discovered {len(discovered_tracks)} spatial audio tracks total")
        return discovered_tracks
    
    def _extract_track_info(self, track_data: Dict, spatial_info: Dict) -> Dict:
        """
        Extract relevant track information for storage.
        
        Args:
            track_data: Raw track data from Apple Music API
            spatial_info: Spatial audio information
            
        Returns:
            Formatted track information
        """
        attributes = track_data.get("attributes", {})
        
        return {
            "apple_music_id": track_data.get("id"),
            "title": attributes.get("name", "Unknown"),
            "artist": attributes.get("artistName", "Unknown"),
            "album": attributes.get("albumName", "Unknown"),
            "format": "Dolby Atmos" if spatial_info["has_dolby_atmos"] else "Spatial Audio",
            "platform": "Apple Music",
            "release_date": self._parse_release_date(attributes.get("releaseDate")),
            "album_art": self._get_album_art_emoji(attributes.get("genreNames", [])),
            "metadata": {
                "genre": attributes.get("genreNames", []),
                "duration_ms": attributes.get("durationInMillis"),
                "isrc": attributes.get("isrc"),
                "audio_variants": spatial_info["audio_variants"]
            }
        }
    
    def _parse_release_date(self, date_string: Optional[str]) -> datetime:
        """
        Parse release date string to datetime.
        
        Args:
            date_string: Date string from Apple Music API
            
        Returns:
            Datetime object
        """
        if not date_string:
            return datetime.now()
        
        try:
            return datetime.fromisoformat(date_string.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            return datetime.now()
    
    def _get_album_art_emoji(self, genres: List[str]) -> str:
        """
        Get an emoji representation for album art based on genre.
        
        Args:
            genres: List of genre names
            
        Returns:
            Emoji string
        """
        genre_emojis = {
            "Pop": "🎵",
            "Rock": "🎸",
            "Hip-Hop/Rap": "🎤",
            "Jazz": "🎷",
            "Classical": "🎻",
            "Electronic": "🎹",
            "Country": "🤠",
            "R&B/Soul": "💿",
            "Metal": "🤘",
            "Dance": "💃"
        }
        
        for genre in genres:
            if genre in genre_emojis:
                return genre_emojis[genre]
        
        return "🎵"  # Default emoji
