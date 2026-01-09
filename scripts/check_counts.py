import sqlite3
import os

def check_counts():
    db_path = 'spatial_selecta.db'
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM tracks")
        track_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM tracks WHERE format = 'Dolby Atmos'")
        atmos_count = cursor.fetchone()[0]
        
        print(f"Total Tracks: {track_count}")
        print(f"Dolby Atmos Tracks: {atmos_count}")
        
        conn.close()
    except Exception as e:
        print(f"Error checking database: {e}")

if __name__ == "__main__":
    check_counts()
