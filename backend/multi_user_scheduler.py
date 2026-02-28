#!/usr/bin/env python3
"""Multi-user automated scheduler for daily messages - GLOBAL MODE"""

import asyncio
import os
from datetime import datetime, time as dt_time, timedelta
from dotenv import load_dotenv
from multi_user_database import MultiUserDatabase
from user_repository import UserRepository, GlobalRepository, UserDailyLog
from video_selector import VideoSelector
from telegram_bot import TelegramBot
import pytz

load_dotenv()

# Set timezone to Indian Standard Time
IST = pytz.timezone('Asia/Kolkata')

class MultiUserScheduler:
    """Schedule and send daily messages automatically - ALL users get SAME content"""
    
    def __init__(self):
        self.db = MultiUserDatabase()
        self.user_repo = UserRepository(self.db)
        self.global_repo = GlobalRepository(self.db)
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "8765768664:AAFK0cbqSnKFfFoNl2a2kJF0g_mdMnoP348")
        self.bot = TelegramBot(self.bot_token)
        self.video_selector = VideoSelector()
        self.is_running = False
        self.sent_today = False  # Track if we sent today (global)
    
    def should_send_playlist_today(self, subject: str, today_date: str, today_weekday: int) -> bool:
        """Check if a playlist should be sent today based on GLOBAL schedule"""
        schedule = self.global_repo.get_global_playlist_schedule(subject)
        
        # If no schedule set, DON'T send (must be explicitly scheduled)
        if not schedule:
            print(f"  ⏭️  {subject.capitalize()}: No schedule found, skipping")
            return False
        
        print(f"  ✓ {subject.capitalize()}: Schedule found - {schedule}")
        
        # Check if today is after or equal to start date
        start_date = datetime.strptime(schedule['start_date'], "%Y-%m-%d").date()
        today = datetime.strptime(today_date, "%Y-%m-%d").date()
        
        if today < start_date:
            print(f"  ⏭️  {subject.capitalize()}: Before start date")
            return False
        
        # Check if today's weekday is in selected days
        selected_days = schedule['selected_days']
        if today_weekday not in selected_days:
            print(f"  ⏭️  {subject.capitalize()}: Today ({today_weekday}) not in selected days {selected_days}")
            return False
        
        # Check frequency (daily or alternate)
        if schedule['frequency'] == 'daily':
            print(f"  ✅ {subject.capitalize()}: Sending (daily)")
            return True
        elif schedule['frequency'] == 'alternate':
            last_sent = schedule.get('last_sent_date')
            if not last_sent:
                print(f"  ✅ {subject.capitalize()}: Sending (first time)")
                return True  # First time, send it
            
            last_sent_date = datetime.strptime(last_sent, "%Y-%m-%d").date()
            
            # Count how many selected days have passed since last send
            days_passed = 0
            check_date = last_sent_date + timedelta(days=1)
            while check_date <= today:
                if check_date.weekday() in selected_days:
                    days_passed += 1
                check_date += timedelta(days=1)
            
            # Send if at least 2 selected days have passed
            should_send = days_passed >= 2
            print(f"  {'✅' if should_send else '⏭️'}  {subject.capitalize()}: {days_passed} days passed since last send")
            return should_send
        
        return True
    
    async def send_daily_message_to_all_users(self):
        """Send SAME content to ALL users"""
        try:
            today = datetime.now(IST).strftime("%Y-%m-%d")
            today_weekday = datetime.now(IST).weekday()  # 0=Monday, 6=Sunday
            
            # Get global config
            config = self.global_repo.get_global_config()
            if not config:
                print("❌ No global config found")
                return False
            
            # Collect all playlists scheduled for today
            playlists_to_send = []
            
            # Check English
            if self.should_send_playlist_today('english', today, today_weekday):
                english_num, english_url = self.video_selector.select_next_english(
                    config.english_index, config.english_playlist
                )
                playlists_to_send.append({
                    'subject': 'English',
                    'number': english_num,
                    'url': english_url,
                    'update_field': 'english_index'
                })
                config.english_index = english_num
            
            # Check History
            if self.should_send_playlist_today('history', today, today_weekday):
                history_num, history_url = self.video_selector.select_next_english(
                    config.history_index, config.history_playlist
                )
                playlists_to_send.append({
                    'subject': 'History',
                    'number': history_num,
                    'url': history_url,
                    'update_field': 'history_index'
                })
                config.history_index = history_num
            
            # Check Polity
            if self.should_send_playlist_today('polity', today, today_weekday):
                polity_num, polity_url = self.video_selector.select_next_english(
                    config.polity_index, config.polity_playlist
                )
                playlists_to_send.append({
                    'subject': 'Polity',
                    'number': polity_num,
                    'url': polity_url,
                    'update_field': 'polity_index'
                })
                config.polity_index = polity_num
            
            # Check Geography
            if self.should_send_playlist_today('geography', today, today_weekday):
                geography_num, geography_url = self.video_selector.select_next_english(
                    config.geography_index, config.geography_playlist
                )
                playlists_to_send.append({
                    'subject': 'Geography',
                    'number': geography_num,
                    'url': geography_url,
                    'update_field': 'geography_index'
                })
                config.geography_index = geography_num
            
            # Check Economics
            if self.should_send_playlist_today('economics', today, today_weekday):
                economics_num, economics_url = self.video_selector.select_next_english(
                    config.economics_index, config.economics_playlist
                )
                playlists_to_send.append({
                    'subject': 'Economics',
                    'number': economics_num,
                    'url': economics_url,
                    'update_field': 'economics_index'
                })
                config.economics_index = economics_num
            
            # If no playlists scheduled for today, skip
            if not playlists_to_send:
                print(f"⏭️  No playlists scheduled for today")
                return False
            
            # Increment global day count
            config.current_day += 1
            current_day = config.current_day
            
            # Build enhanced message with all scheduled playlists
            message = f"🎯 Day {current_day} - CDS Preparation\n"
            message += "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            message += "📚 Today's Study Materials:\n\n"
            
            for i, playlist in enumerate(playlists_to_send, 1):
                emoji = {
                    'English': '🗣️',
                    'History': '🏛️',
                    'Polity': '⚖️',
                    'Geography': '🌍',
                    'Economics': '💰'
                }.get(playlist['subject'], '📚')
                
                message += f"{i}. {emoji} {playlist['subject']} (Video #{playlist['number']})\n"
                message += f"   {playlist['url']}\n\n"
                
                # Update last sent date for this playlist
                self.global_repo.update_global_playlist_last_sent(playlist['subject'].lower(), today)
            
            message += "━━━━━━━━━━━━━━━━━━━━━━\n"
            message += "💡 Action Required:\n"
            message += "✅ Click Done when you complete today's study\n"
            message += "❌ Click Not Done if you need more time\n\n"
            message += "💪 Stay consistent, stay focused!"
            
            # Update global config
            self.global_repo.update_global_config(config)
            
            # Send to ALL users
            users = self.user_repo.get_all_users()
            success_count = 0
            
            for user in users:
                try:
                    await self.bot.send_daily_message_with_buttons(user.chat_id, current_day, message)
                    
                    # Create log for this user
                    first_playlist = playlists_to_send[0]
                    log = UserDailyLog(
                        user_id=user.id,
                        day_number=current_day,
                        date=today,
                        english_video_number=first_playlist['number'],
                        gk_subject=first_playlist['subject'],
                        gk_video_number=first_playlist['number'],
                        status="PENDING"
                    )
                    self.user_repo.insert_user_log(log)
                    self.user_repo.update_last_active(user.id)
                    
                    success_count += 1
                    print(f"✅ Sent to {user.first_name} ({user.chat_id})")
                except Exception as e:
                    print(f"❌ Failed to send to {user.first_name}: {e}")
            
            subjects_sent = ', '.join([p['subject'] for p in playlists_to_send])
            print(f"\n📤 Day {current_day} sent to {success_count}/{len(users)} users: {subjects_sent}")
            return True
            
        except Exception as e:
            print(f"❌ Error in send_daily_message_to_all_users: {e}")
            return False
    
    async def check_and_send(self):
        """Check if it's time to send and send to ALL users"""
        now = datetime.now(IST)
        current_time = now.strftime("%H:%M")
        current_date = now.strftime("%Y-%m-%d")
        
        # Check if already sent today
        if self.sent_today:
            return
        
        # Get global config
        config = self.global_repo.get_global_config()
        if not config:
            return
        
        # Check if schedule is enabled
        if not config.schedule_enabled:
            return
        
        # Check if it's time to send
        if config.schedule_time == current_time:
            print(f"\n📤 Sending scheduled message to ALL users...")
            success = await self.send_daily_message_to_all_users()
            if success:
                self.sent_today = True
    
    async def run_scheduler(self):
        """Run scheduler - checks every minute"""
        print("🤖 Global Scheduler Started")
        print("=" * 60)
        print("ALL users receive SAME content on SAME day")
        print("Checking for scheduled messages every minute...")
        print("Press Ctrl+C to stop")
        print("=" * 60)
        
        self.is_running = True
        
        while self.is_running:
            try:
                await self.check_and_send()
                
                # Clear sent_today flag at midnight
                now = datetime.now(IST)
                if now.hour == 0 and now.minute == 0:
                    self.sent_today = False
                    print("\n🔄 New day - ready to send")
                
                # Wait 60 seconds before next check
                await asyncio.sleep(60)
                
            except Exception as e:
                print(f"❌ Scheduler error: {e}")
                await asyncio.sleep(60)
    
    def stop(self):
        """Stop the scheduler"""
        self.is_running = False
        print("\n🛑 Scheduler stopped")

async def main():
    """Main entry point"""
    scheduler = MultiUserScheduler()
    
    try:
        await scheduler.run_scheduler()
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping scheduler...")
        scheduler.stop()
    except Exception as e:
        print(f"❌ Fatal error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
