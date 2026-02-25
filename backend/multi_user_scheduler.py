#!/usr/bin/env python3
"""Multi-user automated scheduler for daily messages"""

import asyncio
import os
from datetime import datetime, time as dt_time
from dotenv import load_dotenv
from multi_user_database import MultiUserDatabase
from user_repository import UserRepository, UserDailyLog
from video_selector import VideoSelector
from telegram_bot import TelegramBot

load_dotenv()

class MultiUserScheduler:
    """Schedule and send daily messages automatically for all users"""
    
    def __init__(self):
        self.db = MultiUserDatabase()
        self.user_repo = UserRepository(self.db)
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "8765768664:AAFK0cbqSnKFfFoNl2a2kJF0g_mdMnoP348")
        self.bot = TelegramBot(self.bot_token)
        self.video_selector = VideoSelector()
        self.is_running = False
        self.sent_today = set()  # Track which users received message today
    
    async def send_daily_message_to_user(self, user, config):
        """Send daily message to a specific user"""
        try:
            # Check if already sent today
            today = datetime.now().strftime("%Y-%m-%d")
            logs = self.user_repo.get_user_logs(user.id)
            if logs and logs[0].date == today:
                print(f"ℹ️  {user.first_name} already received today's message")
                return False
            
            # Increment day count
            config.day_count += 1
            current_day = config.day_count
            
            # Select videos
            english_num, english_url = self.video_selector.select_next_english(
                config.english_index, config.english_playlist
            )
            config.english_index = english_num
            
            subject_indices = {
                "History": config.history_index,
                "Polity": config.polity_index,
                "Geography": config.geography_index,
                "Economics": config.economics_index
            }
            playlists = {
                "History": config.history_playlist,
                "Polity": config.polity_playlist,
                "Geography": config.geography_playlist,
                "Economics": config.economics_playlist
            }
            
            gk_subject, gk_num, gk_url = self.video_selector.select_next_gk(
                config.gk_rotation_index, subject_indices, playlists
            )
            
            # Update indices
            if gk_subject == "History":
                config.history_index = gk_num
            elif gk_subject == "Polity":
                config.polity_index = gk_num
            elif gk_subject == "Geography":
                config.geography_index = gk_num
            elif gk_subject == "Economics":
                config.economics_index = gk_num
            
            config.gk_rotation_index = self.video_selector.advance_rotation(config.gk_rotation_index)
            
            # Send message
            await self.bot.send_daily_message(
                user.chat_id, current_day, english_url, gk_subject, gk_url
            )
            
            # Create log
            log = UserDailyLog(
                user_id=user.id,
                day_number=current_day,
                date=today,
                english_video_number=english_num,
                gk_subject=gk_subject,
                gk_video_number=gk_num,
                status="PENDING"
            )
            self.user_repo.insert_user_log(log)
            self.user_repo.update_user_config(config)
            self.user_repo.update_last_active(user.id)
            
            print(f"✅ Day {current_day} sent to {user.first_name} ({user.chat_id})")
            return True
            
        except Exception as e:
            print(f"❌ Error sending to {user.first_name}: {e}")
            return False
    
    async def check_and_send(self):
        """Check all users and send messages if scheduled"""
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        current_date = now.strftime("%Y-%m-%d")
        
        # Get all users
        users = self.user_repo.get_all_users()
        
        if not users:
            return
        
        for user in users:
            # Skip if already sent today
            cache_key = f"{user.id}_{current_date}"
            if cache_key in self.sent_today:
                continue
            
            # Get user config
            config = self.user_repo.get_user_config(user.id)
            if not config:
                continue
            
            # Check if schedule is enabled
            if not config.schedule_enabled:
                continue
            
            # Check if it's time to send
            if config.schedule_time == current_time:
                print(f"\n📤 Sending scheduled message to {user.first_name}...")
                success = await self.send_daily_message_to_user(user, config)
                if success:
                    self.sent_today.add(cache_key)
    
    async def run_scheduler(self):
        """Run scheduler - checks every minute"""
        print("🤖 Multi-User Scheduler Started")
        print("=" * 60)
        print("Checking for scheduled messages every minute...")
        print("Press Ctrl+C to stop")
        print("=" * 60)
        
        self.is_running = True
        
        while self.is_running:
            try:
                await self.check_and_send()
                
                # Clear sent_today cache at midnight
                now = datetime.now()
                if now.hour == 0 and now.minute == 0:
                    self.sent_today.clear()
                    print("\n🔄 New day - cache cleared")
                
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
