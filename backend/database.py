import sqlite3
from pathlib import Path
from typing import Optional

class Database:
    """Database manager for Officer Priya CDS system"""
    
    def __init__(self, db_path: str = "officer_priya.db"):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        conn = sqlite3.Connection(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """Initialize database with required tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Create config table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS config (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                chat_id TEXT NOT NULL,
                english_playlist TEXT NOT NULL,
                history_playlist TEXT NOT NULL,
                polity_playlist TEXT NOT NULL,
                geography_playlist TEXT NOT NULL,
                economics_playlist TEXT NOT NULL,
                english_index INTEGER DEFAULT 0,
                history_index INTEGER DEFAULT 0,
                polity_index INTEGER DEFAULT 0,
                geography_index INTEGER DEFAULT 0,
                economics_index INTEGER DEFAULT 0,
                gk_rotation_index INTEGER DEFAULT 0,
                day_count INTEGER DEFAULT 0,
                streak INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create daily_logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                day_number INTEGER NOT NULL UNIQUE,
                date TEXT NOT NULL,
                english_video_number INTEGER NOT NULL,
                gk_subject TEXT NOT NULL,
                gk_video_number INTEGER NOT NULL,
                status TEXT NOT NULL CHECK (status IN ('PENDING', 'DONE', 'NOT_DONE')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create error_logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS error_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                error_type TEXT NOT NULL,
                error_message TEXT NOT NULL,
                stack_trace TEXT,
                context TEXT
            )
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_daily_logs_date ON daily_logs(date DESC)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_daily_logs_status ON daily_logs(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_error_logs_timestamp ON error_logs(timestamp DESC)")
        
        conn.commit()
        conn.close()
