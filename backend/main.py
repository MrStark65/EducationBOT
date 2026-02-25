from fastapi import FastAPI, HTTPException, Body, Query
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from datetime import datetime

from multi_user_database import MultiUserDatabase
from user_repository import UserRepository, UserConfig, UserDailyLog
from video_selector import VideoSelector
from streak_calculator import StreakCalculator
from completion_calculator import CompletionCalculator
from telegram_bot import TelegramBot

# Request models
class PlaylistUpdate(BaseModel):
    subject: str
    url: str

class ScheduleConfig(BaseModel):
    enabled: bool
    time: str  # Format: "HH:MM"

# Load environment variables
load_dotenv()

# Global instances
db = None
user_repo = None
bot = None
video_selector = None
streak_calc = None
completion_calc = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize on startup"""
    global db, user_repo, bot, video_selector, streak_calc, completion_calc
    
    # Initialize multi-user database
    db = MultiUserDatabase()
    user_repo = UserRepository(db)
    
    # Initialize bot
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "8765768664:AAFK0cbqSnKFfFoNl2a2kJF0g_mdMnoP348")
    bot = TelegramBot(bot_token)
    
    # Initialize calculators
    video_selector = VideoSelector()
    streak_calc = StreakCalculator()
    completion_calc = CompletionCalculator()
    
    print("✅ Multi-user system initialized")
    
    yield
    
    # Cleanup on shutdown
    pass


app = FastAPI(title="Officer Priya CDS System", lifespan=lifespan)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Officer Priya CDS System API"}


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


@app.post("/api/send-daily")
async def send_daily(chat_id: str = Query(..., description="User's Telegram chat ID")):
    """Execute daily video delivery workflow for a specific user"""
    try:
        # Get user by chat ID
        user = user_repo.get_user_by_chat_id(chat_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found. Please send /start to the bot first.")
        
        # Load user config
        config = user_repo.get_user_config(user.id)
        if not config:
            raise HTTPException(status_code=500, detail="User configuration not found")
        
        # Increment day count
        config.day_count += 1
        current_day = config.day_count
        
        # Select next English video
        english_num, english_url = video_selector.select_next_english(
            config.english_index,
            config.english_playlist
        )
        config.english_index = english_num
        
        # Select next GK video
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
        
        gk_subject, gk_num, gk_url = video_selector.select_next_gk(
            config.gk_rotation_index,
            subject_indices,
            playlists
        )
        
        # Update subject index
        if gk_subject == "History":
            config.history_index = gk_num
        elif gk_subject == "Polity":
            config.polity_index = gk_num
        elif gk_subject == "Geography":
            config.geography_index = gk_num
        elif gk_subject == "Economics":
            config.economics_index = gk_num
        
        # Advance GK rotation
        config.gk_rotation_index = video_selector.advance_rotation(config.gk_rotation_index)
        
        # Send Telegram message
        await bot.send_daily_message(
            chat_id,
            current_day,
            english_url,
            gk_subject,
            gk_url
        )
        
        # Create daily log entry
        log = UserDailyLog(
            user_id=user.id,
            day_number=current_day,
            date=datetime.now().strftime("%Y-%m-%d"),
            english_video_number=english_num,
            gk_subject=gk_subject,
            gk_video_number=gk_num,
            status="PENDING"
        )
        user_repo.insert_user_log(log)
        
        # Update config in database
        user_repo.update_user_config(config)
        
        # Update last active
        user_repo.update_last_active(user.id)
        
        return {
            "success": True,
            "user_id": user.id,
            "day": current_day,
            "english_video": english_num,
            "gk_subject": gk_subject,
            "gk_video": gk_num
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/telegram/webhook")
async def telegram_webhook(update: dict):
    """Handle Telegram button click callbacks"""
    try:
        # Extract callback query
        callback_query = update.get("callback_query")
        if not callback_query:
            return {"ok": True}
        
        callback_query_id = callback_query.get("id")
        user_id = callback_query.get("user_id")  # Added by bot_simple.py
        
        # Parse callback data
        callback_data = bot.handle_callback(callback_query)
        day = callback_data.get("day")
        status = callback_data.get("status")
        
        if not day or not status:
            if callback_query_id:
                await bot.answer_callback(callback_query_id, "Invalid data")
            return {"ok": False, "error": "Invalid callback data"}
        
        if not user_id:
            if callback_query_id:
                await bot.answer_callback(callback_query_id, "User not found")
            return {"ok": False, "error": "User ID not provided"}
        
        # Update log status for this user
        success = user_repo.update_user_log_status(user_id, day, status)
        if not success:
            if callback_query_id:
                await bot.answer_callback(callback_query_id, "Failed to update")
            return {"ok": False, "error": "Failed to update status"}
        
        # Recalculate streak for this user
        logs = user_repo.get_user_logs(user_id)
        config = user_repo.get_user_config(user_id)
        
        # Calculate streak using logs directly (UserDailyLog has is_completed() method)
        new_streak = streak_calc.calculate_streak(logs)
        config.streak = new_streak
        user_repo.update_user_config(config)
        
        # Answer callback query (removes loading state)
        status_text = "Done ✅" if status == "DONE" else "Not Done ❌"
        if callback_query_id:
            await bot.answer_callback(callback_query_id, f"Day {day} marked as {status_text}")
        
        # Send confirmation message
        chat_id = callback_query.get("message", {}).get("chat", {}).get("id")
        if chat_id:
            confirmation_msg = f"✅ Day {day} marked as {status_text}\n🔥 Current streak: {new_streak} days"
            await bot.send_confirmation(str(chat_id), confirmation_msg)
        
        return {"ok": True, "streak": new_streak}
    
    except Exception as e:
        print(f"Webhook error: {e}")
        # Try to answer callback even on error
        if callback_query and callback_query.get("id"):
            try:
                await bot.answer_callback(callback_query.get("id"), "Error occurred")
            except:
                pass
        return {"ok": False, "error": str(e)}


@app.get("/api/dashboard/metrics")
async def get_metrics(chat_id: str = Query(..., description="User's Telegram chat ID")):
    """Return current day, completion percentages, streak for a specific user"""
    try:
        # Get user
        user = user_repo.get_user_by_chat_id(chat_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        config = user_repo.get_user_config(user.id)
        logs = user_repo.get_user_logs(user.id)
        
        # Calculate completion percentages using the logs directly
        # (UserDailyLog has is_completed() method)
        overall = completion_calc.calculate_overall(logs)
        weekly = completion_calc.calculate_weekly(logs)
        
        completed_count = sum(1 for log in logs if log.is_completed())
        
        return {
            "current_day": config.day_count,
            "overall_completion": overall,
            "weekly_completion": weekly,
            "streak": config.streak,
            "total_days": len(logs),
            "completed_days": completed_count,
            "user_name": user.first_name
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/dashboard/logs")
async def get_logs(chat_id: str = Query(..., description="User's Telegram chat ID"), 
                   limit: int = 50, offset: int = 0):
    """Return paginated daily logs for a specific user"""
    try:
        # Get user
        user = user_repo.get_user_by_chat_id(chat_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        all_logs = user_repo.get_user_logs(user.id)
        total = len(all_logs)
        
        # Apply pagination
        paginated_logs = all_logs[offset:offset + limit]
        
        # Convert to dict
        logs_data = []
        for log in paginated_logs:
            logs_data.append({
                "id": log.id,
                "day_number": log.day_number,
                "date": log.date,
                "english_video_number": log.english_video_number,
                "gk_subject": log.gk_subject,
                "gk_video_number": log.gk_video_number,
                "status": log.status,
                "created_at": str(log.created_at) if log.created_at else None,
                "updated_at": str(log.updated_at) if log.updated_at else None
            })
        
        return {
            "logs": logs_data,
            "total": total
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/config/playlists")
async def get_playlists(chat_id: str = Query(..., description="User's Telegram chat ID")):
    """Return all playlist URLs for a specific user"""
    try:
        user = user_repo.get_user_by_chat_id(chat_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        config = user_repo.get_user_config(user.id)
        return {
            "english": config.english_playlist,
            "history": config.history_playlist,
            "polity": config.polity_playlist,
            "geography": config.geography_playlist,
            "economics": config.economics_playlist
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/config/playlists")
async def update_playlist(data: PlaylistUpdate, chat_id: str = Query(..., description="User's Telegram chat ID")):
    """Update playlist URL for a subject for a specific user"""
    try:
        # Validate YouTube playlist URL
        import re
        if not re.search(r'youtube\.com.*list=', data.url):
            raise HTTPException(status_code=400, detail="Invalid YouTube playlist URL")
        
        user = user_repo.get_user_by_chat_id(chat_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        config = user_repo.get_user_config(user.id)
        
        # Update playlist and reset index
        subject_lower = data.subject.lower()
        if subject_lower == "english":
            config.english_playlist = data.url
            config.english_index = 0
        elif subject_lower == "history":
            config.history_playlist = data.url
            config.history_index = 0
        elif subject_lower == "polity":
            config.polity_playlist = data.url
            config.polity_index = 0
        elif subject_lower == "geography":
            config.geography_playlist = data.url
            config.geography_index = 0
        elif subject_lower == "economics":
            config.economics_playlist = data.url
            config.economics_index = 0
        else:
            raise HTTPException(status_code=400, detail="Invalid subject")
        
        user_repo.update_user_config(config)
        return {"success": True}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/admin/reset")
async def reset_progress(chat_id: str = Query(..., description="User's Telegram chat ID")):
    """Reset all progress for a specific user"""
    try:
        user = user_repo.get_user_by_chat_id(chat_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        config = user_repo.get_user_config(user.id)
        
        # Reset all indices and counters
        config.english_index = 0
        config.history_index = 0
        config.polity_index = 0
        config.geography_index = 0
        config.economics_index = 0
        config.gk_rotation_index = 0
        config.day_count = 0
        config.streak = 0
        
        # Clear all logs for this user
        user_repo.clear_user_logs(user.id)
        
        # Update config
        user_repo.update_user_config(config)
        
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/admin/send-now")
async def send_now(chat_id: str = Query(..., description="User's Telegram chat ID")):
    """Manually trigger daily send for a specific user"""
    try:
        user = user_repo.get_user_by_chat_id(chat_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check if already sent today
        logs = user_repo.get_user_logs(user.id)
        
        today = datetime.now().strftime("%Y-%m-%d")
        if logs and logs[0].date == today:
            raise HTTPException(status_code=400, detail="Already sent today")
        
        # Call send_daily endpoint
        result = await send_daily(chat_id=chat_id)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.get("/api/config/schedule")
async def get_schedule(chat_id: str = Query(..., description="User's Telegram chat ID")):
    """Get schedule configuration for a specific user"""
    try:
        user = user_repo.get_user_by_chat_id(chat_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        config = user_repo.get_user_config(user.id)
        return {
            "enabled": config.schedule_enabled,
            "time": config.schedule_time
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/config/schedule")
async def update_schedule(schedule: ScheduleConfig, chat_id: str = Query(..., description="User's Telegram chat ID")):
    """Update schedule configuration for a specific user"""
    try:
        # Validate time format
        import re
        if not re.match(r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$', schedule.time):
            raise HTTPException(status_code=400, detail="Invalid time format. Use HH:MM")
        
        user = user_repo.get_user_by_chat_id(chat_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        config = user_repo.get_user_config(user.id)
        config.schedule_enabled = schedule.enabled
        config.schedule_time = schedule.time
        
        user_repo.update_user_config(config)
        
        return {
            "success": True,
            "enabled": schedule.enabled,
            "time": schedule.time
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/admin/users")
async def get_all_users():
    """Get all registered users (admin endpoint)"""
    try:
        users = user_repo.get_all_users()
        
        users_data = []
        for user in users:
            config = user_repo.get_user_config(user.id)
            logs = user_repo.get_user_logs(user.id)
            
            users_data.append({
                "id": user.id,
                "chat_id": user.chat_id,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "is_active": user.is_active,
                "created_at": str(user.created_at) if user.created_at else None,
                "last_active": str(user.last_active) if user.last_active else None,
                "day_count": config.day_count if config else 0,
                "streak": config.streak if config else 0,
                "total_logs": len(logs)
            })
        
        return {"users": users_data, "total": len(users_data)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
