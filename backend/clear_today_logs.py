#!/usr/bin/env python3
"""Clear today's logs for testing purposes"""

from datetime import datetime
from multi_user_database import MultiUserDatabase
from user_repository import UserRepository

def clear_today_logs():
    """Clear all logs for today's date"""
    db = MultiUserDatabase()
    user_repo = UserRepository(db)
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Get all users
    users = user_repo.get_all_users()
    
    print(f"🗑️  Clearing logs for date: {today}")
    print("=" * 50)
    
    for user in users:
        logs = user_repo.get_user_logs(user.id)
        today_logs = [log for log in logs if log.date == today]
        
        if today_logs:
            # Delete today's logs
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM user_daily_logs WHERE user_id = ? AND date = ?",
                (user.id, today)
            )
            conn.commit()
            conn.close()
            
            print(f"✅ Cleared {len(today_logs)} log(s) for {user.first_name} (ID: {user.chat_id})")
        else:
            print(f"ℹ️  No logs today for {user.first_name} (ID: {user.chat_id})")
    
    print("=" * 50)
    print("✅ Done! You can now test sending messages again.")

if __name__ == "__main__":
    clear_today_logs()
