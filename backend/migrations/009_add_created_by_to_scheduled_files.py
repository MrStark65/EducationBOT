"""
Migration 009: Add created_by column to scheduled_files table
"""

def upgrade(conn):
    """Add created_by column to scheduled_files table"""
    cursor = conn.cursor()
    
    # Check if column exists
    cursor.execute("PRAGMA table_info(scheduled_files)")
    columns = [row[1] for row in cursor.fetchall()]
    
    if 'created_by' not in columns:
        print("Adding created_by column to scheduled_files table...")
        cursor.execute("""
            ALTER TABLE scheduled_files 
            ADD COLUMN created_by TEXT
        """)
        conn.commit()
        print("✅ Added created_by column")
    else:
        print("✅ created_by column already exists")

def downgrade(conn):
    """Remove created_by column (SQLite doesn't support DROP COLUMN easily)"""
    print("⚠️ Downgrade not supported for this migration")
    pass

if __name__ == "__main__":
    import sqlite3
    import sys
    
    db_path = sys.argv[1] if len(sys.argv) > 1 else "officer_priya_multi.db"
    conn = sqlite3.connect(db_path)
    
    try:
        upgrade(conn)
        print(f"✅ Migration 009 completed for {db_path}")
    except Exception as e:
        print(f"❌ Migration 009 failed: {e}")
        conn.rollback()
    finally:
        conn.close()
