"""
Database migration for Advanced Scheduler and File Management feature

This migration adds support for:
- Multiple playlists
- File uploads and storage
- Content items (videos and files)
- Advanced scheduling
- Delivery tracking
- User interactions
- Analytics
"""

import sqlite3
from pathlib import Path


def migrate(db_path: str = "officer_priya.db"):
    """Apply migration to add new tables for advanced scheduler and file management"""
    conn = sqlite3.Connection(db_path)
    cursor = conn.cursor()
    
    try:
        # Create playlists table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS playlists (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create files table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_id TEXT NOT NULL UNIQUE,
                original_name TEXT NOT NULL,
                file_type TEXT NOT NULL,
                mime_type TEXT NOT NULL,
                file_size INTEGER NOT NULL,
                storage_path TEXT NOT NULL,
                uploaded_by TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_files_type ON files(file_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_files_created ON files(created_at DESC)")
        
        # Create content_items table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS content_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                playlist_id INTEGER NOT NULL,
                content_type TEXT NOT NULL CHECK (content_type IN ('video', 'file')),
                video_url TEXT,
                file_id INTEGER,
                caption TEXT,
                position INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (playlist_id) REFERENCES playlists(id) ON DELETE CASCADE,
                FOREIGN KEY (file_id) REFERENCES files(id) ON DELETE RESTRICT
            )
        """)
        
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_content_items_playlist ON content_items(playlist_id, position)")
        
        # Create schedules table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS schedules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                playlist_id INTEGER NOT NULL,
                start_date DATE NOT NULL,
                end_date DATE,
                delivery_time TIME NOT NULL,
                frequency TEXT NOT NULL CHECK (frequency IN ('daily', 'weekdays', 'custom')),
                custom_days TEXT,
                delivery_mode TEXT NOT NULL CHECK (delivery_mode IN ('sequential', 'all_at_once')),
                timezone TEXT DEFAULT 'UTC',
                status TEXT NOT NULL CHECK (status IN ('active', 'paused', 'completed', 'upcoming')),
                current_position INTEGER DEFAULT 0,
                last_execution TIMESTAMP,
                next_execution TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (playlist_id) REFERENCES playlists(id) ON DELETE RESTRICT
            )
        """)
        
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_schedules_status ON schedules(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_schedules_next_execution ON schedules(next_execution)")
        
        # Create deliveries table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS deliveries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                schedule_id INTEGER NOT NULL,
                content_item_id INTEGER NOT NULL,
                chat_id TEXT NOT NULL,
                delivery_status TEXT NOT NULL CHECK (delivery_status IN ('sent', 'failed', 'pending')),
                retry_count INTEGER DEFAULT 0,
                error_message TEXT,
                delivered_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (schedule_id) REFERENCES schedules(id) ON DELETE CASCADE,
                FOREIGN KEY (content_item_id) REFERENCES content_items(id) ON DELETE CASCADE
            )
        """)
        
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_deliveries_schedule ON deliveries(schedule_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_deliveries_chat ON deliveries(chat_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_deliveries_status ON deliveries(delivery_status)")
        
        # Create user_interactions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                delivery_id INTEGER NOT NULL,
                chat_id TEXT NOT NULL,
                interaction_type TEXT NOT NULL CHECK (interaction_type IN ('completed', 'help_requested')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (delivery_id) REFERENCES deliveries(id) ON DELETE CASCADE
            )
        """)
        
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_interactions_delivery ON user_interactions(delivery_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_interactions_chat ON user_interactions(chat_id)")
        
        # Create file_references table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS file_references (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_id INTEGER NOT NULL,
                content_item_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (file_id) REFERENCES files(id) ON DELETE CASCADE,
                FOREIGN KEY (content_item_id) REFERENCES content_items(id) ON DELETE CASCADE,
                UNIQUE(file_id, content_item_id)
            )
        """)
        
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_file_references_file ON file_references(file_id)")
        
        conn.commit()
        print("✅ Migration completed successfully!")
        print("   - Created playlists table")
        print("   - Created files table")
        print("   - Created content_items table")
        print("   - Created schedules table")
        print("   - Created deliveries table")
        print("   - Created user_interactions table")
        print("   - Created file_references table")
        print("   - Created all indexes")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Migration failed: {e}")
        raise
    finally:
        conn.close()


def rollback(db_path: str = "officer_priya.db"):
    """Rollback migration by dropping all new tables"""
    conn = sqlite3.Connection(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("DROP TABLE IF EXISTS file_references")
        cursor.execute("DROP TABLE IF EXISTS user_interactions")
        cursor.execute("DROP TABLE IF EXISTS deliveries")
        cursor.execute("DROP TABLE IF EXISTS schedules")
        cursor.execute("DROP TABLE IF EXISTS content_items")
        cursor.execute("DROP TABLE IF EXISTS files")
        cursor.execute("DROP TABLE IF EXISTS playlists")
        
        conn.commit()
        print("✅ Rollback completed successfully!")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Rollback failed: {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "rollback":
        rollback()
    else:
        migrate()
