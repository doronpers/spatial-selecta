"""
SQLAlchemy models for spatial audio tracks.
"""
from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime
from backend.database import Base


class Track(Base):
    """
    Model representing a spatial audio track.
    """
    __tablename__ = "tracks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False, index=True)
    artist = Column(String(500), nullable=False, index=True)
    album = Column(String(500), nullable=False)
    format = Column(String(100), nullable=False, index=True)  # Dolby Atmos
    platform = Column(String(100), nullable=False, index=True)  # Apple Music
    release_date = Column(DateTime, nullable=False, index=True)  # Original song release date
    atmos_release_date = Column(DateTime, nullable=True, index=True)  # When Atmos mix was released
    album_art = Column(String(10), nullable=True)  # Emoji or URL
    apple_music_id = Column(String(200), nullable=True, unique=True)  # Apple Music track ID
    discovered_at = Column(DateTime, default=lambda: datetime.now())  # When we first detected this track
    updated_at = Column(DateTime, default=lambda: datetime.now(), onupdate=lambda: datetime.now())
    extra_metadata = Column(Text, nullable=True)  # JSON field for additional metadata

    def __repr__(self):
        return f"<Track(title='{self.title}', artist='{self.artist}', format='{self.format}')>"
