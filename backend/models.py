"""
SQLAlchemy models for spatial audio tracks.
"""
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from backend.database import Base


class Engineer(Base):
    """
    Model representing an audio engineer (mixer, masterer, etc.).
    """
    __tablename__ = "engineers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(500), unique=True, nullable=False, index=True)
    slug = Column(String(500), index=True)
    profile_image_url = Column(String(500), nullable=True)

    # Relationships
    credits = relationship("TrackCredit", back_populates="engineer")


class TrackCredit(Base):
    """
    Association model linking tracks to engineers with specific roles.
    """
    __tablename__ = "track_credits"

    id = Column(Integer, primary_key=True, index=True)
    track_id = Column(Integer, ForeignKey("tracks.id"), nullable=False, index=True)
    engineer_id = Column(Integer, ForeignKey("engineers.id"), nullable=False, index=True)
    role = Column(String(100), nullable=False)  # e.g., "Immersive Mix Engineer"

    # Relationships
    track = relationship("Track", back_populates="credits")
    engineer = relationship("Engineer", back_populates="credits")

    @property
    def engineer_name(self):
        return self.engineer.name if self.engineer else "Unknown"


class RegionAvailability(Base):
    """
    Model tracking track availability across different storefronts.
    """
    __tablename__ = "region_availability"

    id = Column(Integer, primary_key=True, index=True)
    track_id = Column(Integer, ForeignKey("tracks.id"), nullable=False, index=True)
    storefront = Column(String(10), nullable=False, index=True)  # e.g., "us", "gb", "jp"
    is_available = Column(Boolean, default=True)
    format = Column(String(100), nullable=False)  # e.g., "Dolby Atmos", "Stereo"

    # Relationships
    track = relationship("Track", back_populates="region_availability")


class CommunityRating(Base):
    """
    Model for community ratings and quality checks.
    """
    __tablename__ = "community_ratings"

    id = Column(Integer, primary_key=True, index=True)
    track_id = Column(Integer, ForeignKey("tracks.id"), nullable=False, index=True)
    immersiveness_score = Column(Integer, nullable=False)  # 1-10
    is_fake_atmos = Column(Boolean, default=False)
    user_ip_hash = Column(String(64), nullable=False, index=True)  # Anonymized user identifier
    created_at = Column(DateTime, default=datetime.now)

    # Relationships
    track = relationship("Track", back_populates="ratings")


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
    music_link = Column(String(500), nullable=True)  # Direct link to track on streaming platform
    apple_music_id = Column(String(200), nullable=True, unique=True)  # Apple Music track ID
    discovered_at = Column(DateTime, default=datetime.now)  # When we first detected this track
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    extra_metadata = Column(Text, nullable=True)  # JSON field for additional metadata

    # New fields for Phase 1
    hall_of_shame = Column(Boolean, default=False)
    avg_immersiveness = Column(Float, nullable=True)  # Cached average
    review_summary = Column(Text, nullable=True)  # Editorial notes

    # Relationships
    credits = relationship("TrackCredit", back_populates="track", cascade="all, delete-orphan")
    region_availability = relationship("RegionAvailability", back_populates="track", cascade="all, delete-orphan")
    ratings = relationship("CommunityRating", back_populates="track", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Track(title='{self.title}', artist='{self.artist}', format='{self.format}')>"
