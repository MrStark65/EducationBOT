#!/usr/bin/env python3
"""
Simple Telegram Bot with Polling using direct API calls
Works with Python 3.14
"""
import os
import time
import requests
from dotenv import load_dotenv
from multi_user_database import MultiUserDatabase
from user_repository import UserRepository, User
from logger import app_logger

load_dotenv()

# Initialize database
db = MultiUserDatabase()
user_repo = UserRepository(db)

def send_message(bot_token, chat_id, text):
    """Send a message using Telegram API"""
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": text
    }
    try:
        response = requests.post(url, json=data, timeout=10)
        return response.json()
    except Exception as e:
        print(f"❌ Error sending message: {e}")
        return None

def send_typing_action(bot_token, chat_id):
    """Send typing indicator"""
    url = f"https://api.telegram.org/bot{bot_token}/sendChatAction"
    data = {
        "chat_id": chat_id,
        "action": "typing"
    }
    try:
        requests.post(url, json=data, timeout=5)
    except:
        pass

def get_ai_response_with_context(user_message, chat_id, user_name="User"):
    """Get AI response with user context (progress, streak, schedule)"""
    try:
        from ai_assistant import AIAssistant
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            return "❌ AI service not configured. Please contact admin."
        
        # Check if user is asking about schedule
        schedule_keywords = [
            'schedule', 'today', 'tomorrow', 'what do i have', 'what subjects',
            'when do i get', 'what am i studying', 'what will i study',
            'show me schedule', 'my schedule', 'weekly schedule', 'this week',
            'time of content', 'content time', 'what time', 'timing', 'time table',
            'timetable', 'send time', 'delivery time', 'when will i receive'
        ]
        
        # Check if user is asking about days per subject or playlist lengths
        days_per_subject_keywords = [
            'how many days', 'days per week', 'how often', 'frequency',
            'how many times', 'days for', 'times per week', 'weekly frequency',
            'how many classes', 'classes per week', 'how many sessions',
            'sessions per week', 'how many english', 'how many history',
            'how many polity', 'how many geography', 'how many economics',
            'how many videos', 'total videos', 'playlist length',
            'how many lessons', 'total classes', 'total lessons',
            'how many subjects', 'total subjects', 'subjects count',
            'how many playlist', 'total playlist', 'playlist count',
            'all subject', 'all playlist', 'study plan', 'subjects',
            'playlists', 'what subjects', 'which subjects'
        ]
        
        message_lower = user_message.lower()
        is_schedule_query = any(keyword in message_lower for keyword in schedule_keywords)
        is_days_query = any(keyword in message_lower for keyword in days_per_subject_keywords)
        
        # Get user data from database
        user = user_repo.get_user_by_chat_id(str(chat_id))
        user_context = {}
        
        if user:
            config = user_repo.get_user_config(user.id)
            logs = user_repo.get_user_logs(user.id)
            
            if config:
                user_context['streak'] = config.streak
                user_context['day_count'] = config.day_count
                user_context['first_name'] = user.first_name
                user_context['total_days'] = len(logs)
                
                # Calculate completion rate
                if logs:
                    completed = sum(1 for log in logs if log.is_completed())
                    user_context['completion_rate'] = (completed / len(logs)) * 100
                    user_context['completed_days'] = completed
                    user_context['pending_tasks'] = len(logs) - completed
        
        # If asking about schedule or days per subject, fetch and include it
        if is_schedule_query or is_days_query:
            schedule_data = get_weekly_schedule()
            if schedule_data:
                user_context['has_schedule'] = True
                user_context['schedule_data'] = schedule_data
                
                # If asking about days per subject, calculate it
                if is_days_query:
                    days_per_subject = calculate_days_per_subject(schedule_data)
                    user_context['days_per_subject'] = days_per_subject
                    
                    # Also get actual playlist lengths from YouTube API
                    playlist_lengths = get_playlist_lengths()
                    if playlist_lengths:
                        user_context['playlist_lengths'] = playlist_lengths
                        user_context['total_subjects'] = len(playlist_lengths)
                    
                    # Check if asking about a specific subject
                    specific_subject = None
                    for subject in ['english', 'history', 'polity', 'geography', 'economics']:
                        if subject in message_lower:
                            specific_subject = subject
                            break
                    
                    # Also check custom subjects
                    if not specific_subject and playlist_lengths:
                        for subject in playlist_lengths.keys():
                            if subject in message_lower:
                                specific_subject = subject
                                break
                    
                    if specific_subject:
                        user_context['specific_subject'] = specific_subject
                    
                    user_context['schedule_type'] = 'days_per_subject'
                # Determine what type of schedule query
                elif 'today' in message_lower or 'what do i have' in message_lower:
                    user_context['schedule_type'] = 'today'
                elif 'tomorrow' in message_lower:
                    user_context['schedule_type'] = 'tomorrow'
                else:
                    user_context['schedule_type'] = 'weekly'
        
        ai = AIAssistant(api_key=api_key)
        response = ai.get_response(user_message, user_name=user_name, user_context=user_context)
        return response
    except Exception as e:
        print(f"❌ AI Error: {e}")
        app_logger.error(f"AI Error: {e}", exc_info=True)
        return "❌ Sorry, I'm having trouble processing your request. Please try again."

