"""Multi-user database schema"""

import sqlite3
from pathlib import Path
from typing import Optional

class MultiUserDatabase:
    """Database manager for multi-user Officer Priya system"""
    
    def __init__(self, db_path: str = "officer_priya_multi.db"):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        conn = sqlite3.Connection(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """Initialize database with multi-user tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id TEXT NOT NULL UNIQUE,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # User config table (one per user)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_config (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
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
                schedule_enabled BOOLEAN DEFAULT 0,
                schedule_time TEXT DEFAULT '06:00',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                UNIQUE(user_id)
            )
        """)
        
        # User daily logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_daily_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                day_number INTEGER NOT NULL,
                date TEXT NOT NULL,
                english_video_number INTEGER NOT NULL,
                gk_subject TEXT NOT NULL,
                gk_video_number INTEGER NOT NULL,
                status TEXT NOT NULL CHECK (status IN ('PENDING', 'DONE', 'NOT_DONE')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                UNIQUE(user_id, day_number)
            )
        """)
        
        # Error logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS error_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                error_type TEXT NOT NULL,
                error_message TEXT NOT NULL,
                stack_trace TEXT,
                context TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        # Indexes for performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_chat_id ON users(chat_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_logs_user_id ON user_daily_logs(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_logs_date ON user_daily_logs(date DESC)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_config_user_id ON user_config(user_id)")
        
        conn.commit()
        conn.close()
        
        print("✅ Multi-user database initialized")
