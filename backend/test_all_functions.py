#!/usr/bin/env python3
"""
Comprehensive test of all bot functions before deployment
"""

import sys
import os
from datetime import datetime, timedelta
import pytz

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from multi_user_database import MultiUserDatabase
from user_repository import UserRepository, GlobalRepository
from video_selector import VideoSelector
from bot_polling_simple import get_weekly_schedule

IST = pytz.timezone('Asia/Kolkata')

def test_database_connection():
    """Test 1: Database Connection"""
    print(f"\n{'='*70}")
    print("TEST 1: DATABASE CONNECTION")
    print(f"{'='*70}")
    
    try:
        db = MultiUserDatabase()
        print("✅ SQLite database connected")
        
        # Check tables exist
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        required_tables = ['users', 'user_config', 'user_daily_logs', 'global_config', 
                          'global_playlist_schedules', 'custom_subjects']
        
        for table in required_tables:
            if table in tables:
                print(f"  ✅ Table '{table}' exists")
            else:
                print(f"  ❌ Table '{table}' missing!")
                return False
        
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_user_data():
    """Test 2: User Data"""
    print(f"\n{'='*70}")
    print("TEST 2: USER DATA")
    print(f"{'='*70}")
    
    try:
        db = MultiUserDatabase()
        repo = UserRepository(db)
        users = repo.get_all_users()
        
        if not users:
            print("❌ No users found!")
            return False
        
        print(f"✅ Found {len(users)} users")
        
        for user in users:
            config = repo.get_user_config(user.id)
            print(f"\n  👤 {user.first_name} (@{user.username})")
            print(f"     Chat ID: {user.chat_id}")
            print(f"     Day: {config.day_count}, Streak: 🔥 {config.streak}")
            print(f"     English: #{config.english_index}, History: #{config.history_index}")
        
        return True
    except Exception as e:
        print(f"❌ User data test failed: {e}")
        return False

def test_global_config():
    """Test 3: Global Config"""
    print(f"\n{'='*70}")
    print("TEST 3: GLOBAL CONFIG")
    print(f"{'='*70}")
    
    try:
        db = MultiUserDatabase()
        repo = GlobalRepository(db)
        config = repo.get_global_config()
        
        if not config:
            print("❌ No global config found!")
            return False
        
        print(f"✅ Global config found")
        print(f"  Current Day: {config.current_day}")
        print(f"  English Index: {config.english_index}")
        print(f"  History Index: {config.history_index}")
        print(f"  Schedule Time: {config.schedule_time} IST")
        print(f"  Schedule Enabled: {'✅ Yes' if config.schedule_enabled else '❌ No'}")
        
        return True
    except Exception as e:
        print(f"❌ Global config test failed: {e}")
        return False

def test_playlist_schedules():
    """Test 4: Playlist Schedules"""
    print(f"\n{'='*70}")
    print("TEST 4: PLAYLIST SCHEDULES")
    print(f"{'='*70}")
    
    try:
        db = MultiUserDatabase()
        repo = GlobalRepository(db)
        schedules = repo.get_all_global_playlist_schedules()
        
        if not schedules:
            print("❌ No schedules found!")
            return False
        
        print(f"✅ Found {len(schedules)} schedules")
        
        day_names = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
        
        for subject, schedule in schedules.items():
            days = schedule['selected_days']
            day_str = ', '.join([day_names[d] for d in days])
            
            emoji = "📚" if subject == 'english' else "🏛️" if subject == 'history' else "⚖️" if subject == 'polity' else "🌍" if subject == 'geography' else "💰" if subject == 'economics' else "📖"
            
            print(f"\n  {emoji} {subject.upper()}")
            print(f"     Frequency: {schedule['frequency']}")
            print(f"     Days: {day_str}")
            print(f"     Start: {schedule['start_date']}")
            print(f"     Last Sent: {schedule['last_sent_date'] or 'Never'}")
        
        return True
    except Exception as e:
        print(f"❌ Playlist schedules test failed: {e}")
        return False

