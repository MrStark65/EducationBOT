#!/usr/bin/env python3
"""
File Scheduler Service
Checks for scheduled files and sends them at the scheduled time
"""

import asyncio
import sqlite3
from datetime import datetime
from pathlib import Path
from telegram_bot import TelegramBot
from file_manager import FileManager
from user_repository import UserRepository
from multi_user_database import MultiUserDatabase
from logger import app_logger
import os
from dotenv import load_dotenv

load_dotenv()

class FileScheduler:
    def __init__(self):
        self.db_path = "officer_priya_multi.db"
        self.file_manager = FileManager(db_path=self.db_path)
        self.db = MultiUserDatabase()
        self.user_repo = UserRepository(self.db)
        
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.bot = TelegramBot(bot_token)
        
    def get_pending_schedules(self):
        """Get all pending scheduled files that are due"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        # First, get ALL scheduled files for debugging
        cursor.execute("SELECT * FROM scheduled_files ORDER BY scheduled_time ASC")
        all_schedules = [dict(row) for row in cursor.fetchall()]
        
        if all_schedules:
            print(f"\n📋 ALL SCHEDULED FILES (Current time: {now}):")
            for s in all_schedules:
                print(f"   ID: {s['id']}, Time: {s['scheduled_time']}, Status: {s['status']}")
        
        # Now get pending schedules
        cursor.execute("""
            SELECT * FROM scheduled_files
            WHERE status = 'pending'
            AND scheduled_time <= ?
            ORDER BY scheduled_time ASC
        """, (now,))
        
        schedules = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return schedules
    
    def mark_as_sent(self, schedule_id: int):
        """Mark a schedule as sent"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE scheduled_files
            SET status = 'sent'
            WHERE id = ?
        """, (schedule_id,))
        
        conn.commit()
        conn.close()
    
    def mark_as_failed(self, schedule_id: int, error: str):
        """Mark a schedule as failed"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE scheduled_files
            SET status = 'failed'
            WHERE id = ?
        """, (schedule_id,))
        
        conn.commit()
        conn.close()
    
    async def send_scheduled_file(self, schedule):
        """Send a scheduled file to all users"""
        try:
            file_id = schedule['file_id']
            schedule_id = schedule['id']
            
            print(f"\n{'='*60}")
            print(f"📅 SENDING SCHEDULED FILE")
            print(f"   Schedule ID: {schedule_id}")
            print(f"   File ID: {file_id}")
            print(f"   Scheduled Time: {schedule['scheduled_time']}")
            print(f"{'='*60}")
            
            # Get file metadata
            metadata = self.file_manager.get_file_metadata(file_id)
            if not metadata:
                print(f"❌ File not found: {file_id}")
                self.mark_as_failed(schedule_id, "File not found")
                return
            
            print(f"✅ File: {metadata['original_name']} ({metadata['file_size']} bytes)")
            
            # Get file path
            file_path = self.file_manager.get_file_path(file_id)
            if not file_path or not file_path.exists():
                print(f"❌ File not found on disk: {file_path}")
                self.mark_as_failed(schedule_id, "File not found on disk")
                return
            
            # Get all users
            users = self.user_repo.get_all_users()
            if not users:
                print(f"❌ No users found")
                self.mark_as_failed(schedule_id, "No users found")
                return
            
            print(f"📊 Sending to {len(users)} users...")
            
            file_type = metadata['file_type']
            caption = f"📄 {metadata['original_name']}\n⏰ Scheduled delivery"
            
            # Send to all users
            success_count = 0
            for user in users:
                try:
                    print(f"  → Sending to {user.first_name} ({user.chat_id})...")
                    success, error = await self.bot.send_file_with_retry(
                        user.chat_id,
                        str(file_path),
                        caption,
                        file_type,
                        max_retries=2
                    )
                    
                    if success:
                        print(f"  ✅ Sent to {user.first_name}")
                        success_count += 1
                    else:
                        print(f"  ❌ Failed to send to {user.first_name}: {error}")
                except Exception as e:
                    print(f"  ❌ Exception sending to {user.first_name}: {e}")
            
            print(f"\n📊 SEND COMPLETE: {success_count}/{len(users)} users")
            print(f"{'='*60}\n")
            
            # Mark as sent
            self.mark_as_sent(schedule_id)
            app_logger.info(f"Scheduled file {file_id} sent to {success_count}/{len(users)} users")
            
        except Exception as e:
            print(f"❌ Error sending scheduled file: {e}")
            app_logger.error(f"Error sending scheduled file: {e}", exc_info=True)
            self.mark_as_failed(schedule_id, str(e))
    
    async def check_and_send(self):
        """Check for pending schedules and send them"""
        schedules = self.get_pending_schedules()
        
        if schedules:
            print(f"\n📅 Found {len(schedules)} scheduled file(s) to send")
            for schedule in schedules:
                await self.send_scheduled_file(schedule)
        else:
            # Show timestamp every 10 checks (10 minutes)
            if not hasattr(self, '_check_count'):
                self._check_count = 0
            self._check_count += 1
            if self._check_count % 10 == 0:
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"\n⏰ [{now}] No pending schedules")
            else:
                print(".", end="", flush=True)
    
    async def run(self):
        """Main scheduler loop"""
        print("\n" + "="*60)
        print("📅 FILE SCHEDULER STARTED")
        print("="*60)
        print("Checking for scheduled files every minute...")
        print("Press Ctrl+C to stop")
        print("="*60 + "\n")
        
        while True:
            try:
                await self.check_and_send()
                await asyncio.sleep(60)  # Check every minute
            except asyncio.CancelledError:
                print("\n\n🛑 File scheduler stopped")
                break
            except KeyboardInterrupt:
                print("\n\n🛑 Scheduler stopped by user")
                break
            except Exception as e:
                print(f"\n❌ Scheduler error: {e}")
                app_logger.error(f"Scheduler error: {e}", exc_info=True)
                await asyncio.sleep(60)


async def main():
    scheduler = FileScheduler()
    await scheduler.run()


if __name__ == "__main__":
    asyncio.run(main())
