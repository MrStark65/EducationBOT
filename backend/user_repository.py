"""Repository for multi-user operations"""

import sqlite3
from typing import List, Optional, Dict
from datetime import datetime
from multi_user_database import MultiUserDatabase


class User:
    """User model"""
    def __init__(self, id=None, chat_id="", username="", first_name="", last_name="", 
                 is_active=True, created_at=None, last_active=None):
        self.id = id
        self.chat_id = chat_id
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.is_active = is_active
        self.created_at = created_at
        self.last_active = last_active


class UserConfig:
    """User configuration model"""
    def __init__(self, user_id, english_playlist="", history_playlist="", 
                 polity_playlist="", geography_playlist="", economics_playlist="",
                 english_index=0, history_index=0, polity_index=0, 
                 geography_index=0, economics_index=0, gk_rotation_index=0,
                 day_count=0, streak=0, schedule_enabled=False, schedule_time="06:00"):
        self.user_id = user_id
        self.english_playlist = english_playlist
        self.history_playlist = history_playlist
        self.polity_playlist = polity_playlist
        self.geography_playlist = geography_playlist
        self.economics_playlist = economics_playlist
        self.english_index = english_index
        self.history_index = history_index
        self.polity_index = polity_index
        self.geography_index = geography_index
        self.economics_index = economics_index
        self.gk_rotation_index = gk_rotation_index
        self.day_count = day_count
        self.streak = streak
        self.schedule_enabled = schedule_enabled
        self.schedule_time = schedule_time
    
    def get_current_gk_subject(self) -> str:
        subjects = ["History", "Polity", "Geography", "Economics"]
        return subjects[self.gk_rotation_index]


class UserDailyLog:
    """User daily log model"""
    def __init__(self, id=None, user_id=0, day_number=0, date="", 
                 english_video_number=0, gk_subject="", gk_video_number=0,
                 status="PENDING", created_at=None, updated_at=None):
        self.id = id
        self.user_id = user_id
        self.day_number = day_number
        self.date = date
        self.english_video_number = english_video_number
        self.gk_subject = gk_subject
        self.gk_video_number = gk_video_number
        self.status = status
        self.created_at = created_at
        self.updated_at = updated_at
    
    def is_completed(self) -> bool:
        return self.status == "DONE"


class UserRepository:
    """Repository for user operations"""
    
    def __init__(self, db: MultiUserDatabase):
        self.db = db
    
    # User operations
    def create_user(self, chat_id: str, username: str = "", first_name: str = "", last_name: str = "") -> int:
        """Create new user"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO users (chat_id, username, first_name, last_name)
                VALUES (?, ?, ?, ?)
            """, (chat_id, username, first_name, last_name))
            conn.commit()
            user_id = cursor.lastrowid
            
            # Create default config for user
            self._create_default_config(user_id)
            
            return user_id
        except sqlite3.IntegrityError:
            # User already exists, get their ID
            cursor.execute("SELECT id FROM users WHERE chat_id = ?", (chat_id,))
            row = cursor.fetchone()
            return row["id"] if row else None
        finally:
            conn.close()
    
    def _create_default_config(self, user_id: int):
        """Create default configuration for new user"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO user_config (
                user_id, english_playlist, history_playlist, polity_playlist,
                geography_playlist, economics_playlist
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            "https://www.youtube.com/watch?v=fYMbTZm803Y&list=PLhrq-fv7kVgeyGNN5Y4p2iuNd5hLIPUST",
            "https://www.youtube.com/watch?v=P65aLLRhwL0&list=PL3M0QAJjbrLhhy-PKTB3T2ZoA41ptNsfl",
            "https://www.youtube.com/watch?v=8aJFSLC9pOw&list=PL3M0QAJjbrLj0dI6wXZad0C0qNrIhuH_W",
            "https://www.youtube.com/watch?v=VVZ68jY_ZMs&list=PL3M0QAJjbrLgfkfZlkaZnmQoJhXOL1c_V",
            "https://www.youtube.com/watch?v=AVf-uWZ34nE&list=PL3M0QAJjbrLhs6obUK9RiZ2JKnOMvSzWh"
        ))
        conn.commit()
        conn.close()
    
    def get_user_by_chat_id(self, chat_id: str) -> Optional[User]:
        """Get user by chat ID"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE chat_id = ?", (chat_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return User(
                id=row["id"],
                chat_id=row["chat_id"],
                username=row["username"],
                first_name=row["first_name"],
                last_name=row["last_name"],
                is_active=row["is_active"],
                created_at=row["created_at"],
                last_active=row["last_active"]
            )
        return None
    
    def get_all_users(self) -> List[User]:
        """Get all users"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users ORDER BY created_at DESC")
        rows = cursor.fetchall()
        conn.close()
        
        users = []
        for row in rows:
            users.append(User(
                id=row["id"],
                chat_id=row["chat_id"],
                username=row["username"],
                first_name=row["first_name"],
                last_name=row["last_name"],
                is_active=row["is_active"],
                created_at=row["created_at"],
                last_active=row["last_active"]
            ))
        return users
    
    def update_last_active(self, user_id: int):
        """Update user's last active timestamp"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE users SET last_active = CURRENT_TIMESTAMP WHERE id = ?
        """, (user_id,))
        conn.commit()
        conn.close()
    
    # Config operations
    def get_user_config(self, user_id: int) -> Optional[UserConfig]:
        """Get user configuration"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user_config WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return UserConfig(
                user_id=row["user_id"],
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
                schedule_enabled=bool(row["schedule_enabled"]),
                schedule_time=row["schedule_time"]
            )
        return None
    
    def update_user_config(self, config: UserConfig) -> bool:
        """Update user configuration"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE user_config SET
                    english_playlist = ?, history_playlist = ?, polity_playlist = ?,
                    geography_playlist = ?, economics_playlist = ?,
                    english_index = ?, history_index = ?, polity_index = ?,
                    geography_index = ?, economics_index = ?, gk_rotation_index = ?,
                    day_count = ?, streak = ?, schedule_enabled = ?, schedule_time = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
            """, (
                config.english_playlist, config.history_playlist, config.polity_playlist,
                config.geography_playlist, config.economics_playlist,
                config.english_index, config.history_index, config.polity_index,
                config.geography_index, config.economics_index, config.gk_rotation_index,
                config.day_count, config.streak, config.schedule_enabled, config.schedule_time,
                config.user_id
            ))
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    # Log operations
    def insert_user_log(self, log: UserDailyLog) -> int:
        """Create new daily log entry for user"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO user_daily_logs (
                    user_id, day_number, date, english_video_number,
                    gk_subject, gk_video_number, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                log.user_id, log.day_number, log.date, log.english_video_number,
                log.gk_subject, log.gk_video_number, log.status
            ))
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def update_user_log_status(self, user_id: int, day_number: int, status: str) -> bool:
        """Update log status for user"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE user_daily_logs 
                SET status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ? AND day_number = ?
            """, (status, user_id, day_number))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def get_user_logs(self, user_id: int) -> List[UserDailyLog]:
        """Get all logs for user"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM user_daily_logs 
            WHERE user_id = ? 
            ORDER BY day_number DESC
        """, (user_id,))
        rows = cursor.fetchall()
        conn.close()
        
        logs = []
        for row in rows:
            logs.append(UserDailyLog(
                id=row["id"],
                user_id=row["user_id"],
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
    
    def clear_user_logs(self, user_id: int) -> bool:
        """Clear all logs for user"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("DELETE FROM user_daily_logs WHERE user_id = ?", (user_id,))
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
