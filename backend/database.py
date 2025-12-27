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
                conn.execute(text('ALTER TABLE tracks ADD COLUMN IF NOT EXISTS music_link VARCHAR(500)'))
            conn.commit()
            print("Migration: Added music_link column to tracks table")

    # Phase 1 Migrations
    if 'hall_of_shame' not in existing_columns:
        with engine.connect() as conn:
            if 'sqlite' in DATABASE_URL:
                conn.execute(text('ALTER TABLE tracks ADD COLUMN hall_of_shame BOOLEAN DEFAULT 0'))
            else:
                conn.execute(text('ALTER TABLE tracks ADD COLUMN IF NOT EXISTS hall_of_shame BOOLEAN DEFAULT FALSE'))
            conn.commit()
            print("Migration: Added hall_of_shame column")

    if 'avg_immersiveness' not in existing_columns:
        with engine.connect() as conn:
            if 'sqlite' in DATABASE_URL:
                conn.execute(text('ALTER TABLE tracks ADD COLUMN avg_immersiveness FLOAT'))
            else:
                conn.execute(text('ALTER TABLE tracks ADD COLUMN IF NOT EXISTS avg_immersiveness FLOAT'))
            conn.commit()
            print("Migration: Added avg_immersiveness column")

    if 'review_summary' not in existing_columns:
        with engine.connect() as conn:
            if 'sqlite' in DATABASE_URL:
                conn.execute(text('ALTER TABLE tracks ADD COLUMN review_summary TEXT'))
            else:
                conn.execute(text('ALTER TABLE tracks ADD COLUMN IF NOT EXISTS review_summary TEXT'))
            conn.commit()
            print("Migration: Added review_summary column")


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
