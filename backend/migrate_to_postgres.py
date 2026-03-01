#!/usr/bin/env python3
"""
Migrate SQLite database to PostgreSQL
Run this once to copy all data from SQLite to PostgreSQL
"""
import os
import sqlite3
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

load_dotenv()

def migrate_sqlite_to_postgres():
    """Copy all data from SQLite to PostgreSQL"""
    
    # Connect to SQLite
    sqlite_conn = sqlite3.connect("officer_priya_multi.db")
    sqlite_conn.row_factory = sqlite3.Row
    sqlite_cursor = sqlite_conn.cursor()
    
    # Connect to PostgreSQL
    postgres_url = os.getenv("DATABASE_URL")
    if not postgres_url:
        print("❌ DATABASE_URL not found in environment variables")
        return False
    
    postgres_conn = psycopg2.connect(postgres_url)
    postgres_cursor = postgres_conn.cursor()
    
    print("="*60)
    print("🔄 MIGRATING SQLITE TO POSTGRESQL")
    print("="*60)
    
    # Get all tables from SQLite
    sqlite_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    tables = [row[0] for row in sqlite_cursor.fetchall()]
    
    print(f"\n📋 Found {len(tables)} tables to migrate:")
    for table in tables:
        print(f"   - {table}")
    
    # Migrate each table
    for table in tables:
        print(f"\n🔄 Migrating table: {table}")
        
        # Get table schema
        sqlite_cursor.execute(f"PRAGMA table_info({table})")
        columns_info = sqlite_cursor.fetchall()
        columns = [col[1] for col in columns_info]
        
        # Get all data
        sqlite_cursor.execute(f"SELECT * FROM {table}")
        rows = sqlite_cursor.fetchall()
        
        if not rows:
            print(f"   ⏭️  No data in {table}")
            continue
        
        # Convert SQLite rows to tuples
        data = [tuple(row) for row in rows]
        
        # Create INSERT query
        columns_str = ", ".join(columns)
        placeholders = ", ".join(["%s"] * len(columns))
        insert_query = f"INSERT INTO {table} ({columns_str}) VALUES ({placeholders}) ON CONFLICT DO NOTHING"
        
        # Insert data
        try:
            execute_values(postgres_cursor, insert_query, data, template=f"({placeholders})")
            postgres_conn.commit()
            print(f"   ✅ Migrated {len(rows)} rows")
        except Exception as e:
            print(f"   ❌ Error: {e}")
            postgres_conn.rollback()
    
    # Close connections
    sqlite_conn.close()
    postgres_conn.close()
    
    print("\n" + "="*60)
    print("✅ MIGRATION COMPLETE!")
    print("="*60)
    return True


if __name__ == "__main__":
    migrate_sqlite_to_postgres()
