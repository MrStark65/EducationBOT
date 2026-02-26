#!/usr/bin/env python3
"""Centralized logging system"""

import logging
import os
from datetime import datetime
from pathlib import Path
from logging.handlers import RotatingFileHandler
import sqlite3
from typing import Optional

# Create logs directory
LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)

# Database for error tracking
ERROR_DB = "logs/errors.db"


class DatabaseHandler(logging.Handler):
    """Custom handler to store errors in database"""
    
    def __init__(self):
        super().__init__()
        self._init_db()
    
    def _init_db(self):
        """Initialize error tracking database"""
        conn = sqlite3.connect(ERROR_DB)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS error_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                level TEXT NOT NULL,
                module TEXT,
                function TEXT,
                message TEXT NOT NULL,
                exception TEXT,
                stack_trace TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def emit(self, record):
        """Store log record in database"""
        try:
            conn = sqlite3.connect(ERROR_DB)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO error_logs 
                (timestamp, level, module, function, message, exception, stack_trace)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                datetime.fromtimestamp(record.created).isoformat(),
                record.levelname,
                record.module,
                record.funcName,
                record.getMessage(),
                str(record.exc_info[1]) if record.exc_info else None,
                self.format(record) if record.exc_info else None
            ))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Failed to log to database: {e}")


def setup_logger(name: str, level=logging.INFO) -> logging.Logger:
    """Setup logger with file and database handlers"""
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_format)
    
    # File handler (rotating)
    file_handler = RotatingFileHandler(
        LOGS_DIR / f"{name}.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_format)
    
    # Database handler (errors only)
    db_handler = DatabaseHandler()
    db_handler.setLevel(logging.ERROR)
    db_handler.setFormatter(file_format)
    
    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.addHandler(db_handler)
    
    return logger


def get_recent_errors(limit: int = 50) -> list:
    """Get recent errors from database"""
    try:
        conn = sqlite3.connect(ERROR_DB)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, timestamp, level, module, function, message, exception
            FROM error_logs
            ORDER BY created_at DESC
            LIMIT ?
        """, (limit,))
        
        errors = []
        for row in cursor.fetchall():
            errors.append({
                'id': row[0],
                'timestamp': row[1],
                'level': row[2],
                'module': row[3],
                'function': row[4],
                'message': row[5],
                'exception': row[6]
            })
        
        conn.close()
        return errors
    except Exception as e:
        print(f"Failed to fetch errors: {e}")
        return []


def clear_old_errors(days: int = 30):
    """Clear errors older than specified days"""
    try:
        conn = sqlite3.connect(ERROR_DB)
        cursor = conn.cursor()
        
        cursor.execute("""
            DELETE FROM error_logs
            WHERE created_at < datetime('now', '-' || ? || ' days')
        """, (days,))
        
        deleted = cursor.rowcount
        conn.commit()
        conn.close()
        
        return deleted
    except Exception as e:
        print(f"Failed to clear old errors: {e}")
        return 0


# Create default loggers
app_logger = setup_logger('app')
bot_logger = setup_logger('bot')
scheduler_logger = setup_logger('scheduler')
api_logger = setup_logger('api')
