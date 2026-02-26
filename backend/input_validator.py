"""
Input Validation Utilities

Provides validation functions for user inputs
"""

import re
from typing import Optional, Tuple
from urllib.parse import urlparse


class InputValidator:
    """Input validation utilities"""
    
    # Regex patterns
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    USERNAME_PATTERN = re.compile(r'^[a-zA-Z0-9_-]{3,32}$')
    YOUTUBE_URL_PATTERN = re.compile(
        r'^(https?://)?(www\.)?(youtube\.com|youtu\.be)/(watch\?v=|playlist\?list=|embed/)?[\w-]+(&[\w=]*)*$'
    )
    TELEGRAM_CHAT_ID_PATTERN = re.compile(r'^-?\d{6,15}$')
    
    @staticmethod
    def validate_email(email: str) -> Tuple[bool, Optional[str]]:
        """Validate email address"""
        if not email:
            return False, "Email is required"
        
        if len(email) > 255:
            return False, "Email is too long"
        
        if not InputValidator.EMAIL_PATTERN.match(email):
            return False, "Invalid email format"
        
        return True, None
    
    @staticmethod
    def validate_username(username: str) -> Tuple[bool, Optional[str]]:
        """Validate username"""
        if not username:
            return False, "Username is required"
        
        if len(username) < 3:
            return False, "Username must be at least 3 characters"
        
        if len(username) > 32:
            return False, "Username must be at most 32 characters"
        
        if not InputValidator.USERNAME_PATTERN.match(username):
            return False, "Username can only contain letters, numbers, hyphens, and underscores"
        
        return True, None
    
    @staticmethod
    def validate_password(password: str) -> Tuple[bool, Optional[str]]:
        """Validate password strength"""
        if not password:
            return False, "Password is required"
        
        if len(password) < 8:
            return False, "Password must be at least 8 characters"
        
        if len(password) > 128:
            return False, "Password is too long"
        
        # Check for at least one letter and one number
        has_letter = any(c.isalpha() for c in password)
        has_number = any(c.isdigit() for c in password)
        
        if not (has_letter and has_number):
            return False, "Password must contain at least one letter and one number"
        
        return True, None
    
    @staticmethod
    def validate_youtube_url(url: str) -> Tuple[bool, Optional[str]]:
        """Validate YouTube URL"""
        if not url:
            return False, "URL is required"
        
        if len(url) > 2048:
            return False, "URL is too long"
        
        if not InputValidator.YOUTUBE_URL_PATTERN.match(url):
            return False, "Invalid YouTube URL format"
        
        return True, None
    
    @staticmethod
    def validate_telegram_chat_id(chat_id: str) -> Tuple[bool, Optional[str]]:
        """Validate Telegram chat ID"""
        if not chat_id:
            return False, "Chat ID is required"
        
        if not InputValidator.TELEGRAM_CHAT_ID_PATTERN.match(chat_id):
            return False, "Invalid Telegram chat ID format"
        
        return True, None
    
    @staticmethod
    def sanitize_string(text: str, max_length: int = 1000) -> str:
        """Sanitize string input"""
        if not text:
            return ""
        
        # Remove null bytes
        text = text.replace('\x00', '')
        
        # Trim whitespace
        text = text.strip()
        
        # Limit length
        if len(text) > max_length:
            text = text[:max_length]
        
        return text
    
    @staticmethod
    def validate_url(url: str) -> Tuple[bool, Optional[str]]:
        """Validate general URL"""
        if not url:
            return False, "URL is required"
        
        if len(url) > 2048:
            return False, "URL is too long"
        
        try:
            result = urlparse(url)
            if not all([result.scheme, result.netloc]):
                return False, "Invalid URL format"
            
            if result.scheme not in ['http', 'https']:
                return False, "URL must use HTTP or HTTPS"
            
            return True, None
        except Exception:
            return False, "Invalid URL format"
    
    @staticmethod
    def validate_integer(value: any, min_val: int = None, max_val: int = None) -> Tuple[bool, Optional[str]]:
        """Validate integer value"""
        try:
            int_value = int(value)
            
            if min_val is not None and int_value < min_val:
                return False, f"Value must be at least {min_val}"
            
            if max_val is not None and int_value > max_val:
                return False, f"Value must be at most {max_val}"
            
            return True, None
        except (ValueError, TypeError):
            return False, "Invalid integer value"


# Global instance
validator = InputValidator()
