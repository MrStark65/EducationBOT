"""Automated scheduler for daily messages"""

import asyncio
import os
from datetime import datetime, time as dt_time
from dotenv import load_dotenv
from database import Database
from repository import Repository
from models import Config, DailyLog
from video_selector import VideoSelector
from telegram_bot import TelegramBot

load_dotenv()

class DailyScheduler:
    """Schedule and send daily messages automatically"""
    
    def __init__(self):
        self.db = Database("officer_priya.db")
        self.repo = Repository(self.db)
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "8765768664:AAFK0cbqSnKFfFoNl2a2kJF0g_mdMnoP348")
        self.bot = TelegramBot(self.bot_token)
        self.video_selector = VideoSelector()
        self.is_running = False
    
    async def send_daily_message(self):
        """Send daily message"""
        try:
            config = self.repo.get_config()
            if not config:
                print("❌ Configuration not found")
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
                config.chat_id, current_day, english_url, gk_subject, gk_url
            )
            
            # Create log
            log = DailyLog(
                day_number=current_day,
                date=datetime.now().strftime("%Y-%m-%d"),
                english_video_number=english_num,
                gk_subject=gk_subject,
                gk_video_number=gk_num,
                status="PENDING"
            )
            self.repo.insert_log(log)
            self.repo.update_config(config)
            
            print(f"✅ Day {current_day} sent successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Error sending daily message: {e}")
            return False
    
    async def run_scheduler(self, scheduled_time: dt_time):
        """Run scheduler at specified time daily"""
        print(f"🕐 Scheduler started - Will send daily at {scheduled_time.strftime('%H:%M')}")
        self.is_running = True
        
        while self.is_running:
            now = datetime.now()
            target = datetime.combine(now.date(), scheduled_time)
            
            # If target time has passed today, schedule for tomorrow
            if now >= target:
                target = datetime.combine(now.date(), scheduled_time)
                target = target.replace(day=target.day + 1)
            
            # Calculate wait time
            wait_seconds = (target - now).total_seconds()
            
            print(f"⏰ Next send scheduled for: {target.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   Waiting {wait_seconds/3600:.1f} hours...")
            
            # Wait until scheduled time
            await asyncio.sleep(wait_seconds)
            
            # Send message
            print(f"\n📤 Sending daily message...")
            await self.send_daily_message()
            
            # Wait a bit to avoid duplicate sends
            await asyncio.sleep(60)
    
    def stop(self):
        """Stop the scheduler"""
        self.is_running = False
        print("🛑 Scheduler stopped")

async def main():
    """Main entry point"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python scheduler.py HH:MM")
        print("Example: python scheduler.py 06:00")
        return
    
    try:
        time_str = sys.argv[1]
        hour, minute = map(int, time_str.split(':'))
        scheduled_time = dt_time(hour=hour, minute=minute)
        
        scheduler = DailyScheduler()
        await scheduler.run_scheduler(scheduled_time)
        
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping scheduler...")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
