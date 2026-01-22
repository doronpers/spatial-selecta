"""
Pydantic schemas for API request/response validation.
"""
import re
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, validator


class TrackBase(BaseModel):
    """Base schema for track data."""
    title: str = Field(..., min_length=1, max_length=500, description="Track title")
    artist: str = Field(..., min_length=1, max_length=500, description="Artist name")
    album: str = Field(..., min_length=1, max_length=500, description="Album name")
    format: str = Field(..., min_length=1, max_length=100, description="Audio format")
    platform: str = Field(..., min_length=1, max_length=100, description="Platform name")
    release_date: datetime = Field(..., description="Release date")
    atmos_release_date: Optional[datetime] = Field(None, description="Atmos release date")
    album_art: Optional[str] = Field(None, max_length=10, description="Album art emoji or URL")
    music_link: Optional[str] = Field(None, max_length=500, description="Music link URL")

    @validator('title', 'artist', 'album')
    def validate_text_fields(cls, v):
        """Validate text fields don't contain dangerous characters."""
        if not v or not v.strip():
            raise ValueError("Field cannot be empty")
        # Remove null bytes and other control characters
        v = v.replace('\x00', '').strip()
        if len(v) == 0:
            raise ValueError("Field cannot be empty after sanitization")
        return v

    @validator('music_link')
    def validate_music_link(cls, v):
        """Validate music link is a safe URL."""
        if not v:
            return v
        # Only allow http/https URLs
        if not v.startswith(('http://', 'https://')):
            raise ValueError("Music link must be http:// or https:// URL")
        # Basic URL validation
        if len(v) > 500:
            raise ValueError("Music link too long")
        return v


class TrackCreate(TrackBase):
    """Schema for creating a new track."""
    apple_music_id: Optional[str] = Field(None, max_length=200, description="Apple Music track ID")
    extra_metadata: Optional[str] = Field(None, max_length=10000, description="Additional metadata as JSON string")

    @validator('apple_music_id')
    def validate_apple_music_id(cls, v):
        """Validate Apple Music ID format."""
        if not v:
            return v
        # Apple Music IDs are alphanumeric with some special characters
        if not re.match(r'^[a-zA-Z0-9._-]+$', v):
            raise ValueError("Invalid Apple Music ID format")
        return v


class TrackCreditResponse(BaseModel):
    """Schema for track credit info."""
    engineer_name: str
    role: str

class TrackResponse(TrackBase):
    """Schema for track response."""
    id: int
    apple_music_id: Optional[str] = None
    discovered_at: datetime
    updated_at: datetime
    credits: Optional[List[TrackCreditResponse]] = []
    avg_immersiveness: Optional[float] = None
    hall_of_shame: bool = False

    class Config:
        from_attributes = True


class RefreshResponse(BaseModel):
    """Schema for refresh operation response."""
    status: str
    message: str
    tracks_added: int
    tracks_updated: int
    timestamp: datetime


class EngineerBase(BaseModel):
    """Base schema for engineer data."""
    id: int
    name: str
    slug: Optional[str] = None
    profile_image_url: Optional[str] = None

    class Config:
        from_attributes = True

class EngineerResponse(EngineerBase):
    """Response schema for engineer with track count."""
    mix_count: Optional[int] = 0


class RatingRequest(BaseModel):
    """Schema for submitting a track rating."""
    score: int = Field(..., ge=1, le=10, description="Immersiveness score (1-10)")
    is_fake: bool = Field(False, description="Flag if the Atmos mix sounds fake/up-mixed")


class RatingResponse(BaseModel):
    """Response schema after rating a track."""
    track_id: int
    avg_immersiveness: float
    is_fake_atmos_ratio: float