def get_ai_response(user_message, user_name="User"):
    """Get AI response using the AI assistant (legacy - without context)"""
    try:
        from ai_assistant import AIAssistant
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            return "❌ AI service not configured. Please contact admin."
        
        ai = AIAssistant(api_key=api_key)
        response = ai.get_response(user_message, user_name=user_name)
        return response
    except Exception as e:
        print(f"❌ AI Error: {e}")
        app_logger.error(f"AI Error: {e}", exc_info=True)
        return "❌ Sorry, I'm having trouble processing your request. Please try again."

def handle_start_command(bot_token, chat_id, user_info):
    """Handle /start command"""
    first_name = user_info.get("first_name", "User")
    last_name = user_info.get("last_name", "")
    username = user_info.get("username", "")
    
    # Check if user exists
    existing_user = user_repo.get_user_by_chat_id(str(chat_id))
    
    if not existing_user:
        # Create new user
        user_repo.create_user(
            chat_id=str(chat_id),
            username=username,
            first_name=first_name,
            last_name=last_name
        )
        
        welcome_msg = f"👋 Welcome {first_name}!\n\n"
        welcome_msg += "🎯 Officer Priya CDS Preparation Bot\n\n"
        welcome_msg += "You'll receive daily study materials including:\n"
        welcome_msg += "📚 English videos\n"
        welcome_msg += "📖 GK content (History, Polity, Geography, Economics)\n"
        welcome_msg += "📄 Study documents and PDFs\n\n"
        welcome_msg += "✅ Mark your progress with Done/Not Done buttons\n"
        welcome_msg += "🔥 Build your study streak!\n\n"
        welcome_msg += "Ready to start your CDS preparation journey! 💪"
        
        print(f"✅ New user registered: {first_name} ({chat_id})")
        app_logger.info(f"New user registered: {first_name} ({chat_id})")
    else:
        welcome_msg = f"👋 Welcome back {first_name}!\n\n"
        welcome_msg += "You're already registered. You'll continue receiving daily study materials.\n\n"
        welcome_msg += "Keep up the great work! 🔥"
        
        print(f"✅ Existing user: {first_name} ({chat_id})")
        app_logger.info(f"Existing user started bot: {first_name} ({chat_id})")
    
    send_message(bot_token, chat_id, welcome_msg)

def handle_help_command(bot_token, chat_id):
    """Handle /help command"""
    help_msg = "🤖 Officer Priya CDS Bot - Help\n\n"
    help_msg += "Available commands:\n"
    help_msg += "/start - Register and start receiving materials\n"
    help_msg += "/schedule - View your weekly study schedule\n"
    help_msg += "/today - See today's schedule\n"
    help_msg += "/tomorrow - See tomorrow's schedule\n"
    help_msg += "/help - Show this help message\n\n"
    help_msg += "💬 You can also send me any message and I'll help you with:\n"
    help_msg += "• Study tips and guidance\n"
    help_msg += "• CDS preparation advice\n"
    help_msg += "• Answering your questions\n\n"
    help_msg += "📚 You'll receive daily study materials automatically.\n"
    help_msg += "Use the Done/Not Done buttons to track your progress!"
    
    send_message(bot_token, chat_id, help_msg)

