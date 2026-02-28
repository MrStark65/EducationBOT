#!/usr/bin/env python3
"""
Migration 008: User Blocks Table
Creates table for blocking/unblocking users
"""

import sqlite3
import sys
import os

# Add parent directory to path to import database
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from multi_user_database import MultiUserDatabase

def run_migration():
    """Create user_blocks table"""
    db = MultiUserDatabase()
    conn = db.get_connection()
    cursor = conn.cursor()
    
    try:
        # Create user_blocks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_blocks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id TEXT NOT NULL,
                blocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                blocked_by TEXT DEFAULT 'admin',
                reason TEXT,
                unblocked_at TIMESTAMP,
                UNIQUE(chat_id, blocked_at)
            )
        """)
        
        print("✅ Created user_blocks table")
        
        # Create index for faster lookups
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_blocks_chat_id 
            ON user_blocks(chat_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_blocks_active 
            ON user_blocks(chat_id, unblocked_at)
        """)
        
        print("✅ Created indexes on user_blocks table")
        
        conn.commit()
        print("✅ Migration 008 completed successfully")
        
    except Exception as e:
        print(f"❌ Migration 008 failed: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    run_migration()
