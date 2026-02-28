from fastapi import FastAPI, HTTPException, Body, Query, Depends, Header, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
from pydantic import BaseModel
import os
import asyncio
from io import BytesIO
from dotenv import load_dotenv
from datetime import datetime, timedelta
from typing import Optional

from multi_user_database import MultiUserDatabase
from user_repository import UserRepository, GlobalRepository, UserConfig, UserDailyLog
from video_selector import VideoSelector
from streak_calculator import StreakCalculator
from completion_calculator import CompletionCalculator
from telegram_bot import TelegramBot
from auth import get_auth_manager
from logger import app_logger, api_logger, get_recent_errors, clear_old_errors
from backup_manager import get_backup_manager
from user_manager import get_user_manager
from input_validator import validator
from rate_limiter import RateLimiter

# Security
security = HTTPBearer()

# Request models
class LoginRequest(BaseModel):
    username: str
    password: str

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

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
global_repo = None
bot = None
video_selector = None
streak_calc = None
completion_calc = None
auth_manager = None
backup_manager = None
file_manager = None
user_manager = None
bot_thread = None  # Thread for running the bot


# Auth dependency
async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token"""
    token = credentials.credentials
    api_logger.debug(f"Verifying token: {token[:20]}...")
    api_logger.debug(f"Using SECRET_KEY: {os.getenv('JWT_SECRET_KEY', 'default')[:10]}...")
    payload = auth_manager.verify_token(token)
    
    if not payload:
        api_logger.warning(f"Token verification failed - invalid or expired token. Token: {token[:30]}...")
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    # Add username to payload for convenience
    payload["username"] = payload.get("sub", "admin")
    api_logger.debug(f"Token verified successfully for: {payload.get('username')}")
    return payload


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize on startup"""
    global db, user_repo, global_repo, bot, video_selector, streak_calc, completion_calc, auth_manager, backup_manager, file_manager, user_manager, bot_thread
    
    app_logger.info("🚀 Starting Officer Priya CDS System")
    
    # Initialize multi-user database
    db = MultiUserDatabase()
    user_repo = UserRepository(db)
    global_repo = GlobalRepository(db)
    
    # Initialize bot
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "8765768664:AAFK0cbqSnKFfFoNl2a2kJF0g_mdMnoP348")
    bot = TelegramBot(bot_token)
    
    # Initialize calculators
    video_selector = VideoSelector()
    streak_calc = StreakCalculator()
    completion_calc = CompletionCalculator()
    
    # Initialize auth manager
    auth_manager = get_auth_manager()
    app_logger.info("✅ Authentication system initialized")
    
    # Initialize backup manager
    backup_manager = get_backup_manager()
    app_logger.info("✅ Backup system initialized")
    
    # Initialize file manager
    from file_manager import FileManager
    file_manager = FileManager(db_path="officer_priya_multi.db")
    app_logger.info("✅ File manager initialized")
    
    # Initialize user manager
    user_manager = get_user_manager(db_path="officer_priya_multi.db")
    app_logger.info("✅ User manager initialized")
    
    # Start Telegram bot in background thread
    import threading
    def run_bot():
        try:
            app_logger.info("🤖 Starting Telegram Bot in background...")
            from bot_polling_simple import main as bot_main
            bot_main()
        except Exception as e:
            app_logger.error(f"❌ Bot error: {e}", exc_info=True)
    
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    app_logger.info("✅ Telegram Bot started in background thread")
    
    # Create initial backup
    try:
        backup_path = backup_manager.auto_backup(compress=True, keep_count=10)
        if backup_path:
            app_logger.info(f"✅ Initial backup created: {backup_path}")
    except Exception as e:
        app_logger.error(f"❌ Initial backup failed: {e}", exc_info=True)
    
    app_logger.info("✅ Multi-user system initialized")
    
    # Start schedulers in background
    scheduler_tasks = []
    
    # Start file scheduler
    try:
        from file_scheduler import FileScheduler
        file_scheduler = FileScheduler()
        file_scheduler_task = asyncio.create_task(file_scheduler.run())
        scheduler_tasks.append(file_scheduler_task)
        app_logger.info("✅ File scheduler started")
    except Exception as e:
        app_logger.error(f"❌ File scheduler failed to start: {e}", exc_info=True)
    
    # Start daily content scheduler
    try:
        from multi_user_scheduler import MultiUserScheduler
        daily_scheduler = MultiUserScheduler()
        daily_scheduler_task = asyncio.create_task(daily_scheduler.run_scheduler())
        scheduler_tasks.append(daily_scheduler_task)
        app_logger.info("✅ Daily content scheduler started")
    except Exception as e:
        app_logger.error(f"❌ Daily content scheduler failed to start: {e}", exc_info=True)
    
    yield
    
    # Cleanup on shutdown
    app_logger.info("🛑 Shutting down Officer Priya CDS System")
    
    # Cancel scheduler tasks
    for task in scheduler_tasks:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
    
    app_logger.info("✅ Schedulers stopped")


app = FastAPI(title="Officer Priya CDS System", lifespan=lifespan)

# Rate limiting middleware
app.add_middleware(RateLimiter, requests_per_minute=60, requests_per_hour=1000)

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


# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

@app.post("/api/auth/login")
async def login(request: LoginRequest):
    """Login and get JWT token"""
    try:
        api_logger.info(f"Login attempt for user: {request.username}")
        
        if not auth_manager.authenticate_user(request.username, request.password):
            api_logger.warning(f"Failed login attempt for user: {request.username}")
            raise HTTPException(status_code=401, detail="Invalid username or password")
        
        # Create access token
        token = auth_manager.create_access_token(
            data={"sub": request.username},
            expires_delta=timedelta(hours=24)
        )
        
        api_logger.info(f"Successful login for user: {request.username}")
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "expires_in": 86400  # 24 hours in seconds
        }
    
    except HTTPException:
        raise
    except Exception as e:
        api_logger.error(f"Login error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Login failed")


@app.post("/api/auth/verify")
async def verify_token_endpoint(payload: dict = Depends(verify_token)):
    """Verify if token is valid"""
    return {
        "valid": True,
        "username": payload.get("sub"),
        "expires": payload.get("exp")
    }