def get_playlist_lengths():
    """Get actual video counts for all playlists using YouTube API"""
    try:
        from user_repository import GlobalRepository
        from multi_user_database import MultiUserDatabase
        from playlist_tracker import PlaylistTracker
        import os
        
        db = MultiUserDatabase()
        global_repo = GlobalRepository(db)
        config = global_repo.get_global_config()
        
        if not config:
            return None
        
        youtube_api_key = os.getenv("YOUTUBE_API_KEY")
        tracker = PlaylistTracker()
        
        # Get default subjects
        playlists = {
            'english': config.english_playlist,
            'history': config.history_playlist,
            'polity': config.polity_playlist,
            'geography': config.geography_playlist,
            'economics': config.economics_playlist
        }
        
        # Get custom subjects
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT subject_name, playlist_url FROM custom_subjects ORDER BY subject_name")
        custom_subjects = cursor.fetchall()
        conn.close()
        
        for subject_name, playlist_url in custom_subjects:
            playlists[subject_name.lower()] = playlist_url
        
        playlist_lengths = {}
        for subject, url in playlists.items():
            if url:
                length = tracker.get_playlist_length(url, youtube_api_key)
                if length:
                    playlist_lengths[subject] = length
                else:
                    # If we can't get the length, still include the subject with "Unknown"
                    print(f"⚠️ Could not get playlist length for {subject}: {url}")
                    playlist_lengths[subject] = "Unknown"
        
        print(f"✅ Playlist lengths fetched: {list(playlist_lengths.keys())}")
        return playlist_lengths
    except Exception as e:
        print(f"❌ Error getting playlist lengths: {e}")
        return None

def calculate_days_per_subject(schedule_data):
    """Calculate how many days per week each subject is scheduled based on their configuration"""
    try:
        from user_repository import GlobalRepository
        from multi_user_database import MultiUserDatabase
        
        db = MultiUserDatabase()
        global_repo = GlobalRepository(db)
        
        # Get all playlist schedules
        all_schedules = global_repo.get_all_global_playlist_schedules()
        
        days_count = {}
        for subject, schedule in all_schedules.items():
            # Count how many days per week this subject is scheduled
            selected_days = schedule.get('selected_days', [])
            frequency = schedule.get('frequency', 'daily')
            
            if frequency == 'daily':
                # Daily means it sends on all selected days
                days_count[subject] = len(selected_days)
            elif frequency == 'alternate':
                # Alternate means it sends every other occurrence on selected days
                # So it sends approximately once per week regardless of how many days are selected
                # Because it alternates between the selected days
                days_count[subject] = len(selected_days)
        
        return days_count
    except Exception as e:
        print(f"❌ Error calculating days per subject: {e}")
        # Fallback to old method
        if not schedule_data or 'weekly_schedule' not in schedule_data:
            return {}
        
        days_count = {}
        for day in schedule_data['weekly_schedule']:
            for subject in day['subjects']:
                if subject not in days_count:
                    days_count[subject] = 0
                days_count[subject] += 1
        
        return days_count