def test_weekday_conversion():
    """Test 5: Weekday Conversion"""
    print(f"\n{'='*70}")
    print("TEST 5: WEEKDAY CONVERSION (Sunday=0 Fix)")
    print(f"{'='*70}")
    
    try:
        # Test for Sunday, March 1, 2026
        test_date = datetime(2026, 3, 1, 12, 0, 0, tzinfo=IST)
        python_weekday = test_date.weekday()  # Should be 6 (Sunday in Python)
        converted_weekday = (python_weekday + 1) % 7  # Should be 0 (Sunday in our system)
        
        print(f"Test Date: {test_date.strftime('%A, %B %d, %Y')}")
        print(f"Python weekday(): {python_weekday} (0=Monday, 6=Sunday)")
        print(f"Converted weekday: {converted_weekday} (0=Sunday, 1=Monday)")
        
        if converted_weekday == 0:
            print("✅ Conversion correct: Sunday = 0")
        else:
            print(f"❌ Conversion wrong: Expected 0, got {converted_weekday}")
            return False
        
        # Test schedule matching
        db = MultiUserDatabase()
        repo = GlobalRepository(db)
        schedules = repo.get_all_global_playlist_schedules()
        
        print(f"\nSchedule matching for Sunday (weekday={converted_weekday}):")
        
        expected_results = {
            'english': True,  # Daily
            'history': True,  # Sun, Sat
            'polity': False,  # Mon, Thu
            'geography': False,  # Tue, Fri
            'economics': False,  # Wed
        }
        
        all_correct = True
        for subject, schedule in schedules.items():
            if subject not in expected_results:
                continue
            
            should_send = converted_weekday in schedule['selected_days']
            expected = expected_results[subject]
            
            if should_send == expected:
                emoji = "✅" if should_send else "⏸️"
                print(f"  {emoji} {subject}: {'SEND' if should_send else 'SKIP'} (correct)")
            else:
                print(f"  ❌ {subject}: {'SEND' if should_send else 'SKIP'} (WRONG! Expected {'SEND' if expected else 'SKIP'})")
                all_correct = False
        
        return all_correct
    except Exception as e:
        print(f"❌ Weekday conversion test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_video_selector():
    """Test 6: Video Selector"""
    print(f"\n{'='*70}")
    print("TEST 6: VIDEO SELECTOR")
    print(f"{'='*70}")
    
    try:
        selector = VideoSelector()
        
        # Test English playlist
        test_playlist = "https://www.youtube.com/watch?v=fYMbTZm803Y&list=PLhrq-fv7kVgeyGNN5Y4p2iuNd5hLIPUST"
        
        print(f"Testing with English playlist...")
        video_num, video_url = selector.select_next_english(1, test_playlist)
        
        print(f"  Current Index: 1")
        print(f"  Next Video: #{video_num}")
        print(f"  URL: {video_url[:60]}...")
        
        if video_num == 2:
            print("✅ Video selector working correctly")
            return True
        else:
            print(f"❌ Expected video #2, got #{video_num}")
            return False
    except Exception as e:
        print(f"❌ Video selector test failed: {e}")
        return False

def test_weekly_schedule_display():
    """Test 7: Weekly Schedule Display (Bot Command)"""
    print(f"\n{'='*70}")
    print("TEST 7: WEEKLY SCHEDULE DISPLAY")
    print(f"{'='*70}")
    
    try:
        db = MultiUserDatabase()
        repo = UserRepository(db)
        
        # Get schedule for a test user
        users = repo.get_all_users()
        if not users:
            print("❌ No users to test with")
            return False
        
        test_user = users[0]
        print(f"Testing with user: {test_user.first_name}")
        
        schedule_data = get_weekly_schedule()
        
        print(f"\nSchedule output:")
        print(f"  Schedule Time: {schedule_data.get('schedule_time')}")
        print(f"  Current Day: {schedule_data.get('current_day')}")
        
        # Check weekly schedule
        weekly = schedule_data.get('weekly_schedule', [])
        for day in weekly:
            subjects_str = ', '.join(day['subjects'])
            today_marker = " (TODAY)" if day['is_today'] else ""
            print(f"  {day['day_name']}{today_marker}: {subjects_str}")
        
        # Check if schedule contains expected subjects
        all_subjects = []
        for day in weekly:
            all_subjects.extend(day['subjects'])
        
        if 'english' in all_subjects:
            print("\n✅ English found in schedule")
        else:
            print("\n❌ English missing from schedule")
            return False
        
        if 'history' in all_subjects:
            print("✅ History found in schedule")
        else:
            print("⚠️  History missing from schedule (might be correct depending on configuration)")
        
        return True
    except Exception as e:
        print(f"❌ Weekly schedule display test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_timezone():
    """Test 8: Timezone (IST)"""
    print(f"\n{'='*70}")
    print("TEST 8: TIMEZONE (IST)")
    print(f"{'='*70}")
    
    try:
        now_ist = datetime.now(IST)
        now_utc = datetime.now(pytz.UTC)
        
        print(f"Current IST Time: {now_ist.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        print(f"Current UTC Time: {now_utc.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        
        # IST should be UTC+5:30
        offset = now_ist.utcoffset().total_seconds() / 3600
        
        if offset == 5.5:
            print(f"✅ IST offset correct: UTC+5:30")
            return True
        else:
            print(f"❌ IST offset wrong: UTC+{offset}")
            return False
    except Exception as e:
        print(f"❌ Timezone test failed: {e}")
        return False

def test_next_delivery_calculation():
    """Test 9: Next Delivery Calculation"""
    print(f"\n{'='*70}")
    print("TEST 9: NEXT DELIVERY CALCULATION")
    print(f"{'='*70}")
    
    try:
        db = MultiUserDatabase()
        global_repo = GlobalRepository(db)
        config = global_repo.get_global_config()
        
        if not config:
            print("❌ No global config")
            return False
        
        # Parse schedule time
        schedule_hour, schedule_minute = map(int, config.schedule_time.split(':'))
        
        now = datetime.now(IST)
        next_delivery = now.replace(hour=schedule_hour, minute=schedule_minute, second=0, microsecond=0)
        
        # If time has passed today, next delivery is tomorrow
        if now >= next_delivery:
            next_delivery = next_delivery + timedelta(days=1)
        
        time_until = next_delivery - now
        
        print(f"Current Time: {now.strftime('%Y-%m-%d %H:%M:%S IST')}")
        print(f"Schedule Time: {config.schedule_time} IST")
        print(f"Next Delivery: {next_delivery.strftime('%A, %B %d at %I:%M %p IST')}")
        print(f"Time Until: {time_until}")
        
        # Predict subjects for next delivery
        next_weekday = (next_delivery.weekday() + 1) % 7  # Convert to 0=Sunday
        schedules = global_repo.get_all_global_playlist_schedules()
        
        subjects_to_send = []
        for subject, schedule in schedules.items():
            if schedule['frequency'] == 'daily':
                subjects_to_send.append(subject)
            elif next_weekday in schedule['selected_days']:
                subjects_to_send.append(subject)
        
        print(f"\nSubjects for next delivery:")
        for subj in subjects_to_send:
            emoji = "📚" if subj == 'english' else "🏛️" if subj == 'history' else "⚖️" if subj == 'polity' else "🌍" if subj == 'geography' else "💰" if subj == 'economics' else "📖"
            print(f"  {emoji} {subj.upper()}")
        
        return True
    except Exception as e:
        print(f"❌ Next delivery calculation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_all_tests():
    """Run all tests"""
    print(f"\n{'#'*70}")
    print(f"# COMPREHENSIVE BOT FUNCTION TEST")
    print(f"# Testing all functions before deployment")
    print(f"{'#'*70}")
    
    tests = [
        ("Database Connection", test_database_connection),
        ("User Data", test_user_data),
        ("Global Config", test_global_config),
        ("Playlist Schedules", test_playlist_schedules),
        ("Weekday Conversion", test_weekday_conversion),
        ("Video Selector", test_video_selector),
        ("Weekly Schedule Display", test_weekly_schedule_display),
        ("Timezone (IST)", test_timezone),
        ("Next Delivery Calculation", test_next_delivery_calculation),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ Test '{test_name}' crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*70}")
    print(f"TEST SUMMARY")
    print(f"{'='*70}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        emoji = "✅" if result else "❌"
        print(f"{emoji} {test_name}")
    
    print(f"\n{'='*70}")
    print(f"RESULT: {passed}/{total} tests passed")
    print(f"{'='*70}")
    
    if passed == total:
        print(f"\n🎉 ALL TESTS PASSED! Ready to deploy!")
        return True
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Fix issues before deploying.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
