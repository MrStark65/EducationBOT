#!/usr/bin/env python3
"""Migration 005: Create advanced schedules table"""

import sqlite3

def migrate(db_path: str = "officer_priya_multi.db"):
    """Create schedules table for advanced scheduler"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create schedules table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS schedules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            schedule_type TEXT NOT NULL,
            cron_expression TEXT,
            time TEXT,
            days_of_week TEXT,
            content_type TEXT NOT NULL,
            content_id TEXT,
            enabled BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()
    print("✅ Migration 005: Advanced schedules table created")

if __name__ == "__main__":
    migrate()
