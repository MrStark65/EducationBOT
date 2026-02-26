"""
User Management System

Handles user blocking, analytics, and activity tracking
"""

import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class UserActivity:
    """User activity data"""
    chat_id: str
    username: str
    total_days: int
    completed_days: int
    completion_rate: float
    current_streak: int
    longest_streak: int
    last_activity: Optional[datetime]
    is_blocked: bool
    created_at: datetime


class UserManager:
    """Manage users, blocking, and analytics"""
    
    def __init__(self, db_path: str = "officer_priya_multi.db"):
        self.db_path = db_path
        self._ensure_tables()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _ensure_tables(self):
        """Ensure required tables exist"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # User blocking table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_blocks (
                chat_id TEXT PRIMARY KEY,
                blocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                blocked_by TEXT,
                reason TEXT,
                unblocked_at TIMESTAMP
            )
        """)
        
        # User activity tracking table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_activity_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id TEXT NOT NULL,
                activity_type TEXT NOT NULL,
                activity_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_activity_chat ON user_activity_log(chat_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_activity_created ON user_activity_log(created_at DESC)")
        
        conn.commit()
        conn.close()
    
    def block_user(self, chat_id: str, reason: str = None, blocked_by: str = "admin") -> bool:
        """Block a user"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO user_blocks (chat_id, blocked_at, blocked_by, reason, unblocked_at)
                VALUES (?, CURRENT_TIMESTAMP, ?, ?, NULL)
            """, (chat_id, blocked_by, reason))
            
            # Log activity
            self.log_activity(chat_id, "user_blocked", f"Blocked by {blocked_by}: {reason}")
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error blocking user: {e}")
            return False
    
    def unblock_user(self, chat_id: str) -> bool:
        """Unblock a user"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE user_blocks
                SET unblocked_at = CURRENT_TIMESTAMP
                WHERE chat_id = ? AND unblocked_at IS NULL
            """, (chat_id,))
            
            # Log activity
            self.log_activity(chat_id, "user_unblocked", "User unblocked")
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error unblocking user: {e}")
            return False
    
    def is_user_blocked(self, chat_id: str) -> bool:
        """Check if user is blocked"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 1 FROM user_blocks
            WHERE chat_id = ? AND unblocked_at IS NULL
        """, (chat_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        return result is not None
    
    def get_blocked_users(self) -> List[Dict]:
        """Get all blocked users"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT ub.*, u.username
            FROM user_blocks ub
            LEFT JOIN users u ON ub.chat_id = u.chat_id
            WHERE ub.unblocked_at IS NULL
            ORDER BY ub.blocked_at DESC
        """)
        
        users = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return users
    
    def log_activity(self, chat_id: str, activity_type: str, activity_data: str = None):
        """Log user activity"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO user_activity_log (chat_id, activity_type, activity_data)
                VALUES (?, ?, ?)
            """, (chat_id, activity_type, activity_data))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error logging activity: {e}")
    
    def get_user_activity(self, chat_id: str, limit: int = 50) -> List[Dict]:
        """Get user activity log"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM user_activity_log
            WHERE chat_id = ?
            ORDER BY created_at DESC
            LIMIT ?
        """, (chat_id, limit))
        
        activities = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return activities
    
    def get_user_analytics(self, chat_id: str) -> Optional[UserActivity]:
        """Get comprehensive user analytics"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Get user info
        cursor.execute("SELECT * FROM users WHERE chat_id = ?", (chat_id,))
        user = cursor.fetchone()
        
        if not user:
            conn.close()
            return None
        
        user_id = user['id']
        
        # Get daily logs using user_id
        cursor.execute("""
            SELECT status, created_at
            FROM user_daily_logs
            WHERE user_id = ?
            ORDER BY day_number
        """, (user_id,))
        
        logs = cursor.fetchall()
        
        # Calculate metrics
        total_days = len(logs)
        completed_days = sum(1 for log in logs if log['status'] == 'DONE')
        completion_rate = (completed_days / total_days * 100) if total_days > 0 else 0
        
        # Calculate streaks
        current_streak = 0
        longest_streak = 0
        temp_streak = 0
        
        for log in reversed(logs):
            if log['status'] == 'DONE':
                temp_streak += 1
                longest_streak = max(longest_streak, temp_streak)
            else:
                if current_streak == 0:
                    current_streak = temp_streak
                temp_streak = 0
        
        if temp_streak > 0:
            current_streak = temp_streak
        
        # Get last activity
        last_activity = logs[-1]['created_at'] if logs else None
        
        # Check if blocked
        is_blocked = self.is_user_blocked(chat_id)
        
        conn.close()
        
        return UserActivity(
            chat_id=chat_id,
            username=user['username'],
            total_days=total_days,
            completed_days=completed_days,
            completion_rate=round(completion_rate, 2),
            current_streak=current_streak,
            longest_streak=longest_streak,
            last_activity=datetime.fromisoformat(last_activity) if last_activity else None,
            is_blocked=is_blocked,
            created_at=datetime.fromisoformat(user['created_at'])
        )
    
    def get_all_users_analytics(self) -> List[UserActivity]:
        """Get analytics for all users"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT chat_id FROM users")
        users = cursor.fetchall()
        conn.close()
        
        analytics = []
        for user in users:
            user_analytics = self.get_user_analytics(user['chat_id'])
            if user_analytics:
                analytics.append(user_analytics)
        
        return analytics
    
    def get_system_analytics(self) -> Dict:
        """Get system-wide analytics"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Total users
        cursor.execute("SELECT COUNT(*) as count FROM users")
        total_users = cursor.fetchone()['count']
        
        # Active users (activity in last 7 days) - use user_id instead of chat_id
        cursor.execute("""
            SELECT COUNT(DISTINCT user_id) as count
            FROM user_daily_logs
            WHERE created_at >= datetime('now', '-7 days')
        """)
        active_users = cursor.fetchone()['count']
        
        # Blocked users
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM user_blocks
            WHERE unblocked_at IS NULL
        """)
        blocked_users = cursor.fetchone()['count']
        
        # Total completions
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM user_daily_logs
            WHERE status = 'DONE'
        """)
        total_completions = cursor.fetchone()['count']
        
        # Average completion rate
        cursor.execute("""
            SELECT 
                CAST(SUM(CASE WHEN status = 'DONE' THEN 1 ELSE 0 END) AS FLOAT) / 
                COUNT(*) * 100 as avg_rate
            FROM user_daily_logs
        """)
        avg_completion_rate = cursor.fetchone()['avg_rate'] or 0
        
        conn.close()
        
        return {
            'total_users': total_users,
            'active_users': active_users,
            'blocked_users': blocked_users,
            'total_completions': total_completions,
            'average_completion_rate': round(avg_completion_rate, 2)
        }


# Global instance
_user_manager = None


def get_user_manager(db_path: str = "officer_priya_multi.db") -> UserManager:
    """Get global user manager instance"""
    global _user_manager
    if _user_manager is None:
        _user_manager = UserManager(db_path)
    return _user_manager
