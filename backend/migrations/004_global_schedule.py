"""
Migration: Make schedules global instead of per-user
All users receive the same content on the same day
"""

import sqlite3

def run_migration(db_path: str = "officer_priya_multi.db"):
    """Add global config and update playlist schedules"""
    conn = sqlite3.Connection(db_path)
    cursor = conn.cursor()
    
    # Drop old per-user playlist_schedules table
    cursor.execute("DROP TABLE IF EXISTS playlist_schedules")
    
    # Create global playlist schedules table (no user_id)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS global_playlist_schedules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_name TEXT NOT NULL UNIQUE,
            start_date TEXT NOT NULL,
            frequency TEXT NOT NULL CHECK (frequency IN ('daily', 'alternate')),
            selected_days TEXT NOT NULL,
            last_sent_date TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create global config table (single row for system-wide settings)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS global_config (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            current_day INTEGER DEFAULT 0,
            english_playlist TEXT NOT NULL DEFAULT 'https://www.youtube.com/watch?v=fYMbTZm803Y&list=PLhrq-fv7kVgeyGNN5Y4p2iuNd5hLIPUST',
            history_playlist TEXT NOT NULL DEFAULT 'https://www.youtube.com/watch?v=P65aLLRhwL0&list=PL3M0QAJjbrLhhy-PKTB3T2ZoA41ptNsfl',
            polity_playlist TEXT NOT NULL DEFAULT 'https://www.youtube.com/watch?v=8aJFSLC9pOw&list=PL3M0QAJjbrLj0dI6wXZad0C0qNrIhuH_W',
            geography_playlist TEXT NOT NULL DEFAULT 'https://www.youtube.com/watch?v=VVZ68jY_ZMs&list=PL3M0QAJjbrLgfkfZlkaZnmQoJhXOL1c_V',
            economics_playlist TEXT NOT NULL DEFAULT 'https://www.youtube.com/watch?v=AVf-uWZ34nE&list=PL3M0QAJjbrLhs6obUK9RiZ2JKnOMvSzWh',
            english_index INTEGER DEFAULT 0,
            history_index INTEGER DEFAULT 0,
            polity_index INTEGER DEFAULT 0,
            geography_index INTEGER DEFAULT 0,
            economics_index INTEGER DEFAULT 0,
            schedule_enabled BOOLEAN DEFAULT 0,
            schedule_time TEXT DEFAULT '06:00',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Insert default global config
    cursor.execute("""
        INSERT OR IGNORE INTO global_config (id) VALUES (1)
    """)
    
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_global_playlist_schedules_subject ON global_playlist_schedules(subject_name)")
    
    conn.commit()
    conn.close()
    
    print("✅ Migration 004: Global schedule system created")

if __name__ == "__main__":
    run_migration()
