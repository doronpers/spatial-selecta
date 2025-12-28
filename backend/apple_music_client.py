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

from backend.utils.apple_music import get_apple_music_token

load_dotenv()

logger = logging.getLogger(__name__)


class AppleMusicClient:
    """
    Client for interacting with Apple Music API to detect spatial audio content.
    """
    
    BASE_URL = "https://api.music.apple.com/v1"
    
    # VERIFIED Apple Music Spatial Audio Playlists (December 2024)
    # These are real, active playlists curated by Apple
    SPATIAL_AUDIO_PLAYLISTS = [
        # Main curated playlists
        "pl.ba2404fbc4464b8ba2d60399189cf24e",  # Hits in Spatial Audio (US)
        "pl.cc74a5aec23942da9cf083c6c4344aee",  # Pop in Spatial Audio
        "pl.a82d7ac0ee854d8b8a95708c76210023",  # Rock in Spatial Audio
        "pl.3e9b112e3ffe4287b9fb785251545246",  # Hard Rock in Spatial Audio
        "pl.9ca5521e31c8408c97377a71030396d1",  # Electronic in Spatial Audio
        "pl.a0c765aa555e457c9666b2a201de5506",  # Hip-Hop in Spatial Audio
        "pl.efbd24628ff04ff3b5e416a6e237d753",  # Jazz in Spatial Audio
        "pl.ffea4bbea2d141cbb0ec67e32059b278",  # Classical in Spatial Audio
        "pl.924f9f9df2294b9c97f5e40d8862f7e7",  # Country in Spatial Audio
        # Regional/Genre specific
        "pl.4d2dbe3d55064021870291c2eb29bc72",  # K-Pop in Spatial Audio
        "pl.04a2d5c0ba2c4afa917241f1e22fa535",  # J-Pop in Spatial Audio
        "pl.7cdf5c34b7c84bf0b0ff3f9188528439",  # C-Pop in Spatial Audio
        "pl.c6287a0994a841e387f7f015948718f3",  # Ambient in Dolby Atmos
    ]
    
    def __init__(self):
        """Initialize Apple Music client with API credentials."""
        self.developer_token = os.getenv("APPLE_MUSIC_DEVELOPER_TOKEN")
        
        # Try to generate token if not in environment
        if not self.developer_token:
            try:
                self.developer_token = get_apple_music_token()
                logger.info("Generated Apple Music Developer Token dynamically")
            except Exception as e:
                logger.warning(f"Could not generate Apple Music token: {e}")
        
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
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
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
    
    def get_playlist_tracks(self, playlist_id: str, storefront: str = "us", 
                           limit: int = 100, offset: int = 0) -> Optional[List[Dict]]:
        """
        Get tracks from a specific playlist with pagination support.
        
        Args:
            playlist_id: Apple Music playlist ID
            storefront: Apple Music storefront (country code)
            limit: Maximum tracks to return (max 100)
            offset: Number of tracks to skip
            
        Returns:
            List of tracks in the playlist
        """
        endpoint = f"catalog/{storefront}/playlists/{playlist_id}"
        params = {
            "extend": "audioVariants",
            "include": "tracks",
            "limit[tracks]": min(limit, 100),
            "offset[tracks]": offset
        }
        
        response = self._make_request(endpoint, params)
        
        if response and "data" in response:
            data = response["data"][0]
            if "relationships" in data and "tracks" in data["relationships"]:
                tracks = data["relationships"]["tracks"]["data"]
                
                # Check for pagination - get next page if available
                next_url = data["relationships"]["tracks"].get("next")
                if next_url and len(tracks) >= limit:
                    # Recursively get more tracks
                    more_tracks = self.get_playlist_tracks(
                        playlist_id, storefront, limit, offset + limit
                    )
                    if more_tracks:
                        tracks.extend(more_tracks)
                
                return tracks
        
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
            
            # Check for Dolby Atmos in variants (handle both list and dict formats)
            if isinstance(audio_variants, list):
                for variant in audio_variants:
                    variant_str = str(variant).lower()
                    if "atmos" in variant_str or "dolby" in variant_str:
                        result["has_dolby_atmos"] = True
                        result["has_spatial_audio"] = True
                        break
            elif isinstance(audio_variants, dict):
                for variant in audio_variants.values():
                    variant_str = str(variant).lower()
                    if "atmos" in variant_str or "dolby" in variant_str:
                        result["has_dolby_atmos"] = True
                        result["has_spatial_audio"] = True
                        break
        
        # Fallback: Check audioTraits (older method)
        if not result["has_spatial_audio"] and "audioTraits" in attributes:
            audio_traits = attributes["audioTraits"]
            if isinstance(audio_traits, list):
                for trait in audio_traits:
                    trait_str = str(trait).lower()
                    if "spatial" in trait_str or "atmos" in trait_str:
                        result["has_spatial_audio"] = True
                        result["has_dolby_atmos"] = True
                        break
            elif isinstance(audio_traits, str):
                if "spatial" in audio_traits.lower() or "atmos" in audio_traits.lower():
                    result["has_spatial_audio"] = True
                    result["has_dolby_atmos"] = True
        
        return result
    
    def discover_spatial_audio_tracks(self, storefront: str = "us", 
                                      max_playlists: int = None) -> List[Dict]:
        """
        Discover new spatial audio tracks by monitoring curated playlists.
        
        Args:
            storefront: Apple Music storefront (country code)
            max_playlists: Maximum number of playlists to scan (None = all)
            
        Returns:
            List of spatial audio tracks discovered
        """
        discovered_tracks = []
        seen_ids = set()
        
        playlists_to_scan = self.SPATIAL_AUDIO_PLAYLISTS
        if max_playlists:
            playlists_to_scan = playlists_to_scan[:max_playlists]
        
        logger.info(f"Discovering spatial audio tracks from {len(playlists_to_scan)} playlists")
        
        for playlist_id in playlists_to_scan:
            try:
                tracks = self.get_playlist_tracks(playlist_id, storefront)
                
                if not tracks:
                    logger.warning(f"No tracks found in playlist {playlist_id}")
                    continue
                
                playlist_added = 0
                for track in tracks:
                    # Skip duplicates
                    track_id = track.get("id")
                    if track_id in seen_ids:
                        continue
                    seen_ids.add(track_id)
                    
                    spatial_info = self.check_spatial_audio_support(track)
                    
                    if spatial_info["has_spatial_audio"]:
                        track_info = self._extract_track_info(track, spatial_info)
                        discovered_tracks.append(track_info)
                        playlist_added += 1
                
                logger.info(f"Playlist {playlist_id}: {len(tracks)} tracks, {playlist_added} new spatial audio")
                
            except Exception as e:
                logger.error(f"Error processing playlist {playlist_id}: {e}")
        
        logger.info(f"Discovered {len(discovered_tracks)} unique spatial audio tracks total")
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
        
        # Get album artwork URL for potential future use
        artwork = attributes.get("artwork", {})
        artwork_url = None
        if artwork:
            url_template = artwork.get("url", "")
            if url_template:
                artwork_url = url_template.replace("{w}", "300").replace("{h}", "300")
        
        # Get the music URL from the API (this is the direct Apple Music link)
        music_link = attributes.get("url")
        
        # Parse release dates
        release_date = self._parse_release_date(attributes.get("releaseDate"))
        
        # For atmos_release_date, use the release date if the track has Atmos
        # NOTE: This assumes tracks are released with Atmos from day one.
        # For catalog releases where Atmos was added later, this will be inaccurate.
        # Future enhancement: Track when Atmos was specifically added vs original release.
        # For now, manual correction in data.json is recommended for older catalog releases.
        atmos_release_date = release_date if spatial_info["has_dolby_atmos"] else None
        
        return {
            "apple_music_id": track_data.get("id"),
            "title": attributes.get("name", "Unknown"),
            "artist": attributes.get("artistName", "Unknown"),
            "album": attributes.get("albumName", "Unknown"),
            "format": "Dolby Atmos" if spatial_info["has_dolby_atmos"] else "Spatial Audio",
            "platform": "Apple Music",
            "release_date": release_date,
            "atmos_release_date": atmos_release_date,
            "album_art": self._get_album_art_emoji(attributes.get("genreNames", [])),
            "music_link": music_link,
            "metadata": {
                "genre": attributes.get("genreNames", []),
                "duration_ms": attributes.get("durationInMillis"),
                "isrc": attributes.get("isrc"),
                "audio_variants": spatial_info["audio_variants"],
                "artwork_url": artwork_url,
                "composer": attributes.get("composerName"),
                "track_number": attributes.get("trackNumber"),
                "disc_number": attributes.get("discNumber"),
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
            # Handle YYYY-MM-DD format
            if len(date_string) == 10:
                return datetime.strptime(date_string, "%Y-%m-%d")
            # Handle ISO format with timezone
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
            "Hip-Hop": "🎤",
            "Rap": "🎤",
            "Jazz": "🎷",
            "Classical": "🎻",
            "Electronic": "🎹",
            "Dance": "💃",
            "Country": "🤠",
            "R&B/Soul": "💿",
            "R&B": "💿",
            "Soul": "💿",
            "Metal": "🤘",
            "Alternative": "🎧",
            "Indie": "🎧",
            "Latin": "💃",
            "Reggae": "🌴",
            "Blues": "🎺",
            "Folk": "🪕",
            "Soundtrack": "🎬",
            "K-Pop": "⭐",
            "J-Pop": "🌸",
            "Ambient": "🌌",
        }
        
        for genre in genres:
            # Check exact match first
            if genre in genre_emojis:
                return genre_emojis[genre]
            # Check partial match
            for key, emoji in genre_emojis.items():
                if key.lower() in genre.lower():
                    return emoji
        
        return "🎵"  # Default emoji
    
    def test_connection(self) -> bool:
        """
        Test the API connection with a simple request.
        
        Returns:
            True if connection successful, False otherwise
        """
        if not self.developer_token:
            logger.error("No developer token configured")
            return False
        
        # Try to fetch a known playlist
        try:
            endpoint = "catalog/us/playlists/pl.ba2404fbc4464b8ba2d60399189cf24e"
            response = self._make_request(endpoint, {"limit": 1})
            if response and "data" in response:
                logger.info("Apple Music API connection successful")
                return True
        except Exception as e:
            logger.error(f"API connection test failed: {e}")
        
        return False
