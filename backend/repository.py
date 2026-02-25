import sqlite3
from typing import List, Optional
from datetime import datetime
from models import Config, DailyLog
from database import Database


class Repository:
    """Database repository for CRUD operations"""
    
    def __init__(self, db: Database):
        self.db = db
    
    def get_config(self) -> Optional[Config]:
        """Load configuration from database"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM config WHERE id = 1")
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return Config(
                id=row["id"],
                chat_id=row["chat_id"],
                english_playlist=row["english_playlist"],
                history_playlist=row["history_playlist"],
                polity_playlist=row["polity_playlist"],
                geography_playlist=row["geography_playlist"],
                economics_playlist=row["economics_playlist"],
                english_index=row["english_index"],
                history_index=row["history_index"],
                polity_index=row["polity_index"],
                geography_index=row["geography_index"],
                economics_index=row["economics_index"],
                gk_rotation_index=row["gk_rotation_index"],
                day_count=row["day_count"],
                streak=row["streak"],
                created_at=row["created_at"],
                updated_at=row["updated_at"]
            )
        return None
    
    def update_config(self, config: Config) -> bool:
        """Persist configuration changes"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO config (
                    id, chat_id, english_playlist, history_playlist, polity_playlist,
                    geography_playlist, economics_playlist, english_index, history_index,
                    polity_index, geography_index, economics_index, gk_rotation_index,
                    day_count, streak, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                config.id, config.chat_id, config.english_playlist, config.history_playlist,
                config.polity_playlist, config.geography_playlist, config.economics_playlist,
                config.english_index, config.history_index, config.polity_index,
                config.geography_index, config.economics_index, config.gk_rotation_index,
                config.day_count, config.streak
            ))
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def insert_log(self, log: DailyLog) -> int:
        """Create new daily log entry"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO daily_logs (
                    day_number, date, english_video_number, gk_subject,
                    gk_video_number, status
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                log.day_number, log.date, log.english_video_number,
                log.gk_subject, log.gk_video_number, log.status
            ))
            conn.commit()
            log_id = cursor.lastrowid
            return log_id
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def update_log_status(self, day_number: int, status: str) -> bool:
        """Update completion status"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE daily_logs 
                SET status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE day_number = ?
            """, (status, day_number))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def get_all_logs(self) -> List[DailyLog]:
        """Retrieve all logs ordered by day descending"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM daily_logs ORDER BY day_number DESC")
        rows = cursor.fetchall()
        conn.close()
        
        logs = []
        for row in rows:
            logs.append(DailyLog(
                id=row["id"],
                day_number=row["day_number"],
                date=row["date"],
                english_video_number=row["english_video_number"],
                gk_subject=row["gk_subject"],
                gk_video_number=row["gk_video_number"],
                status=row["status"],
                created_at=row["created_at"],
                updated_at=row["updated_at"]
            ))
        return logs
    
    def get_recent_logs(self, limit: int) -> List[DailyLog]:
        """Get most recent N logs"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM daily_logs ORDER BY day_number DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        conn.close()
        
        logs = []
        for row in rows:
            logs.append(DailyLog(
                id=row["id"],
                day_number=row["day_number"],
                date=row["date"],
                english_video_number=row["english_video_number"],
                gk_subject=row["gk_subject"],
                gk_video_number=row["gk_video_number"],
                status=row["status"],
                created_at=row["created_at"],
                updated_at=row["updated_at"]
            ))
        return logs
    
    def clear_all_logs(self) -> bool:
        """Delete all log entries"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("DELETE FROM daily_logs")
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
