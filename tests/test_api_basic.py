import os
import pytest

# Set environment variables BEFORE importing app to ensure they are picked up
os.environ["ENVIRONMENT"] = "testing"
os.environ["DATABASE_URL"] = "sqlite:///./test_spatial_selecta.db"

from fastapi.testclient import TestClient
from backend.main import app
from backend.database import Base, engine

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    # Create tables
    Base.metadata.create_all(bind=engine)
    yield
    # Cleanup
    if os.path.exists("./test_spatial_selecta.db"):
        os.remove("./test_spatial_selecta.db")

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["name"] == "SpatialSelects.com API"

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_get_tracks_structure():
    # This might fail if DB is empty, but returns 200 list
    response = client.get("/api/tracks?limit=10")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        # Check structure of first track
        track = data[0]
        assert "title" in track
        assert "artist" in track
        assert "platform" in track

def test_get_engineers():
    response = client.get("/api/engineers")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
