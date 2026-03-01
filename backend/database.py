"""
Database connection manager - supports both SQLite and PostgreSQL
"""
import os
import sqlite3
from typing import Optional

# Check if we should use PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL")
USE_POSTGRES = DATABASE_URL and DATABASE_URL.startswith("postgresql://")

if USE_POSTGRES:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    print("✅ Using PostgreSQL")
else:
    print("✅ Using SQLite")


class DatabaseConnection:
    """Unified database connection that works with both SQLite and PostgreSQL"""
    
    def __init__(self, db_path: str = "officer_priya_multi.db"):
        self.db_path = db_path
        self.use_postgres = USE_POSTGRES
        self.database_url = DATABASE_URL
    
    def get_connection(self):
        """Get database connection (SQLite or PostgreSQL)"""
        if self.use_postgres:
            # PostgreSQL connection
            conn = psycopg2.connect(self.database_url)
            conn.row_factory = RealDictCursor
            return conn
        else:
            # SQLite connection
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            return conn
    
    def execute_query(self, query: str, params: tuple = None):
        """Execute a query and return results"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        results = cursor.fetchall()
        conn.close()
        return results
    
    def execute_update(self, query: str, params: tuple = None):
        """Execute an update/insert/delete query"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        conn.commit()
        affected_rows = cursor.rowcount
        conn.close()
        return affected_rows


def get_db_connection():
    """Get database connection"""
    db = DatabaseConnection()
    return db.get_connection()
