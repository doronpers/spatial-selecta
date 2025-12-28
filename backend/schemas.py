"""
Pydantic schemas for API request/response validation.
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class TrackBase(BaseModel):
    """Base schema for track data."""
    title: str
    artist: str
    album: str
    format: str
    platform: str
    release_date: datetime
    atmos_release_date: Optional[datetime] = None
    album_art: Optional[str] = None


class TrackCreate(TrackBase):
    """Schema for creating a new track."""
    apple_music_id: Optional[str] = None
    extra_metadata: Optional[str] = None


class TrackResponse(TrackBase):
    """Schema for track response."""
    id: int
    apple_music_id: Optional[str] = None
    discovered_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RefreshResponse(BaseModel):
    """Schema for refresh operation response."""
    status: str
    message: str
    tracks_added: int
    tracks_updated: int
    timestamp: datetime
