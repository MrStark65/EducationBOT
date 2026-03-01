#!/usr/bin/env python3
"""
Verify PostgreSQL database is set up correctly
"""

import sys
import os
from datetime import datetime, timedelta
import pytz

try:
    import psycopg2
except ImportError:
    print("Installing psycopg2...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "psycopg2-binary"])
    import psycopg2

DATABASE_URL = "postgresql://officer_priya_user:4tlaLpq32HVQHHehr603G8F1H6iXWXo8@dpg-d6htj08gjchc73cv07gg-a.oregon-postgres.render.com/officer_priya"

def verify_database():
    """Verify all data and schedules"""
    
    print(f"\n{'='*70}")
    print(f"🔍 POSTGRESQL DATABASE VERIFICATION")
    print(f"{'='*70}\n")
    
    try:
        # Connect
        print("🔌 Connecting to PostgreSQL...")
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        print("✅ Connected!\n")
        
        # 1. Check Users
        print(f"{'='*70}")
        print("👥 USERS")
        print(f"{'='*70}")
        cursor.execute("""
            SELECT u.id, u.chat_id, u.username, u.first_name, u.is_active,
                   c.day_count, c.streak, c.english_index, c.history_index
            FROM users u
            LEFT JOIN user_config c ON u.id = c.user_id
            ORDER BY u.id
        """)
        users = cursor.fetchall()
        
        if not users:
            print("❌ NO USERS FOUND!")
            return False
        
        for user in users:
            user_id, chat_id, username, first_name, is_active, day, streak, eng_idx, hist_idx = user
            status = "✅ Active" if is_active else "❌ Inactive"
            print(f"\n{first_name} (@{username})")
            print(f"  Chat ID: {chat_id}")
            print(f"  Status: {status}")
            print(f"  Day: {day}, Streak: 🔥 {streak}")
            print(f"  English Index: {eng_idx}, History Index: {hist_idx}")
        
        # 2. Check Daily Logs
        print(f"\n{'='*70}")
        print("📋 DAILY LOGS")
        print(f"{'='*70}")
        cursor.execute("""
            SELECT u.first_name, l.day_number, l.date, l.status, l.gk_subject
            FROM user_daily_logs l
            JOIN users u ON l.user_id = u.id
            ORDER BY l.date DESC, u.id
        """)
        logs = cursor.fetchall()
        
        if not logs:
            print("⚠️  No daily logs found")
        else:
            for log in logs:
                name, day, date, status, subject = log
                emoji = "✅" if status == "DONE" else "❌"
                print(f"{emoji} {name}: Day {day} ({date}) - {status} - {subject}")
        
        # 3. Check Global Config
        print(f"\n{'='*70}")
        print("🌍 GLOBAL CONFIG")
        print(f"{'='*70}")
        cursor.execute("""
            SELECT current_day, english_index, history_index, 
                   schedule_enabled, schedule_time
            FROM global_config
            WHERE id = 1
        """)
        config = cursor.fetchone()
        
        if not config:
            print("❌ NO GLOBAL CONFIG FOUND!")
            return False
        
        current_day, eng_idx, hist_idx, enabled, schedule_time = config
        print(f"Current Day: {current_day}")
        print(f"English Index: {eng_idx} (next to send: #{eng_idx + 1})")
        print(f"History Index: {hist_idx} (next to send: #{hist_idx + 1})")
        print(f"Schedule Enabled: {'✅ Yes' if enabled else '❌ No'}")
        print(f"Schedule Time: {schedule_time} IST")
        
        # 4. Check Playlist Schedules
        print(f"\n{'='*70}")
        print("📅 PLAYLIST SCHEDULES")
        print(f"{'='*70}")
        cursor.execute("""
            SELECT subject_name, start_date, frequency, selected_days, last_sent_date
            FROM global_playlist_schedules
            ORDER BY id
        """)
        schedules = cursor.fetchall()
        
        if not schedules:
            print("❌ NO SCHEDULES FOUND!")
            return False
        
        ist = pytz.timezone('Asia/Kolkata')
        today = datetime.now(ist)
        today_weekday = today.weekday()  # 0=Monday, 6=Sunday
        
        print(f"\nToday: {today.strftime('%A, %B %d, %Y')} (Weekday: {today_weekday})")
        print(f"Current IST Time: {today.strftime('%H:%M:%S')}\n")
        
        for schedule in schedules:
            subject, start_date, freq, days, last_sent = schedule
            
            # Parse selected days
            day_list = [int(d) for d in days.split(',')] if days else []
            day_names = {0: 'Mon', 1: 'Tue', 2: 'Wed', 3: 'Thu', 4: 'Fri', 5: 'Sat', 6: 'Sun'}
            day_str = ', '.join([day_names[d] for d in day_list])
            
            # Check if should send today
            should_send_today = False
            if freq == 'daily':
                should_send_today = True
            elif freq == 'alternate':
                # Check if today is in selected days
                if today_weekday in day_list:
                    # Check if already sent today
                    if last_sent:
                        last_sent_date = datetime.strptime(str(last_sent), '%Y-%m-%d').date()
                        today_date = today.date()
                        if last_sent_date < today_date:
                            should_send_today = True
                    else:
                        # Never sent, check if start date has passed
                        start = datetime.strptime(str(start_date), '%Y-%m-%d').date()
                        if today.date() >= start:
                            should_send_today = True
            
            emoji = "📚" if subject == 'english' else "🏛️" if subject == 'history' else "⚖️" if subject == 'polity' else "🌍" if subject == 'geography' else "💰" if subject == 'economics' else "📖"
            status_emoji = "✅" if should_send_today else "⏸️"
            
            print(f"{emoji} {subject.upper()}")
            print(f"  Frequency: {freq}")
            print(f"  Days: {day_str}")
            print(f"  Start Date: {start_date}")
            print(f"  Last Sent: {last_sent or 'Never'}")
            print(f"  {status_emoji} Send Today: {'YES' if should_send_today else 'NO'}")
            print()
        
        # 5. Calculate Next Delivery
        print(f"{'='*70}")
        print("🚀 NEXT DELIVERY PREDICTION")
        print(f"{'='*70}")
        
        # Get schedule time
        schedule_hour, schedule_minute = map(int, schedule_time.split(':'))
        next_delivery = today.replace(hour=schedule_hour, minute=schedule_minute, second=0, microsecond=0)
        
        # If time has passed today, next delivery is tomorrow
        if today >= next_delivery:
            next_delivery = next_delivery + timedelta(days=1)
        
        print(f"\nNext Delivery: {next_delivery.strftime('%A, %B %d, %Y at %I:%M %p IST')}")
        print(f"Time Until Delivery: {next_delivery - today}")
        
        # Predict what will be sent
        next_day = next_delivery.weekday()
        subjects_to_send = []
        
        for schedule in schedules:
            subject, start_date, freq, days, last_sent = schedule
            day_list = [int(d) for d in days.split(',')] if days else []
            
            if freq == 'daily':
                subjects_to_send.append(subject)
            elif freq == 'alternate' and next_day in day_list:
                subjects_to_send.append(subject)
        
        if subjects_to_send:
            print(f"\nSubjects to Send:")
            for subj in subjects_to_send:
                emoji = "📚" if subj == 'english' else "🏛️" if subj == 'history' else "⚖️" if subj == 'polity' else "🌍" if subj == 'geography' else "💰" if subj == 'economics' else "📖"
                print(f"  {emoji} {subj.upper()}")
        else:
            print("\n⚠️  No subjects scheduled for next delivery!")
        
        # 6. Check Custom Subjects
        print(f"\n{'='*70}")
        print("📖 CUSTOM SUBJECTS")
        print(f"{'='*70}")
        cursor.execute("SELECT subject_name, playlist_url, current_index FROM custom_subjects")
        custom = cursor.fetchall()
        
        if custom:
            for subj in custom:
                name, url, idx = subj
                print(f"📚 {name}")
                print(f"  URL: {url}")
                print(f"  Current Index: {idx}")
        else:
            print("No custom subjects")
        
        # 7. Final Summary
        print(f"\n{'='*70}")
        print("✅ VERIFICATION SUMMARY")
        print(f"{'='*70}")
        print(f"✅ Users: {len(users)}")
        print(f"✅ Daily Logs: {len(logs)}")
        print(f"✅ Schedules: {len(schedules)}")
        print(f"✅ Custom Subjects: {len(custom)}")
        print(f"✅ Global Config: Present")
        print(f"✅ Next Delivery: {next_delivery.strftime('%A at %I:%M %p IST')}")
        print(f"\n{'='*70}")
        print("🎉 DATABASE IS READY!")
        print(f"{'='*70}\n")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = verify_database()
    sys.exit(0 if success else 1)
