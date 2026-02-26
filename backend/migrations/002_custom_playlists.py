"""
Migration: Add custom playlists support
Allows users to add custom subjects beyond the default 5
"""

import sqlite3

def run_migration(db_path: str = "officer_priya_multi.db"):
    """Add custom_playlists table"""
    conn = sqlite3.Connection(db_path)
    cursor = conn.cursor()
    
    # Custom playlists table (for user-defined subjects)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS custom_playlists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            subject_name TEXT NOT NULL,
            playlist_url TEXT NOT NULL,
            current_index INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            UNIQUE(user_id, subject_name)
        )
    """)
    
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_custom_playlists_user_id ON custom_playlists(user_id)")
    
    conn.commit()
    conn.close()
    
    print("✅ Migration 002: Custom playlists table created")

if __name__ == "__main__":
    run_migration()
