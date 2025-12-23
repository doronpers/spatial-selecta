#!/usr/bin/env python3
"""
Setup script for Spatial Selecta backend.
Initializes the database and optionally imports existing data from data.json.
"""
import sys
import os

# Add the parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import init_db, SessionLocal
from backend.scheduler import import_existing_data_json


def main():
    print("Initializing Spatial Selecta database...")
    
    # Initialize database (create tables)
    try:
        init_db()
        print("✓ Database tables created successfully")
    except Exception as e:
        print(f"✗ Error creating database tables: {e}")
        return 1
    
    # Ask if user wants to import existing data
    print("\nWould you like to import existing tracks from data.json? (y/n)")
    response = input().strip().lower()
    
    if response == 'y':
        try:
            db = SessionLocal()
            data_json_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                'data.json'
            )
            
            if not os.path.exists(data_json_path):
                print(f"✗ data.json not found at {data_json_path}")
                return 1
            
            import_existing_data_json(db, data_json_path)
            db.close()
            print("✓ Data imported successfully from data.json")
        except Exception as e:
            print(f"✗ Error importing data: {e}")
            return 1
    
    print("\n✓ Setup complete!")
    print("\nNext steps:")
    print("1. Configure your Apple Music API credentials in .env")
    print("2. Run the backend: uvicorn backend.main:app --reload")
    print("3. Access API docs at http://localhost:8000/docs")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
