#!/usr/bin/env python3
"""
Import data from database_export.sql into PostgreSQL database
"""

import sys
from pathlib import Path

try:
    import psycopg2
    from psycopg2 import sql
except ImportError:
    print("❌ psycopg2 not installed. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "psycopg2-binary"])
    import psycopg2
    from psycopg2 import sql

# PostgreSQL connection string
# Get from environment variable or use default
import os
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://officer_priya_user:4tlaLpq32HVQHHehr603G8F1H6iXWXo8@dpg-d6htj08gjchc73cv07gg-a.oregon-postgres.render.com/officer_priya"
)

def create_tables(cursor):
    """Create all required tables"""
    print("\n📋 Creating tables...")
    
    tables = [
        """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            chat_id VARCHAR(50) UNIQUE NOT NULL,
            username VARCHAR(100),
            first_name VARCHAR(100),
            last_name VARCHAR(100),
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS user_config (
            id SERIAL PRIMARY KEY,
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
            schedule_enabled BOOLEAN DEFAULT FALSE,
            schedule_time VARCHAR(10) DEFAULT '06:00',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            UNIQUE(user_id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS user_daily_logs (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            day_number INTEGER NOT NULL,
            date DATE NOT NULL,
            english_video_number INTEGER,
            gk_subject VARCHAR(50),
            gk_video_number INTEGER,
            status VARCHAR(20) DEFAULT 'PENDING',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS global_config (
            id SERIAL PRIMARY KEY,
            current_day INTEGER DEFAULT 0,
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
            schedule_enabled BOOLEAN DEFAULT TRUE,
            schedule_time VARCHAR(10) DEFAULT '06:00',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS global_playlist_schedules (
            id SERIAL PRIMARY KEY,
            subject_name VARCHAR(100) NOT NULL,
            start_date DATE NOT NULL,
            frequency VARCHAR(20) NOT NULL,
            selected_days VARCHAR(50),
            last_sent_date DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS custom_subjects (
            id SERIAL PRIMARY KEY,
            subject_name VARCHAR(100) UNIQUE NOT NULL,
            playlist_url TEXT NOT NULL,
            current_index INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    ]
    
    for table_sql in tables:
        cursor.execute(table_sql)
        table_name = table_sql.split("TABLE IF NOT EXISTS")[1].split("(")[0].strip()
        print(f"  ✅ {table_name}")

def import_data():
    """Import SQL data into PostgreSQL database"""
    
    sql_file = Path(__file__).parent / "database_export.sql"
    
    if not sql_file.exists():
        print(f"❌ SQL file not found: {sql_file}")
        return False
    
    print(f"📄 SQL file: {sql_file}")
    print(f"🔗 Database: PostgreSQL on Render")
    print(f"\n{'='*60}")
    print(f"🔄 IMPORTING DATA TO POSTGRESQL...")
    print(f"{'='*60}\n")
    
    try:
        # Connect to PostgreSQL
        print("🔌 Connecting to PostgreSQL...")
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        print("✅ Connected!\n")
        
        # Create tables
        create_tables(cursor)
        conn.commit()
        
        # Read SQL file
        print("\n📥 Reading SQL file...")
        with open(sql_file, 'r') as f:
            sql_content = f.read()
        
        # Convert SQLite SQL to PostgreSQL SQL
        # Replace ON CONFLICT DO NOTHING with PostgreSQL syntax
        sql_content = sql_content.replace('ON CONFLICT DO NOTHING', 'ON CONFLICT DO NOTHING')
        sql_content = sql_content.replace('ON CONFLICT(user_id)', 'ON CONFLICT (user_id)')
        sql_content = sql_content.replace('ON CONFLICT(id)', 'ON CONFLICT (id)')
        
        # Remove comments and split statements
        lines = []
        for line in sql_content.split('\n'):
            line = line.strip()
            if line and not line.startswith('--'):
                lines.append(line)
        
        sql_content = ' '.join(lines)
        statements = [s.strip() for s in sql_content.split(';') if s.strip()]
        
        print(f"📊 Found {len(statements)} statements to execute\n")
        
        success_count = 0
        for i, statement in enumerate(statements, 1):
            try:
                cursor.execute(statement)
                success_count += 1
                # Extract table name for logging
                if 'INSERT INTO' in statement:
                    table_name = statement.split('INSERT INTO')[1].split('(')[0].strip()
                    if 'DO UPDATE' in statement:
                        print(f"  {i}. ✅ Updated {table_name}")
                    else:
                        print(f"  {i}. ✅ Inserted into {table_name}")
            except psycopg2.IntegrityError as e:
                print(f"  {i}. ⚠️  Skipped duplicate: {e}")
                conn.rollback()
            except Exception as e:
                print(f"  {i}. ❌ Error: {e}")
                print(f"     Statement: {statement[:150]}...")
                conn.rollback()
        
        conn.commit()
        
        print(f"\n{'='*60}")
        print(f"✅ IMPORT COMPLETE")
        print(f"   Executed {success_count}/{len(statements)} statements")
        print(f"{'='*60}\n")
        
        # Verify data
        print(f"📊 DATABASE CONTENTS:")
        
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"   Users: {user_count}")
        
        cursor.execute("SELECT COUNT(*) FROM user_config")
        config_count = cursor.fetchone()[0]
        print(f"   Configs: {config_count}")
        
        cursor.execute("SELECT COUNT(*) FROM user_daily_logs")
        log_count = cursor.fetchone()[0]
        print(f"   Daily logs: {log_count}")
        
        cursor.execute("SELECT COUNT(*) FROM global_playlist_schedules")
        schedule_count = cursor.fetchone()[0]
        print(f"   Schedules: {schedule_count}")
        
        cursor.execute("SELECT COUNT(*) FROM custom_subjects")
        custom_count = cursor.fetchone()[0]
        print(f"   Custom subjects: {custom_count}")
        
        # Show user details
        cursor.execute("""
            SELECT u.first_name, u.chat_id, c.day_count, c.streak, c.english_index, c.history_index
            FROM users u
            JOIN user_config c ON u.id = c.user_id
            ORDER BY u.id
        """)
        
        print(f"\n👥 USER STATUS:")
        for row in cursor.fetchall():
            name, chat_id, day, streak, eng_idx, hist_idx = row
            print(f"   {name} ({chat_id}): Day {day}, Streak 🔥 {streak}, English #{eng_idx}, History #{hist_idx}")
        
        # Show global config
        cursor.execute("SELECT current_day, english_index, history_index FROM global_config WHERE id=1")
        result = cursor.fetchone()
        if result:
            current_day, eng_idx, hist_idx = result
            print(f"\n🌍 GLOBAL CONFIG:")
            print(f"   Current Day: {current_day}")
            print(f"   English Index: {eng_idx}")
            print(f"   History Index: {hist_idx}")
        
        cursor.close()
        conn.close()
        
        print(f"\n{'='*60}")
        print(f"✅ SUCCESS! Data imported to PostgreSQL")
        print(f"{'='*60}\n")
        
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = import_data()
    sys.exit(0 if success else 1)
