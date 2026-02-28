#!/usr/bin/env python3
"""
Migration 006: Add playlist metadata and completion tracking
"""

import sqlite3

def migrate():
    """Add playlist_metadata table"""
    conn = sqlite3.connect("officer_priya_multi.db")
    cursor = conn.cursor()
    
    # Create playlist_metadata table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS playlist_metadata (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_name TEXT NOT NULL UNIQUE,
            playlist_url TEXT NOT NULL,
            total_videos INTEGER,
            last_checked TIMESTAMP,
            completion_notified BOOLEAN DEFAULT 0,
            loop_on_completion BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create index
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_playlist_metadata_subject 
        ON playlist_metadata(subject_name)
    """)
    
    conn.commit()
    conn.close()
    print("✅ Migration 006: Playlist metadata table created")

if __name__ == "__main__":
    migrate()