@app.post("/api/auth/change-password")
async def change_password(
    request: ChangePasswordRequest,
    payload: dict = Depends(verify_token)
):
    """Change user password"""
    try:
        username = payload.get("sub")
        
        if not auth_manager.change_password(username, request.old_password, request.new_password):
            raise HTTPException(status_code=400, detail="Invalid old password")
        
        api_logger.info(f"Password changed for user: {username}")
        
        return {"success": True, "message": "Password changed successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        api_logger.error(f"Password change error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Password change failed")


# ============================================================================
# SYSTEM MANAGEMENT ENDPOINTS (Protected)
# ============================================================================

@app.get("/api/system/errors")
async def get_system_errors(
    limit: int = 50,
    payload: dict = Depends(verify_token)
):
    """Get recent system errors"""
    try:
        errors = get_recent_errors(limit=limit)
        return {"errors": errors, "total": len(errors)}
    except Exception as e:
        api_logger.error(f"Failed to fetch errors: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch errors")


@app.delete("/api/system/errors")
async def clear_system_errors(
    days: int = 30,
    payload: dict = Depends(verify_token)
):
    """Clear old system errors"""
    try:
        deleted = clear_old_errors(days=days)
        api_logger.info(f"Cleared {deleted} old errors")
        return {"success": True, "deleted": deleted}
    except Exception as e:
        api_logger.error(f"Failed to clear errors: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to clear errors")


@app.get("/api/system/backups")
async def list_backups(payload: dict = Depends(verify_token)):
    """List all available backups"""
    try:
        backups = backup_manager.list_backups()
        return {"backups": backups, "total": len(backups)}
    except Exception as e:
        api_logger.error(f"Failed to list backups: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to list backups")


@app.post("/api/system/backups")
async def create_backup(
    compress: bool = True,
    payload: dict = Depends(verify_token)
):
    """Create a new backup"""
    try:
        backup_path = backup_manager.create_backup(compress=compress)
        
        if not backup_path:
            raise HTTPException(status_code=500, detail="Backup creation failed")
        
        api_logger.info(f"Backup created: {backup_path}")
        
        return {
            "success": True,
            "backup_path": backup_path,
            "message": "Backup created successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        api_logger.error(f"Backup creation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Backup creation failed")


@app.post("/api/system/backups/restore")
async def restore_backup(
    backup_path: str = Body(..., embed=True),
    payload: dict = Depends(verify_token)
):
    """Restore database from backup"""
    try:
        success = backup_manager.restore_backup(backup_path)
        
        if not success:
            raise HTTPException(status_code=500, detail="Backup restoration failed")
        
        api_logger.info(f"Backup restored: {backup_path}")
        
        return {
            "success": True,
            "message": "Backup restored successfully. Please restart the application."
        }
    except HTTPException:
        raise
    except Exception as e:
        api_logger.error(f"Backup restoration error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Backup restoration failed")


@app.delete("/api/system/backups")
async def delete_backup(
    backup_path: str = Query(...),
    payload: dict = Depends(verify_token)
):
    """Delete a backup"""
    try:
        success = backup_manager.delete_backup(backup_path)
        
        if not success:
            raise HTTPException(status_code=500, detail="Backup deletion failed")
        
        api_logger.info(f"Backup deleted: {backup_path}")
        
        return {"success": True, "message": "Backup deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        api_logger.error(f"Backup deletion error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Backup deletion failed")


@app.get("/api/system/stats")
async def get_system_stats(payload: dict = Depends(verify_token)):
    """Get system statistics"""
    try:
        users = user_repo.get_all_users()
        errors = get_recent_errors(limit=100)
        backups = backup_manager.list_backups()
        
        # Calculate stats
        total_users = len(users)
        active_users = sum(1 for u in users if u.is_active)
        total_errors = len(errors)
        recent_errors = sum(1 for e in errors if e['level'] == 'ERROR')
        total_backups = len(backups)
        
        # Get latest backup info
        latest_backup = backups[0] if backups else None
        
        return {
            "users": {
                "total": total_users,
                "active": active_users,
                "inactive": total_users - active_users
            },
            "errors": {
                "total": total_errors,
                "recent": recent_errors
            },
            "backups": {
                "total": total_backups,
                "latest": latest_backup
            },
            "system": {
                "uptime": "N/A",  # TODO: Track uptime
                "version": "2.0.0"
            }
        }
    except Exception as e:
        api_logger.error(f"Failed to fetch system stats: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch system stats")


# ============================================================================
# EXISTING ENDPOINTS (Keep as is, add logging)
# ============================================================================


@app.post("/api/send-daily")
async def send_daily(chat_id: str = Query(..., description="User's Telegram chat ID")):
    """Execute daily video delivery workflow for a specific user"""
    try:
        api_logger.info(f"Send daily request for chat_id: {chat_id}")
        
        # Get user by chat ID
        user = user_repo.get_user_by_chat_id(chat_id)
        if not user:
            api_logger.warning(f"User not found: {chat_id}")
            raise HTTPException(status_code=404, detail="User not found. Please send /start to the bot first.")
        
        # Load user config
        config = user_repo.get_user_config(user.id)
        if not config:
            api_logger.error(f"User configuration not found for user_id: {user.id}")
            raise HTTPException(status_code=500, detail="User configuration not found")
        
        today = datetime.now().strftime("%Y-%m-%d")
        today_weekday = datetime.now().weekday()
        
        # Collect all playlists scheduled for today
        playlists_to_send = []
        
        # Check English
        english_num, english_url = video_selector.select_next_english(
            config.english_index, config.english_playlist
        )
        playlists_to_send.append({
            'subject': 'English',
            'number': english_num,
            'url': english_url,
            'update_field': 'english_index'
        })
        
        # Check History
        history_num, history_url = video_selector.select_next_english(
            config.history_index, config.history_playlist
        )
        playlists_to_send.append({
            'subject': 'History',
            'number': history_num,
            'url': history_url,
            'update_field': 'history_index'
        })
        
        # Check Polity
        polity_num, polity_url = video_selector.select_next_english(
            config.polity_index, config.polity_playlist
        )
        playlists_to_send.append({
            'subject': 'Polity',
            'number': polity_num,
            'url': polity_url,
            'update_field': 'polity_index'
        })
        
        # Check Geography
        geography_num, geography_url = video_selector.select_next_english(
            config.geography_index, config.geography_playlist
        )
        playlists_to_send.append({
            'subject': 'Geography',
            'number': geography_num,
            'url': geography_url,
            'update_field': 'geography_index'
        })
        
        # Check Economics
        economics_num, economics_url = video_selector.select_next_english(
            config.economics_index, config.economics_playlist
        )
        playlists_to_send.append({
            'subject': 'Economics',
            'number': economics_num,
            'url': economics_url,
            'update_field': 'economics_index'
        })
        
        # Increment day count
        config.day_count += 1
        current_day = config.day_count
        
        # Build message with all playlists
        message = f"📚 Day {current_day} - Your Study Materials\n\n"
        
        for playlist in playlists_to_send:
            emoji = {
                'English': '🗣️',
                'History': '🏛️',
                'Polity': '⚖️',
                'Geography': '🌍',
                'Economics': '💰'
            }.get(playlist['subject'], '📚')
            
            message += f"{emoji} {playlist['subject']} #{playlist['number']}\n{playlist['url']}\n\n"
            
            # Update indices
            if playlist['update_field'] == 'english_index':
                config.english_index = playlist['number']
            elif playlist['update_field'] == 'history_index':
                config.history_index = playlist['number']
            elif playlist['update_field'] == 'polity_index':
                config.polity_index = playlist['number']
            elif playlist['update_field'] == 'geography_index':
                config.geography_index = playlist['number']
            elif playlist['update_field'] == 'economics_index':
                config.economics_index = playlist['number']
        
        message += "✅ Mark as DONE when completed\n❌ Mark as NOT DONE if you need more time"
        
        # Send Telegram message
        await bot.send_confirmation(chat_id, message)
        
        # Create daily log entry (store first playlist for compatibility)
        first_playlist = playlists_to_send[0]
        log = UserDailyLog(
            user_id=user.id,
            day_number=current_day,
            date=datetime.now().strftime("%Y-%m-%d"),
            english_video_number=first_playlist['number'],
            gk_subject=first_playlist['subject'],
            gk_video_number=first_playlist['number'],
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
            "playlists_sent": [p['subject'] for p in playlists_to_send]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/telegram/webhook")
async def telegram_webhook(update: dict):
    """Handle Telegram updates (messages and callbacks)"""
    try:
        # Handle regular messages (like /start command)
        message = update.get("message")
        if message:
            chat_id = message.get("chat", {}).get("id")
            text = message.get("text", "")
            user_info = message.get("from", {})
            
            # Handle /start command
            if text.startswith("/start"):
                # Register or update user
                first_name = user_info.get("first_name", "User")
                last_name = user_info.get("last_name", "")
                username = user_info.get("username", "")
                
                # Check if user exists
                existing_user = user_repo.get_user_by_chat_id(str(chat_id))
                
                if not existing_user:
                    # Create new user
                    from user_repository import User
                    new_user = User(
                        chat_id=str(chat_id),
                        first_name=first_name,
                        last_name=last_name,
                        username=username,
                        is_active=True
                    )
                    user_repo.insert_user(new_user)
                    
                    welcome_msg = f"👋 Welcome {first_name}!\n\n"
                    welcome_msg += "🎯 Officer Priya CDS Preparation Bot\n\n"
                    welcome_msg += "You'll receive daily study materials including:\n"
                    welcome_msg += "📚 English videos\n"
                    welcome_msg += "📖 GK content (History, Polity, Geography, Economics)\n"
                    welcome_msg += "📄 Study documents and PDFs\n\n"
                    welcome_msg += "✅ Mark your progress with Done/Not Done buttons\n"
                    welcome_msg += "🔥 Build your study streak!\n\n"
                    welcome_msg += "Ready to start your CDS preparation journey! 💪"
                else:
                    # User already exists
                    welcome_msg = f"👋 Welcome back {first_name}!\n\n"
                    welcome_msg += "You're already registered. You'll continue receiving daily study materials.\n\n"
                    welcome_msg += "Keep up the great work! 🔥"
                
                # Send welcome message
                await bot.send_confirmation(str(chat_id), welcome_msg)
                
                return {"ok": True, "message": "Welcome message sent"}
            
            # Handle other commands or messages
            elif text.startswith("/help"):
                help_msg = "🤖 Officer Priya CDS Bot - Help\n\n"
                help_msg += "Available commands:\n"
                help_msg += "/start - Register and start receiving materials\n"
                help_msg += "/help - Show this help message\n\n"
                help_msg += "You'll receive daily study materials automatically.\n"
                help_msg += "Use the Done/Not Done buttons to track your progress!"
                
                await bot.send_confirmation(str(chat_id), help_msg)
                return {"ok": True, "message": "Help message sent"}
            
            # For other messages, just acknowledge
            return {"ok": True}
        
        # Handle callback queries (button clicks)
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
        
        # Send enhanced confirmation message with motivation
        chat_id = callback_query.get("message", {}).get("chat", {}).get("id")
        if chat_id:
            if status == "DONE":
                # Motivational messages for completion
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
                
                confirmation_msg = f"✅ *Day {day} Completed!*\n\n"
                confirmation_msg += f"🔥 Current Streak: *{new_streak} days*\n\n"
                confirmation_msg += motivation
            else:
                confirmation_msg = f"📝 *Day {day} marked as Not Done*\n\n"
                confirmation_msg += "Don't worry! You can try again tomorrow.\n"
                confirmation_msg += "Consistency matters more than perfection! 💪"
            
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
async def get_playlists(chat_id: str = Query(None, description="User's Telegram chat ID (optional for global mode)")):
    """Return all playlist URLs (GLOBAL - same for all users)"""
    try:
        config = global_repo.get_global_config()
        if not config:
            raise HTTPException(status_code=500, detail="Global configuration not found")
        
        playlists = {
            "english": config.english_playlist,
            "history": config.history_playlist,
            "polity": config.polity_playlist,
            "geography": config.geography_playlist,
            "economics": config.economics_playlist
        }
        
        # Add custom subjects
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT subject_name, playlist_url FROM custom_subjects ORDER BY subject_name")
        custom_subjects = cursor.fetchall()
        conn.close()
        
        for subject_name, playlist_url in custom_subjects:
            playlists[subject_name.lower()] = playlist_url
        
        return playlists
    except HTTPException:
        raise
    except Exception as e:
        api_logger.error(f"Get playlists error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/config/playlists")
async def update_playlist(data: PlaylistUpdate, chat_id: str = Query(None, description="User's Telegram chat ID (optional for global mode)")):
    """Update playlist URL for a subject (GLOBAL - affects all users)"""
    try:
        # Validate YouTube playlist URL
        import re
        if not re.search(r'youtube\.com.*list=', data.url):
            raise HTTPException(status_code=400, detail="Invalid YouTube playlist URL")
        
        subject_lower = data.subject.lower()
        
        # Check if it's a default subject
        default_subjects = ["english", "history", "polity", "geography", "economics"]
        
        if subject_lower in default_subjects:
            # Update default subject in global_config
            config = global_repo.get_global_config()
            if not config:
                raise HTTPException(status_code=500, detail="Global configuration not found")
            
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
            
            global_repo.update_global_config(config)
        else:
            # Handle custom subject
            conn = db.get_connection()
            cursor = conn.cursor()
            
            # Check if custom subject exists
            cursor.execute("SELECT id FROM custom_subjects WHERE LOWER(subject_name) = ?", (subject_lower,))
            existing = cursor.fetchone()
            
            if existing:
                # Update existing custom subject
                cursor.execute("""
                    UPDATE custom_subjects 
                    SET playlist_url = ?, current_index = 0, updated_at = CURRENT_TIMESTAMP
                    WHERE LOWER(subject_name) = ?
                """, (data.url, subject_lower))
            else:
                # Insert new custom subject
                cursor.execute("""
                    INSERT INTO custom_subjects (subject_name, playlist_url, current_index)
                    VALUES (?, ?, 0)
                """, (data.subject, data.url))
            
            conn.commit()
            conn.close()
        
        return {"success": True}
    
    except HTTPException:
        raise
    except Exception as e:
        api_logger.error(f"Update playlist error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/config/playlists/{subject}")
async def delete_custom_playlist(subject: str, chat_id: str = Query(None, description="User's Telegram chat ID (optional for global mode)")):
    """Delete a playlist - clears URL for default subjects, removes custom subjects"""
    try:
        default_subjects = ["english", "history", "polity", "geography", "economics"]
        subject_lower = subject.lower()
        
        if subject_lower in default_subjects:
            # For default subjects, just clear the URL (don't delete from config)
            config = global_repo.get_global_config()
            if not config:
                raise HTTPException(status_code=500, detail="Global configuration not found")
            
            if subject_lower == "english":
                config.english_playlist = ""
            elif subject_lower == "history":
                config.history_playlist = ""
            elif subject_lower == "polity":
                config.polity_playlist = ""
            elif subject_lower == "geography":
                config.geography_playlist = ""
            elif subject_lower == "economics":
                config.economics_playlist = ""
            
            global_repo.update_global_config(config)
            
            # Also delete its schedule if exists
            global_repo.delete_global_playlist_schedule(subject_lower)
            
            api_logger.info(f"Cleared playlist URL for default subject: {subject}")
            return {"success": True, "message": f"Playlist URL cleared for {subject}"}
        else:
            # Delete custom subject completely
            conn = db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM custom_subjects WHERE LOWER(subject_name) = ?", (subject_lower,))
            deleted = cursor.rowcount
            
            # Also delete its schedule if exists
            cursor.execute("DELETE FROM global_playlist_schedules WHERE LOWER(subject_name) = ?", (subject_lower,))
            
            conn.commit()
            conn.close()
            
            if deleted == 0:
                raise HTTPException(status_code=404, detail="Custom subject not found")
            
            api_logger.info(f"Deleted custom subject: {subject}")
            return {"success": True, "message": f"Custom subject {subject} deleted"}
    
    except HTTPException:
        raise
    except Exception as e:
        api_logger.error(f"Delete playlist error: {e}", exc_info=True)
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


@app.post("/api/admin/reset-global")
async def reset_global_progress():
    """Reset global progress (affects ALL users)"""
    try:
        # Get global config
        config = global_repo.get_global_config()
        if not config:
            raise HTTPException(status_code=500, detail="Global configuration not found")
        
        # Reset all global indices and counters
        config.current_day = 0
        config.english_index = 0
        config.history_index = 0
        config.polity_index = 0
        config.geography_index = 0
        config.economics_index = 0
        
        # Update global config
        global_repo.update_global_config(config)
        
        # Clear all user logs AND reset streaks
        users = user_repo.get_all_users()
        for user in users:
            # Clear logs
            user_repo.clear_user_logs(user.id)
            
            # Reset user streak and day count
            user_config = user_repo.get_user_config(user.id)
            if user_config:
                user_config.streak = 0
                user_config.day_count = 0
                user_repo.update_user_config(user_config)
        
        return {"success": True, "message": f"Global progress reset. Cleared logs and streaks for {len(users)} users."}
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
        if logs and len(logs) > 0 and logs[0].date == today:
            raise HTTPException(status_code=400, detail="Already sent today")
        
        # Call send_daily endpoint
        result = await send_daily(chat_id=chat_id)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.get("/api/config/schedule")
async def get_schedule(chat_id: str = Query(None, description="User's Telegram chat ID (optional for global mode)")):
    """Get schedule configuration (GLOBAL - same for all users)"""
    try:
        config = global_repo.get_global_config()
        if not config:
            raise HTTPException(status_code=500, detail="Global configuration not found")
        
        return {
            "enabled": config.schedule_enabled,
            "time": config.schedule_time
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/config/schedule")
async def update_schedule(schedule: ScheduleConfig, chat_id: str = Query(None, description="User's Telegram chat ID (optional for global mode)")):
    """Update schedule configuration (GLOBAL - affects all users)"""
    try:
        # Validate time format
        import re
        if not re.match(r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$', schedule.time):
            raise HTTPException(status_code=400, detail="Invalid time format. Use HH:MM")
        
        config = global_repo.get_global_config()
        if not config:
            raise HTTPException(status_code=500, detail="Global configuration not found")
        
        config.schedule_enabled = schedule.enabled
        config.schedule_time = schedule.time
        
        global_repo.update_global_config(config)
        
        return {
            "success": True,
            "enabled": schedule.enabled,
            "time": schedule.time
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/config/schedule-summary")
async def get_schedule_summary(payload: dict = Depends(verify_token)):
    """Get weekly schedule summary showing what sends on each day"""
    try:
        from datetime import datetime, timedelta
        
        config = global_repo.get_global_config()
        if not config:
            raise HTTPException(status_code=500, detail="Global configuration not found")
        
        # Get all playlist schedules from database (not hardcoded)
        playlist_schedules = global_repo.get_all_global_playlist_schedules()
        
        # Build weekly schedule (next 7 days)
        weekly_schedule = []
        today = datetime.now().date()
        
        for day_offset in range(7):
            date = today + timedelta(days=day_offset)
            python_weekday = date.weekday()  # 0=Monday, 6=Sunday
            # Convert Python weekday to calendar weekday (0=Sunday, 6=Saturday)
            weekday = (python_weekday + 1) % 7
            day_name = date.strftime("%A")
            date_str = date.strftime("%Y-%m-%d")
            
            subjects_for_day = []
            
            # Check each subject
            for subject, schedule in playlist_schedules.items():
                start_date = datetime.strptime(schedule['start_date'], "%Y-%m-%d").date()
                
                # Check if date is after start date
                if date < start_date:
                    continue
                
                # Check if weekday is in selected days
                if weekday not in schedule['selected_days']:
                    continue
                
                # Check frequency
                if schedule['frequency'] == 'daily':
                    subjects_for_day.append(subject)
                elif schedule['frequency'] == 'alternate':
                    last_sent = schedule.get('last_sent_date')
                    if not last_sent:
                        subjects_for_day.append(subject)
                    else:
                        last_sent_date = datetime.strptime(last_sent, "%Y-%m-%d").date()
                        days_passed = 0
                        check_date = last_sent_date + timedelta(days=1)
                        while check_date <= date:
                            check_python_weekday = check_date.weekday()
                            check_weekday = (check_python_weekday + 1) % 7
                            if check_weekday in schedule['selected_days']:
                                days_passed += 1
                            check_date += timedelta(days=1)
                        
                        if days_passed >= 2:
                            subjects_for_day.append(subject)
            
            weekly_schedule.append({
                "date": date_str,
                "day_name": day_name,
                "weekday": weekday,
                "is_today": day_offset == 0,
                "subjects": subjects_for_day
            })
        
        return {
            "schedule_enabled": config.schedule_enabled,
            "schedule_time": config.schedule_time,
            "current_day": config.current_day,
            "weekly_schedule": weekly_schedule
        }
    
    except HTTPException:
        raise
    except Exception as e:
        api_logger.error(f"Schedule summary error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
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


@app.post("/api/admin/send-file")
async def send_file_now(file_id: str = Body(..., embed=True), chat_id: str = Query(None)):
    """Send a file immediately to a user or ALL users (global mode)"""
    import time
    start_time = time.time()
    
    try:
        print(f"\n{'='*60}")
        print(f"📤 SEND FILE REQUEST RECEIVED")
        print(f"   File ID: {file_id}")
        print(f"   Chat ID: {chat_id or 'ALL USERS (global)'}")
        print(f"{'='*60}")
        
        # Get file metadata
        metadata = file_manager.get_file_metadata(file_id)
        
        if not metadata:
            print(f"❌ File not found in database: {file_id}")
            raise HTTPException(status_code=404, detail="File not found")
        
        print(f"✅ File metadata found: {metadata['original_name']} ({metadata['file_size']} bytes)")
        
        # Get file path
        file_path = file_manager.get_file_path(file_id)
        if not file_path or not file_path.exists():
            print(f"❌ File not found on disk: {file_path}")
            raise HTTPException(status_code=404, detail="File not found on disk")
        
        print(f"✅ File exists on disk: {file_path}")
        
        file_type = metadata['file_type']
        caption = f"📄 {metadata['original_name']}"
        
        # If no chat_id provided, send to ALL users (global mode)
        if not chat_id:
            users = user_repo.get_all_users()
            if not users:
                print(f"❌ No users found")
                raise HTTPException(status_code=404, detail="No users found")
            
            print(f"📊 Sending to {len(users)} users...")
            
            # For large files (>20MB), send sequentially to avoid pool timeout
            # For smaller files, send in parallel
            file_size_mb = metadata['file_size'] / (1024 * 1024)
            send_parallel = file_size_mb < 20
            
            if send_parallel:
                print(f"  Using parallel sending (file < 20MB)")
                # Send to all users in parallel
                async def send_to_user(user):
                    user_start = time.time()
                    try:
                        print(f"  → Starting send to {user.first_name} ({user.chat_id})...")
                        success, error = await bot.send_file_with_retry(
                            user.chat_id, 
                            str(file_path), 
                            caption, 
                            file_type,
                            max_retries=2
                        )
                        elapsed = time.time() - user_start
                        if success:
                            print(f"  ✅ Sent to {user.first_name} in {elapsed:.1f}s")
                        else:
                            print(f"  ❌ Failed to send to {user.first_name}: {error}")
                        return (user, success, error)
                    except Exception as e:
                        elapsed = time.time() - user_start
                        print(f"  ❌ Exception sending to {user.first_name} after {elapsed:.1f}s: {e}")
                        return (user, False, str(e))
                
                # Send to all users concurrently
                results = await asyncio.gather(*[send_to_user(user) for user in users])
            else:
                print(f"  Using sequential sending (file >= 20MB)")
                # Send to users one by one (sequential)
                results = []
                for user in users:
                    user_start = time.time()
                    try:
                        print(f"  → Sending to {user.first_name} ({user.chat_id})...")
                        success, error = await bot.send_file_with_retry(
                            user.chat_id, 
                            str(file_path), 
                            caption, 
                            file_type,
                            max_retries=2
                        )
                        elapsed = time.time() - user_start
                        if success:
                            print(f"  ✅ Sent to {user.first_name} in {elapsed:.1f}s")
                        else:
                            print(f"  ❌ Failed to send to {user.first_name}: {error}")
                        results.append((user, success, error))
                    except Exception as e:
                        elapsed = time.time() - user_start
                        print(f"  ❌ Exception sending to {user.first_name} after {elapsed:.1f}s: {e}")
                        results.append((user, False, str(e)))
            
            success_count = sum(1 for _, success, _ in results if success)
            failed_users = [(user.first_name, error) for user, success, error in results if not success]
            
            total_time = time.time() - start_time
            print(f"\n📊 SEND COMPLETE:")
            print(f"   Success: {success_count}/{len(users)} users")
            print(f"   Total time: {total_time:.1f}s")
            print(f"{'='*60}\n")
            
            message = f"File sent to {success_count}/{len(users)} users in {total_time:.0f}s"
            if failed_users:
                failed_names = ', '.join([name for name, _ in failed_users[:3]])
                message += f". Failed: {failed_names}"
                if len(failed_users) > 3:
                    message += f" and {len(failed_users) - 3} more"
            
            return {"success": True, "message": message, "sent_count": success_count, "total_users": len(users)}
        
        # Send to specific user (backward compatibility)
        user = user_repo.get_user_by_chat_id(chat_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        success, error = await bot.send_file_with_retry(
            chat_id, 
            str(file_path), 
            caption, 
            file_type
        )
        
        if not success:
            raise HTTPException(status_code=500, detail=f"Failed to send file: {error}")
        
        return {"success": True, "message": "File sent successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        api_logger.error(f"Error in send_file_now: {str(e)}", exc_info=True)
        print(f"❌ EXCEPTION in send_file_now: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/admin/schedule-file")
async def schedule_file(
    file_id: str = Body(...),
    scheduled_time: str = Body(...),
    payload: dict = Depends(verify_token)
):
    """Schedule a file to be sent at a specific date and time"""
    try:
        from datetime import datetime
        
        # Validate file exists
        metadata = file_manager.get_file_metadata(file_id)
        if not metadata:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Parse and validate scheduled time
        try:
            scheduled_dt = datetime.strptime(scheduled_time, "%Y-%m-%d %H:%M")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date/time format. Use YYYY-MM-DD HH:MM")
        
        # Check if time is in the future
        if scheduled_dt <= datetime.now():
            raise HTTPException(status_code=400, detail="Scheduled time must be in the future")
        
        # Store schedule in database
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Create scheduled_files table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scheduled_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_id TEXT NOT NULL,
                scheduled_time TIMESTAMP NOT NULL,
                status TEXT DEFAULT 'pending',
                created_by TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            INSERT INTO scheduled_files (file_id, scheduled_time, created_by)
            VALUES (?, ?, ?)
        """, (file_id, scheduled_time, payload.get("username", "admin")))
        
        conn.commit()
        conn.close()
        
        api_logger.info(f"File {file_id} scheduled for {scheduled_time} by {payload.get('username')}")
        
        return {
            "success": True,
            "message": f"File scheduled for {scheduled_dt.strftime('%B %d, %Y at %I:%M %p')}",
            "scheduled_time": scheduled_time
        }
        
    except HTTPException:
        raise
    except Exception as e:
        api_logger.error(f"Error scheduling file: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# Playlist schedule endpoints
class PlaylistScheduleUpdate(BaseModel):
    subject: str
    start_date: str
    frequency: str
    selected_days: list


@app.get("/api/config/playlist-schedules")
async def get_playlist_schedules(chat_id: str = Query(None, description="User's Telegram chat ID (optional for global mode)")):
    """Get all playlist schedules (GLOBAL - same for all users)"""
    try:
        schedules = global_repo.get_all_global_playlist_schedules()
        return schedules
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/config/playlist-schedules")
async def update_playlist_schedule(data: PlaylistScheduleUpdate, chat_id: str = Query(None, description="User's Telegram chat ID (optional for global mode)")):
    """Update or create playlist schedule (GLOBAL - affects all users)"""
    try:
        # Validate frequency
        if data.frequency not in ['daily', 'alternate']:
            raise HTTPException(status_code=400, detail="Frequency must be 'daily' or 'alternate'")
        
        # Validate selected_days (should be array of 0-6)
        if not all(isinstance(d, int) and 0 <= d <= 6 for d in data.selected_days):
            raise HTTPException(status_code=400, detail="selected_days must be array of integers 0-6")
        
        global_repo.upsert_global_playlist_schedule(
            data.subject, 
            data.start_date, 
            data.frequency, 
            data.selected_days
        )
        
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/config/playlist-schedules/{subject}")
async def delete_playlist_schedule(subject: str, chat_id: str = Query(None, description="User's Telegram chat ID (optional for global mode)")):
    """Delete playlist schedule (GLOBAL)"""
    try:
        success = global_repo.delete_global_playlist_schedule(subject)
        if not success:
            raise HTTPException(status_code=404, detail="Schedule not found")
        
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== FILE MANAGEMENT ENDPOINTS ====================


@app.get("/api/files")
async def get_files(
    limit: int = Query(100, description="Maximum number of files to return"),
    search: Optional[str] = Query(None, description="Search term for filename"),
    type: Optional[str] = Query(None, description="Filter by file type (pdf, video, image, audio)"),
    payload: dict = Depends(verify_token)
):
    """Get list of uploaded files"""
    try:
        files, total = file_manager.list_files(
            file_type=type if type != 'all' else None,
            search=search,
            limit=limit
        )
        return {"files": files, "total": total}
    except Exception as e:
        api_logger.error(f"Error fetching files: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/files/upload")
async def upload_file(
    file: UploadFile = File(...),
    payload: dict = Depends(verify_token)
):
    """Upload a new file"""
    try:
        # Read file data
        file_data = await file.read()
        
        # Save file
        result = file_manager.save_file(
            file_data=BytesIO(file_data),
            original_filename=file.filename,
            uploaded_by=payload.get("username", "admin")
        )
        
        api_logger.info(f"File uploaded: {file.filename} by {payload.get('username')}")
        return {"success": True, **result}
    except ValueError as e:
        api_logger.warning(f"File validation failed: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        api_logger.error(f"Error uploading file: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/files/{file_id}")
async def delete_file(
    file_id: str,
    payload: dict = Depends(verify_token)
):
    """Delete a file"""
    try:
        api_logger.info(f"Attempting to delete file: {file_id}")
        success, error, warnings = file_manager.delete_file(file_id)
        
        if not success:
            api_logger.warning(f"Delete failed: {error}")
            raise HTTPException(status_code=404, detail=error or "File not found")
        
        api_logger.info(f"File deleted: {file_id} by {payload.get('username')}")
        return {"success": True, "warnings": warnings}
    except HTTPException:
        raise
    except Exception as e:
        api_logger.error(f"Error deleting file: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/files/{file_id}/download")
async def download_file(
    file_id: str,
    payload: dict = Depends(verify_token)
):
    """Download a file"""
    try:
        file_path = file_manager.get_file_path(file_id)
        
        if not file_path or not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        metadata = file_manager.get_file_metadata(file_id)
        filename = metadata.get("original_filename", "download") if metadata else "download"
        
        return FileResponse(
            path=str(file_path),
            filename=filename,
            media_type="application/octet-stream"
        )
    except HTTPException:
        raise
    except Exception as e:
        api_logger.error(f"Error downloading file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== USER MANAGEMENT ENDPOINTS ====================

@app.post("/api/admin/users/{chat_id}/block")
async def block_user(
    chat_id: str,
    reason: str = Body(None, embed=True),
    payload: dict = Depends(verify_token)
):
    """Block a user"""
    try:
        success = user_manager.block_user(
            chat_id=chat_id,
            reason=reason,
            blocked_by=payload.get("username", "admin")
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to block user")
        
        api_logger.info(f"User blocked: {chat_id} by {payload.get('username')}")
        return {"success": True, "message": "User blocked successfully"}
    except Exception as e:
        api_logger.error(f"Error blocking user: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/admin/users/{chat_id}/unblock")
async def unblock_user(
    chat_id: str,
    payload: dict = Depends(verify_token)
):
    """Unblock a user"""
    try:
        success = user_manager.unblock_user(chat_id)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to unblock user")
        
        api_logger.info(f"User unblocked: {chat_id} by {payload.get('username')}")
        return {"success": True, "message": "User unblocked successfully"}
    except Exception as e:
        api_logger.error(f"Error unblocking user: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/admin/users/blocked")
async def get_blocked_users(payload: dict = Depends(verify_token)):
    """Get all blocked users"""
    try:
        users = user_manager.get_blocked_users()
        return {"users": users}
    except Exception as e:
        api_logger.error(f"Error fetching blocked users: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/admin/users/{chat_id}/analytics")
async def get_user_analytics(
    chat_id: str,
    payload: dict = Depends(verify_token)
):
    """Get detailed analytics for a specific user"""
    try:
        analytics = user_manager.get_user_analytics(chat_id)
        
        if not analytics:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {
            "chat_id": analytics.chat_id,
            "username": analytics.username,
            "total_days": analytics.total_days,
            "completed_days": analytics.completed_days,
            "completion_rate": analytics.completion_rate,
            "current_streak": analytics.current_streak,
            "longest_streak": analytics.longest_streak,
            "last_activity": analytics.last_activity.isoformat() if analytics.last_activity else None
        }
    except HTTPException:
        raise
    except Exception as e:
        api_logger.error(f"Error fetching user analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== DATABASE VIEWER ENDPOINTS ====================

@app.get("/api/database/tables")
async def get_database_tables(payload: dict = Depends(verify_token)):
    """Get list of all database tables"""
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        
        return {"tables": tables}
    except Exception as e:
        api_logger.error(f"Error fetching tables: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/database/table/{table_name}")
async def get_table_data(table_name: str, payload: dict = Depends(verify_token)):
    """Get data from a specific table"""
    try:
        # Validate table name to prevent SQL injection
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Table not found")
        
        # Get table data (limit to 1000 rows for performance)
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 1000")
        
        # Get column names
        columns = [description[0] for description in cursor.description]
        
        # Fetch rows and convert to dict
        rows = []
        for row in cursor.fetchall():
            rows.append(dict(zip(columns, row)))
        
        conn.close()
        
        return {"rows": rows, "count": len(rows)}
    except HTTPException:
        raise
    except Exception as e:
        api_logger.error(f"Error fetching table data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/admin/users/{chat_id}/analytics")
async def get_user_analytics(
    chat_id: str,
    payload: dict = Depends(verify_token)
):
    """Get detailed analytics for a specific user"""
    try:
        analytics = user_manager.get_user_analytics(chat_id)
        
        if not analytics:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {
            "chat_id": analytics.chat_id,
            "username": analytics.username,
            "total_days": analytics.total_days,
            "completed_days": analytics.completed_days,
            "completion_rate": analytics.completion_rate,
            "current_streak": analytics.current_streak,
            "longest_streak": analytics.longest_streak,
            "last_activity": analytics.last_activity.isoformat() if analytics.last_activity else None,
            "is_blocked": analytics.is_blocked,
            "created_at": analytics.created_at.isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        api_logger.error(f"Error fetching user analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/admin/users/{chat_id}/activity")
async def get_user_activity_log(
    chat_id: str,
    limit: int = Query(50, description="Number of activities to return"),
    payload: dict = Depends(verify_token)
):
    """Get user activity log"""
    try:
        activities = user_manager.get_user_activity(chat_id, limit)
        return {"activities": activities}
    except Exception as e:
        api_logger.error(f"Error fetching user activity: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/admin/analytics/all-users")
async def get_all_users_analytics(payload: dict = Depends(verify_token)):
    """Get analytics for all users"""
    try:
        analytics = user_manager.get_all_users_analytics()
        
        return {
            "users": [
                {
                    "chat_id": a.chat_id,
                    "username": a.username,
                    "total_days": a.total_days,
                    "completed_days": a.completed_days,
                    "completion_rate": a.completion_rate,
                    "current_streak": a.current_streak,
                    "longest_streak": a.longest_streak,
                    "last_activity": a.last_activity.isoformat() if a.last_activity else None,
                    "is_blocked": a.is_blocked,
                    "created_at": a.created_at.isoformat()
                }
                for a in analytics
            ]
        }
    except Exception as e:
        api_logger.error(f"Error fetching all users analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/admin/analytics/system")
async def get_system_analytics(payload: dict = Depends(verify_token)):
    """Get system-wide analytics"""
    try:
        analytics = user_manager.get_system_analytics()
        return analytics
    except Exception as e:
        api_logger.error(f"Error fetching system analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== PLAYLIST COMPLETION TRACKING ====================

@app.get("/api/playlists/status")
async def get_playlists_status(payload: dict = Depends(verify_token)):
    """Get completion status for all playlists (shows first user's progress)"""
    try:
        from playlist_tracker import get_playlist_tracker
        
        tracker = get_playlist_tracker()
        
        # Get first user's config (multi-user system)
        user_config = user_repo.get_user_config(user_id=1)  # Show first user's progress
        
        if not user_config:
            raise HTTPException(status_code=500, detail="User configuration not found")
        
        # Get YouTube API key from environment (optional)
        youtube_api_key = os.getenv("YOUTUBE_API_KEY")
        
        playlists_status = []
        
        # Default subjects with user-specific indices
        subjects = [
            ('english', user_config.english_playlist, user_config.english_index),
            ('history', user_config.history_playlist, user_config.history_index),
            ('polity', user_config.polity_playlist, user_config.polity_index),
            ('geography', user_config.geography_playlist, user_config.geography_index),
            ('economics', user_config.economics_playlist, user_config.economics_index)
        ]
        
        # Add custom subjects
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT subject_name, playlist_url, current_index FROM custom_subjects ORDER BY subject_name")
        custom_subjects = cursor.fetchall()
        conn.close()
        
        for subject_name, playlist_url, current_index in custom_subjects:
            subjects.append((subject_name.lower(), playlist_url, current_index))
        
        for subject, playlist_url, current_index in subjects:
            if not playlist_url:
                continue
            
            is_completed, total = tracker.is_playlist_completed(
                current_index, 
                playlist_url,
                youtube_api_key
            )
            
            percentage = tracker.get_completion_percentage(
                current_index,
                playlist_url,
                youtube_api_key
            )
            
            remaining = tracker.get_remaining_videos(
                current_index,
                playlist_url,
                youtube_api_key
            )
            
            playlists_status.append({
                'subject': subject,
                'current_index': current_index,
                'total_videos': total,
                'is_completed': is_completed,
                'completion_percentage': round(percentage, 1) if percentage else None,
                'remaining_videos': remaining,
                'playlist_url': playlist_url
            })
        
        return {
            'playlists': playlists_status,
            'has_completed': any(p['is_completed'] for p in playlists_status),
            'youtube_api_configured': youtube_api_key is not None
        }
    
    except Exception as e:
        api_logger.error(f"Error getting playlist status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/playlists/{subject}/reset")
async def reset_playlist(subject: str, payload: dict = Depends(verify_token)):
    """Reset a playlist to start from beginning"""
    try:
        config = global_repo.get_global_config()
        if not config:
            raise HTTPException(status_code=500, detail="Global configuration not found")
        
        subject_lower = subject.lower()
        
        # Reset index for the subject
        if subject_lower == "english":
            config.english_index = 0
        elif subject_lower == "history":
            config.history_index = 0
        elif subject_lower == "polity":
            config.polity_index = 0
        elif subject_lower == "geography":
            config.geography_index = 0
        elif subject_lower == "economics":
            config.economics_index = 0
        else:
            raise HTTPException(status_code=400, detail="Invalid subject")
        
        global_repo.update_global_config(config)
        
        api_logger.info(f"Playlist reset for {subject} by {payload.get('username')}")
        
        return {
            "success": True,
            "message": f"{subject.capitalize()} playlist reset to beginning"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        api_logger.error(f"Error resetting playlist: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ==================== ADMIN BROADCAST MESSAGING ====================

class BroadcastMessage(BaseModel):
    message: str
    target: str = "all"  # "all" or specific chat_id
    chat_id: Optional[str] = None


@app.post("/api/admin/broadcast")
async def broadcast_message(
    data: BroadcastMessage,
    payload: dict = Depends(verify_token)
):
    """Send broadcast message to users"""
    try:
        if data.target == "all":
            # Send to all active users
            users = user_repo.get_all_users()
            active_users = [u for u in users if u.is_active]
            
            if not active_users:
                raise HTTPException(status_code=404, detail="No active users found")
            
            success_count = 0
            failed_users = []
            
            for user in active_users:
                try:
                    # Format message with admin signature
                    formatted_message = f"📢 ANNOUNCEMENT\n\n{data.message}\n\n— Admin Team"
                    
                    success, error = await bot.send_confirmation(user.chat_id, formatted_message)
                    if success:
                        success_count += 1
                    else:
                        failed_users.append((user.first_name, error))
                except Exception as e:
                    failed_users.append((user.first_name, str(e)))
            
            api_logger.info(f"Broadcast sent to {success_count}/{len(active_users)} users by {payload.get('username')}")
            
            return {
                "success": True,
                "message": f"Broadcast sent to {success_count}/{len(active_users)} users",
                "sent_count": success_count,
                "total_users": len(active_users),
                "failed_count": len(failed_users)
            }
        
        else:
            # Send to specific user
            if not data.chat_id:
                raise HTTPException(status_code=400, detail="chat_id required for targeted message")
            
            user = user_repo.get_user_by_chat_id(data.chat_id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            # Format message with admin signature
            formatted_message = f"📬 MESSAGE FROM ADMIN\n\n{data.message}\n\n— Admin Team"
            
            success, error = await bot.send_confirmation(data.chat_id, formatted_message)
            
            if not success:
                raise HTTPException(status_code=500, detail=f"Failed to send message: {error}")
            
            api_logger.info(f"Message sent to {user.first_name} by {payload.get('username')}")
            
            return {
                "success": True,
                "message": f"Message sent to {user.first_name}",
                "recipient": user.first_name
            }
    
    except HTTPException:
        raise
    except Exception as e:
        api_logger.error(f"Broadcast error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