def get_weekly_schedule():
    """Get weekly schedule from global repository - shows the PATTERN, not actual delivery prediction"""
    try:
        from user_repository import GlobalRepository
        from multi_user_database import MultiUserDatabase
        from datetime import datetime, timedelta
        
        db = MultiUserDatabase()
        global_repo = GlobalRepository(db)
        
        config = global_repo.get_global_config()
        if not config:
            return None
        
        # Debug: Print the actual schedule time from database
        print(f"📊 DEBUG: schedule_time from DB = '{config.schedule_time}' (type: {type(config.schedule_time)})")
        
        # Get all playlist schedules from database (not hardcoded)
        playlist_schedules = global_repo.get_all_global_playlist_schedules()
        
        # Build weekly schedule - show PATTERN not actual delivery
        weekly_schedule = []
        today = datetime.now().date()
        
        for day_offset in range(7):
            date = today + timedelta(days=day_offset)
            python_weekday = date.weekday()  # 0=Monday, 6=Sunday
            # Convert Python weekday to calendar weekday (0=Sunday, 6=Saturday)
            weekday = (python_weekday + 1) % 7
            day_name = date.strftime("%A")
            
            subjects_for_day = []
            
            for subject, schedule in playlist_schedules.items():
                start_date = datetime.strptime(schedule['start_date'], "%Y-%m-%d").date()
                
                # Skip if before start date
                if date < start_date:
                    continue
                
                # Check if this weekday is in the schedule
                if weekday not in schedule['selected_days']:
                    continue
                
                # For weekly schedule display, show all subjects on their configured days
                # regardless of last_sent_date (that's for actual delivery logic)
                subjects_for_day.append(subject)
            
            weekly_schedule.append({
                "day_name": day_name,
                "subjects": subjects_for_day,
                "is_today": day_offset == 0
            })
        
        return {
            "schedule_time": format_time_to_12hr(config.schedule_time),
            "schedule_time_24hr": config.schedule_time if isinstance(config.schedule_time, str) else config.schedule_time.strftime("%H:%M"),
            "current_day": config.current_day,
            "weekly_schedule": weekly_schedule
        }
    except Exception as e:
        print(f"❌ Error getting schedule: {e}")
        import traceback
        traceback.print_exc()
        return None

def format_time_to_12hr(time_str):
    """Convert 24-hour time string to 12-hour format with AM/PM"""
    from datetime import datetime
    try:
        if isinstance(time_str, str):
            time_obj = datetime.strptime(time_str, "%H:%M")
            return time_obj.strftime("%I:%M %p")
        elif hasattr(time_str, 'strftime'):
            return time_str.strftime("%I:%M %p")
        else:
            return str(time_str)
    except Exception as e:
        print(f"❌ Error formatting time {time_str}: {e}")
        return str(time_str)
        print(f"❌ Error getting schedule: {e}")
        return None

def handle_schedule_command(bot_token, chat_id):
    """Handle /schedule command - show weekly schedule"""
    schedule_data = get_weekly_schedule()
    
    if not schedule_data:
        send_message(bot_token, chat_id, "❌ Unable to fetch schedule. Please try again later.")
        return
    
    emoji_map = {
        'english': '🗣️',
        'history': '🏛️',
        'polity': '⚖️',
        'geography': '🌍',
        'economics': '💰'
    }
    
    msg = "📅 YOUR WEEKLY STUDY SCHEDULE\n"
    msg += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    for day in schedule_data['weekly_schedule']:
        day_marker = " (Today)" if day['is_today'] else ""
        msg += f"📆 {day['day_name'].upper()}{day_marker}\n"
        
        if day['subjects']:
            for subject in day['subjects']:
                emoji = emoji_map.get(subject, '📚')
                msg += f"{emoji} {subject.capitalize()}\n"
        else:
            msg += "⏭️ No subjects scheduled\n"
        
        msg += "\n"
    
    msg += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    msg += f"⏰ Daily send time: {schedule_data['schedule_time']}\n"
    msg += f"📍 You are on Day {schedule_data['current_day']}\n\n"
    msg += "💡 Tip: Complete your daily tasks to build your streak! 🔥"
    
    send_message(bot_token, chat_id, msg)

def handle_today_command(bot_token, chat_id):
    """Handle /today command - show today's schedule"""
    schedule_data = get_weekly_schedule()
    
    if not schedule_data:
        send_message(bot_token, chat_id, "❌ Unable to fetch schedule. Please try again later.")
        return
    
    emoji_map = {
        'english': '🗣️',
        'history': '🏛️',
        'polity': '⚖️',
        'geography': '🌍',
        'economics': '💰'
    }
    
    today = schedule_data['weekly_schedule'][0]
    
    msg = f"📅 TODAY'S SCHEDULE ({today['day_name']})\n"
    msg += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    if today['subjects']:
        for subject in today['subjects']:
            emoji = emoji_map.get(subject, '📚')
            msg += f"{emoji} {subject.capitalize()}\n"
        
        msg += f"\n⏰ Will be sent at {schedule_data['schedule_time']}\n\n"
        msg += "✅ Mark as Done when completed!"
    else:
        msg += "⏭️ No subjects scheduled for today\n\n"
        msg += "Enjoy your rest day! 😊"
    
    send_message(bot_token, chat_id, msg)

