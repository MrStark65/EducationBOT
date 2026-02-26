"""
Migration: Add playlist schedules support
Allows users to set start date, frequency, and selected days for each playlist
"""

import sqlite3

def run_migration(db_path: str = "officer_priya_multi.db"):
    """Add playlist_schedules table"""
    conn = sqlite3.Connection(db_path)
    cursor = conn.cursor()
    
    # Playlist schedules table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS playlist_schedules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            subject_name TEXT NOT NULL,
            start_date TEXT NOT NULL,
            frequency TEXT NOT NULL CHECK (frequency IN ('daily', 'alternate')),
            selected_days TEXT NOT NULL,
            last_sent_date TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            UNIQUE(user_id, subject_name)
        )
    """)
    
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_playlist_schedules_user_id ON playlist_schedules(user_id)")
    
    conn.commit()
    conn.close()
    
    print("✅ Migration 003: Playlist schedules table created")

if __name__ == "__main__":
    run_migration()
