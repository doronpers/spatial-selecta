from backend.database import init_db, engine
from sqlalchemy import inspect

def verify_schema():
    print("Initializing database...")
    init_db()
    
    inspector = inspect(engine)
    table_names = inspector.get_table_names()
    print(f"Tables found: {table_names}")
    
    expected_tables = ['tracks', 'engineers', 'track_credits', 'region_availability', 'community_ratings']
    for table in expected_tables:
        if table in table_names:
            print(f"✅ Table '{table}' exists.")
        else:
            print(f"❌ Table '{table}' MISSING.")
            
    # Check columns in tracks
    columns = [col['name'] for col in inspector.get_columns('tracks')]
    expected_columns = ['hall_of_shame', 'avg_immersiveness', 'review_summary']
    for col in expected_columns:
        if col in columns:
            print(f"✅ Column '{col}' in 'tracks' exists.")
        else:
            print(f"❌ Column '{col}' in 'tracks' MISSING.")

if __name__ == "__main__":
    verify_schema()
