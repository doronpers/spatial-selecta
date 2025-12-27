"""
Database configuration and session management.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# Database URL - defaults to SQLite for local development
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./spatial_selecta.db"
)

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for declarative models
Base = declarative_base()


def init_db():
    """Initialize database by creating all tables and run migrations."""
    from backend.models import Track
    Base.metadata.create_all(bind=engine)
    # Run migrations for existing databases
    run_migrations()


def run_migrations():
    """
    Run database migrations for schema updates.
    This handles adding new columns to existing databases.
    """
    from sqlalchemy import inspect, text

    inspector = inspect(engine)

    # Check if tracks table exists
    if 'tracks' not in inspector.get_table_names():
        return  # Table doesn't exist yet, will be created by create_all

    # Get existing columns
    existing_columns = {col['name'] for col in inspector.get_columns('tracks')}

    # Add music_link column if it doesn't exist
    if 'music_link' not in existing_columns:
        with engine.connect() as conn:
            if 'sqlite' in DATABASE_URL:
                conn.execute(text('ALTER TABLE tracks ADD COLUMN music_link VARCHAR(500)'))
            else:
                # PostgreSQL syntax
                conn.execute(text('ALTER TABLE tracks ADD COLUMN IF NOT EXISTS music_link VARCHAR(500)'))
            conn.commit()
            print("Migration: Added music_link column to tracks table")


def get_db():
    """
    Dependency to get database session.
    Yields a database session and ensures it's closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