def handle_tomorrow_command(bot_token, chat_id):
    """Handle /tomorrow command - show tomorrow's schedule"""
    schedule_data = get_weekly_schedule()
    
    if not schedule_data:
        send_message(bot_token, chat_id, "❌ Unable to fetch schedule. Please try again later.")
        return
    
    emoji_map = {
        'english': '🗣️',
        'history': '🏛️',
        'polity': '⚖️',
        'geography': '🌍',
        'economics': '💰'
    }
    
    tomorrow = schedule_data['weekly_schedule'][1]
    
    msg = f"📅 TOMORROW'S SCHEDULE ({tomorrow['day_name']})\n"
    msg += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    if tomorrow['subjects']:
        for subject in tomorrow['subjects']:
            emoji = emoji_map.get(subject, '📚')
            msg += f"{emoji} {subject.capitalize()}\n"
        
        msg += f"\n⏰ Will be sent at {schedule_data['schedule_time']}"
    else:
        msg += "⏭️ No subjects scheduled for tomorrow"
    
    send_message(bot_token, chat_id, msg)

def handle_text_message(bot_token, chat_id, text, user_info):
    """Handle regular text messages with AI"""
    first_name = user_info.get("first_name", "User")
    
    print(f"💬 Message from {first_name} ({chat_id}): {text[:50]}...")
    
    # Show typing indicator
    send_typing_action(bot_token, chat_id)
    
    # Get AI response with user context
    response = get_ai_response_with_context(text, chat_id, user_name=first_name)
    
    if response:
        send_message(bot_token, chat_id, response)
        print(f"✅ AI response sent to {first_name}")
    else:
        error_msg = "❌ Sorry, I couldn't process your message. Please try again."
        send_message(bot_token, chat_id, error_msg)

def get_updates(bot_token, offset=0, timeout=10):
    """Get updates from Telegram"""
    url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
    params = {
        "offset": offset,
        "timeout": timeout,
        "allowed_updates": ["message", "callback_query"]
    }
    try:
        response = requests.get(url, params=params, timeout=timeout + 5)
        return response.json()
    except Exception as e:
        print(f"❌ Error getting updates: {e}")
        return None

