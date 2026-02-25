import os
import json
from typing import Dict, Any
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application


class TelegramBot:
    """Telegram bot for sending messages and handling callbacks"""
    
    def __init__(self, token: str):
        self.token = token
        self.bot = Bot(token=token)
    
    async def send_daily_message(
        self,
        chat_id: str,
        day: int,
        english_link: str,
        gk_subject: str,
        gk_link: str
    ) -> Dict[str, Any]:
        """
        Send formatted daily message with buttons
        
        Args:
            chat_id: Telegram chat ID
            day: Day number
            english_link: English video link
            gk_subject: GK subject name
            gk_link: GK video link
            
        Returns:
            Message response dict
        """
        message_text = f"""Officer Priya – Day {day}

📚 English: {english_link}
📖 GK ({gk_subject}): {gk_link}

Mark your completion:"""
        
        # Create inline keyboard with buttons
        keyboard = [
            [
                InlineKeyboardButton(
                    "✅ Done",
                    callback_data=json.dumps({"action": "complete", "day": day, "status": "DONE"})
                ),
                InlineKeyboardButton(
                    "❌ Not Done",
                    callback_data=json.dumps({"action": "complete", "day": day, "status": "NOT_DONE"})
                )
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Send message
        message = await self.bot.send_message(
            chat_id=chat_id,
            text=message_text,
            reply_markup=reply_markup
        )
        
        return {
            "ok": True,
            "message_id": message.message_id,
            "chat_id": chat_id
        }
    
    def handle_callback(self, callback_query: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse callback data and return action
        
        Args:
            callback_query: Telegram callback query dict
            
        Returns:
            Parsed callback data
        """
        data_str = callback_query.get("data", "{}")
        try:
            data = json.loads(data_str)
            return {
                "action": data.get("action"),
                "day": data.get("day"),
                "status": data.get("status")
            }
        except json.JSONDecodeError:
            return {"action": None, "day": None, "status": None}
    
    async def answer_callback(self, callback_query_id: str, text: str = None) -> bool:
        """
        Answer callback query to remove loading state
        
        Args:
            callback_query_id: Callback query ID
            text: Optional text to show
            
        Returns:
            Success status
        """
        try:
            await self.bot.answer_callback_query(
                callback_query_id=callback_query_id,
                text=text
            )
            return True
        except Exception as e:
            print(f"Error answering callback: {e}")
            return False
    
    async def send_confirmation(self, chat_id: str, message: str) -> bool:
        """
        Send simple text confirmation
        
        Args:
            chat_id: Telegram chat ID
            message: Confirmation message
            
        Returns:
            Success status
        """
        try:
            await self.bot.send_message(chat_id=chat_id, text=message)
            return True
        except Exception as e:
            print(f"Error sending confirmation: {e}")
            return False
