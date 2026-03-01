#!/usr/bin/env python3
"""
Import data from database_export.sql into SQLite database
Run this on Render to restore data after restart
"""

import sqlite3
import sys
from pathlib import Path

def import_data():
    """Import SQL data into database"""
    
    db_path = Path(__file__).parent / "officer_priya_multi.db"
    sql_file = Path(__file__).parent / "database_export.sql"
    
    if not sql_file.exists():
        print(f"❌ SQL file not found: {sql_file}")
        return False
    
    print(f"📂 Database: {db_path}")
    print(f"📄 SQL file: {sql_file}")
    print(f"\n{'='*60}")
    print(f"🔄 IMPORTING DATA...")
    print(f"{'='*60}\n")
    
    try:
        # Read SQL file
        with open(sql_file, 'r') as f:
            sql_content = f.read()
        
        # Connect to database
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Split by semicolons and execute each statement
        # Remove comments and empty lines
        lines = []
        for line in sql_content.split('\n'):
            line = line.strip()
            if line and not line.startswith('--'):
                lines.append(line)
        
        sql_content = ' '.join(lines)
        statements = [s.strip() for s in sql_content.split(';') if s.strip()]
        
        success_count = 0
        for statement in statements:
            try:
                cursor.execute(statement)
                success_count += 1
                # Extract table name for logging
                if 'INSERT INTO' in statement:
                    table_name = statement.split('INSERT INTO')[1].split('(')[0].strip()
                    if 'DO UPDATE' in statement:
                        print(f"✅ Updated {table_name}")
                    else:
                        print(f"✅ Imported into {table_name}")
            except sqlite3.IntegrityError as e:
                # Skip conflicts (data already exists)
                print(f"⚠️  Skipped duplicate: {e}")
            except Exception as e:
                print(f"❌ Error executing statement: {e}")
                print(f"   Statement: {statement[:150]}...")
        
        conn.commit()
        conn.close()
        
        print(f"\n{'='*60}")
        print(f"✅ IMPORT COMPLETE")
        print(f"   Executed {success_count} statements")
        print(f"{'='*60}\n")
        
        # Verify data
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM user_config")
        config_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM user_daily_logs")
        log_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM global_playlist_schedules")
        schedule_count = cursor.fetchone()[0]
        
        print(f"📊 DATABASE CONTENTS:")
        print(f"   Users: {user_count}")
        print(f"   Configs: {config_count}")
        print(f"   Daily logs: {log_count}")
        print(f"   Schedules: {schedule_count}")
        
        # Show user details
        cursor.execute("""
            SELECT u.first_name, u.chat_id, c.day_count, c.streak, c.english_index, c.history_index
            FROM users u
            JOIN user_config c ON u.id = c.user_id
        """)
        
        print(f"\n👥 USER STATUS:")
        for row in cursor.fetchall():
            name, chat_id, day, streak, eng_idx, hist_idx = row
            print(f"   {name} ({chat_id}): Day {day}, Streak 🔥 {streak}, English #{eng_idx}, History #{hist_idx}")
        
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = import_data()
    sys.exit(0 if success else 1)