def main():
    """Start the bot in polling mode"""
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    
    if not bot_token:
        print("❌ TELEGRAM_BOT_TOKEN not found in .env file!")
        return
    
    print("🤖 Starting Telegram Bot (Polling Mode)")
    print("="*60)
    print("Bot will listen for /start commands")
    print("Press Ctrl+C to stop")
    print("="*60)
    print("\n✅ Bot is running...\n")
    
    offset = 0
    
    try:
        while True:
            # Get updates
            result = get_updates(bot_token, offset)
            
            if not result or not result.get("ok"):
                time.sleep(1)
                continue
            
            updates = result.get("result", [])
            
            for update in updates:
                # Update offset
                offset = update["update_id"] + 1
                
                # Handle messages
                if "message" in update:
                    message = update["message"]
                    chat_id = message["chat"]["id"]
                    text = message.get("text", "")
                    user_info = message.get("from", {})
                    
                    if text.startswith("/start"):
                        print(f"📨 Received /start from {user_info.get('first_name')} ({chat_id})")
                        handle_start_command(bot_token, chat_id, user_info)
                    
                    elif text.startswith("/help"):
                        print(f"📨 Received /help from {user_info.get('first_name')} ({chat_id})")
                        handle_help_command(bot_token, chat_id)
                    
                    elif text.startswith("/schedule"):
                        print(f"📨 Received /schedule from {user_info.get('first_name')} ({chat_id})")
                        handle_schedule_command(bot_token, chat_id)
                    
                    elif text.startswith("/today"):
                        print(f"📨 Received /today from {user_info.get('first_name')} ({chat_id})")
                        handle_today_command(bot_token, chat_id)
                    
                    elif text.startswith("/tomorrow"):
                        print(f"📨 Received /tomorrow from {user_info.get('first_name')} ({chat_id})")
                        handle_tomorrow_command(bot_token, chat_id)
                    
                    elif text and not text.startswith("/"):
                        # Handle regular text messages with AI
                        print(f"💬 Message from {user_info.get('first_name')} ({chat_id}): {text[:50]}...")
                        handle_text_message(bot_token, chat_id, text, user_info)
                
                # Handle callback queries (button clicks)
                elif "callback_query" in update:
                    callback_query = update["callback_query"]
                    callback_id = callback_query["id"]
                    chat_id = callback_query.get("message", {}).get("chat", {}).get("id")
                    user_info = callback_query.get("from", {})
                    data = callback_query.get("data", "")
                    
                    print(f"🔘 Button click from {user_info.get('first_name')} ({chat_id}): {data}")
                    
                    # IMMEDIATELY answer callback to remove loading state
                    try:
                        url = f"https://api.telegram.org/bot{bot_token}/answerCallbackQuery"
                        requests.post(url, json={"callback_query_id": callback_id}, timeout=1)
                        print(f"✅ Callback answered immediately")
                    except Exception as e:
                        print(f"❌ Failed to answer callback: {e}")
                    
                    # Parse callback data and process
                    try:
                        import json
                        callback_data = json.loads(data)
                        action = callback_data.get("action")
                        day = callback_data.get("day")
                        status = callback_data.get("status")
                        
                        print(f"   Action: {action}, Day: {day}, Status: {status}")
                        
                        if action == "complete" and day and status:
                            # Get user from database
                            user = user_repo.get_user_by_chat_id(str(chat_id))
                            if user:
                                print(f"   User found: {user.first_name} (ID: {user.id})")
                                
                                # Update log status
                                from streak_calculator import StreakCalculator
                                streak_calc = StreakCalculator()
                                
                                success = user_repo.update_user_log_status(user.id, day, status)
                                print(f"   Update status: {success}")
                                
                                if success:
                                    # Recalculate streak
                                    logs = user_repo.get_user_logs(user.id)
                                    config = user_repo.get_user_config(user.id)
                                    new_streak = streak_calc.calculate_streak(logs)
                                    config.streak = new_streak
                                    user_repo.update_user_config(config)
                                    
                                    print(f"   New streak: {new_streak}")
                                    
                                    # Send confirmation message
                                    if status == "DONE":
                                        if new_streak == 1:
                                            motivation = "🎉 Great start! First day completed!"
                                        elif new_streak < 7:
                                            motivation = f"💪 {new_streak} days strong! Keep the momentum!"
                                        elif new_streak < 14:
                                            motivation = f"🔥 {new_streak} day streak! You're on fire!"
                                        elif new_streak < 30:
                                            motivation = f"⭐ {new_streak} days! Consistency is your superpower!"
                                        elif new_streak < 60:
                                            motivation = f"🏆 {new_streak} day streak! Incredible dedication!"
                                        else:
                                            motivation = f"👑 {new_streak} days! You're a legend!"
                                        
                                        confirmation_msg = f"✅ Day {day} Completed!\n\n"
                                        confirmation_msg += f"🔥 Current Streak: {new_streak} days\n\n"
                                        confirmation_msg += motivation
                                    else:
                                        confirmation_msg = f"📝 Day {day} marked as Not Done\n\n"
                                        confirmation_msg += "Don't worry! You can try again tomorrow.\n"
                                        confirmation_msg += "Consistency matters more than perfection! 💪"
                                    
                                    send_message(bot_token, chat_id, confirmation_msg)
                                    print(f"✅ Confirmation sent: Day {day} - {status}")
                                else:
                                    print(f"❌ Failed to update status in database")
                                    send_message(bot_token, chat_id, "❌ Failed to update status. Please try again.")
                            else:
                                print(f"❌ User not found for chat_id: {chat_id}")
                                send_message(bot_token, chat_id, "❌ User not found. Please send /start first.")
                    
                    except json.JSONDecodeError as e:
                        print(f"❌ JSON decode error: {e}")
                    except Exception as e:
                        print(f"❌ Callback processing error: {e}")
                        import traceback
                        traceback.print_exc()
            
            # Small delay to prevent hammering the API
            if not updates:
                time.sleep(0.1)
    
    except KeyboardInterrupt:
        print("\n\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        app_logger.error(f"Bot error: {e}", exc_info=True)

if __name__ == "__main__":
    main()
