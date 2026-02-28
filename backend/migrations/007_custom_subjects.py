#!/usr/bin/env python3
"""
Migration 007: Add support for custom subjects
Creates a table to store custom subjects with their playlists and indices
"""

import sqlite3
from pathlib import Path

def run_migration(db_path: str = "officer_priya_multi.db"):
    """Run the migration"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Create custom_subjects table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS custom_subjects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject_name TEXT NOT NULL UNIQUE,
                playlist_url TEXT NOT NULL,
                current_index INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        print("✅ Created custom_subjects table")
        
        conn.commit()
        print("✅ Migration 007 completed successfully")
        
    except Exception as e:
        print(f"❌ Migration 007 failed: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    run_migration()
