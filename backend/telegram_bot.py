import os
import json
from typing import Dict, Any
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application


class TelegramBot:
    """Telegram bot for sending messages and handling callbacks"""
    
    def __init__(self, token: str):
        self.token = token
        # Increase connection pool size for parallel file sending
        # pool_size: number of connections in the pool (default 1)
        # max_overflow: additional connections when pool is full (default 0)
        from telegram.request import HTTPXRequest
        request = HTTPXRequest(
            connection_pool_size=8,  # Allow 8 simultaneous connections
            pool_timeout=60.0  # Wait up to 60s for a connection
        )
        self.bot = Bot(token=token, request=request)
    
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
    
    async def send_confirmation(self, chat_id: str, message: str, parse_mode: str = 'Markdown') -> bool:
        """
        Send simple text confirmation
        
        Args:
            chat_id: Telegram chat ID
            message: Confirmation message
            parse_mode: Message formatting (default: Markdown)
            
        Returns:
            Success status
        """
        try:
            await self.bot.send_message(
                chat_id=chat_id, 
                text=message,
                parse_mode=parse_mode
            )
            return True
        except Exception as e:
            print(f"Error sending confirmation: {e}")
            return False
    
    async def send_daily_message_with_buttons(self, chat_id: str, day: int, message_text: str) -> bool:
        """
        Send daily message with DONE/NOT DONE buttons
        
        Args:
            chat_id: Telegram chat ID
            day: Day number
            message_text: Message content
            
        Returns:
            Success status
        """
        try:
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
            
            # Escape special Markdown characters in URLs and text
            # Characters that need escaping in Markdown: _ * [ ] ( ) ~ ` > # + - = | { } . !
            def escape_markdown(text: str) -> str:
                """Escape special characters for Telegram Markdown"""
                special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
                for char in special_chars:
                    text = text.replace(char, f'\\{char}')
                return text
            
            # Don't escape the entire message, just send without parse_mode to avoid issues
            # Send message without Markdown formatting to avoid parsing errors
            await self.bot.send_message(
                chat_id=chat_id,
                text=message_text,
                reply_markup=reply_markup
            )
            return True
        except Exception as e:
            print(f"Error sending message with buttons: {e}")
            return False

    async def send_content_message(
        self,
        chat_id: str,
        video_url: str,
        caption: str = None,
        content_type: str = 'video'
    ) -> Dict[str, Any]:
        """
        Send content message (video link) with interaction buttons
        
        Args:
            chat_id: Telegram chat ID
            video_url: Video URL
            caption: Optional caption
            content_type: Type of content
            
        Returns:
            Message response dict
        """
        message_text = f"""📹 CDS Preparation Content

{caption if caption else ''}

🔗 {video_url}"""
        
        # Create inline keyboard with buttons
        keyboard = [
            [
                InlineKeyboardButton(
                    "✅ Completed",
                    callback_data=json.dumps({"action": "completed", "type": "content"})
                ),
                InlineKeyboardButton(
                    "🆘 Need Help",
                    callback_data=json.dumps({"action": "help", "type": "content"})
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
    
    async def send_file(
        self,
        chat_id: str,
        file_path: str,
        caption: str = None,
        file_type: str = 'pdf'
    ) -> Dict[str, Any]:
        """
        Send file (PDF, image, document) with interaction buttons
        
        Args:
            chat_id: Telegram chat ID
            file_path: Path to file
            caption: Optional caption
            file_type: Type of file (pdf, jpg, png, doc, etc.)
            
        Returns:
            Message response dict
        """
        import os
        
        # Get file size for timeout calculation
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        # Calculate timeout: 30s base + 10s per MB (e.g., 32MB = 30 + 320 = 350s)
        timeout = max(60, int(30 + file_size_mb * 10))
        
        print(f"📤 Sending {file_size_mb:.1f}MB file to {chat_id} with {timeout}s timeout...")
        
        try:
            # For large files (>20MB), send without buttons to reduce complexity
            if file_size_mb > 20:
                print(f"  Large file detected, sending without buttons...")
                if file_type in ['jpg', 'jpeg', 'png']:
                    with open(file_path, 'rb') as file:
                        message = await self.bot.send_photo(
                            chat_id=chat_id,
                            photo=file,
                            caption=caption or "📄 CDS Study Material",
                            read_timeout=timeout,
                            write_timeout=timeout,
                            connect_timeout=30
                        )
                else:
                    with open(file_path, 'rb') as file:
                        message = await self.bot.send_document(
                            chat_id=chat_id,
                            document=file,
                            caption=caption or "📄 CDS Study Material",
                            read_timeout=timeout,
                            write_timeout=timeout,
                            connect_timeout=30
                        )
            else:
                # For smaller files, include buttons
                keyboard = [
                    [
                        InlineKeyboardButton(
                            "✅ Completed",
                            callback_data=json.dumps({"action": "completed", "type": "file"})
                        ),
                        InlineKeyboardButton(
                            "🆘 Need Help",
                            callback_data=json.dumps({"action": "help", "type": "file"})
                        )
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                if file_type in ['jpg', 'jpeg', 'png']:
                    with open(file_path, 'rb') as file:
                        message = await self.bot.send_photo(
                            chat_id=chat_id,
                            photo=file,
                            caption=caption or "📄 CDS Study Material",
                            reply_markup=reply_markup,
                            read_timeout=timeout,
                            write_timeout=timeout,
                            connect_timeout=30
                        )
                else:
                    with open(file_path, 'rb') as file:
                        message = await self.bot.send_document(
                            chat_id=chat_id,
                            document=file,
                            caption=caption or "📄 CDS Study Material",
                            reply_markup=reply_markup,
                            read_timeout=timeout,
                            write_timeout=timeout,
                            connect_timeout=30
                        )
            
            print(f"✅ File sent successfully to {chat_id}")
            
            return {
                "ok": True,
                "message_id": message.message_id,
                "chat_id": chat_id
            }
        except Exception as e:
            print(f"❌ Error sending file to {chat_id}: {str(e)}")
            raise
    
    async def send_file_with_retry(
        self,
        chat_id: str,
        file_path: str,
        caption: str = None,
        file_type: str = 'pdf',
        max_retries: int = 2
    ) -> tuple[bool, str]:
        """
        Send file with retry logic
        
        Args:
            chat_id: Telegram chat ID
            file_path: Path to file
            caption: Optional caption
            file_type: Type of file
            max_retries: Maximum number of retry attempts
            
        Returns:
            (success, error_message)
        """
        import asyncio
        import os
        
        # Get file size for better retry logic
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        
        for attempt in range(max_retries):
            try:
                await self.send_file(chat_id, file_path, caption, file_type)
                return True, None
            
            except Exception as e:
                error_msg = str(e)
                print(f"❌ Attempt {attempt + 1}/{max_retries} failed for {chat_id}: {error_msg}")
                
                if attempt < max_retries - 1:
                    # Longer wait for large files: 2s for small, 5s for large
                    wait_time = 2 if file_size_mb < 10 else 5
                    print(f"⏳ Waiting {wait_time}s before retry...")
                    await asyncio.sleep(wait_time)
                else:
                    # Final attempt failed
                    return False, error_msg
        
        return False, "Max retries exceeded"
    
    def handle_interaction_callback(self, callback_query: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse interaction callback data (completed/help)
        
        Args:
            callback_query: Telegram callback query dict
            
        Returns:
            Parsed callback data
        """
        data_str = callback_query.get("data", "{}")
        try:
            data = json.loads(data_str)
            return {
                "action": data.get("action"),  # 'completed' or 'help'
                "type": data.get("type"),      # 'content' or 'file'
                "delivery_id": callback_query.get("message", {}).get("message_id")
            }
        except json.JSONDecodeError:
            return {"action": None, "type": None, "delivery_id": None}
