#!/usr/bin/env python3
"""Authentication and authorization system"""

import os
import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

# Default admin credentials (change in production)
DEFAULT_ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
DEFAULT_ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")


class AuthManager:
    """Manage authentication and authorization"""
    
    def __init__(self):
        # Hash default password
        self.admin_username = DEFAULT_ADMIN_USERNAME
        self.admin_password_hash = bcrypt.hashpw(
            DEFAULT_ADMIN_PASSWORD.encode('utf-8'),
            bcrypt.gensalt()
        )
    
    def verify_password(self, plain_password: str, hashed_password: bytes) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password)
    
    def authenticate_user(self, username: str, password: str) -> bool:
        """Authenticate user credentials"""
        if username != self.admin_username:
            return False
        return self.verify_password(password, self.admin_password_hash)
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[dict]:
        """Verify JWT token and return payload"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
        except Exception:
            return None
    
    def change_password(self, username: str, old_password: str, new_password: str) -> bool:
        """Change user password"""
        if not self.authenticate_user(username, old_password):
            return False
        
        self.admin_password_hash = bcrypt.hashpw(
            new_password.encode('utf-8'),
            bcrypt.gensalt()
        )
        return True


# Singleton instance
_auth_manager = None

def get_auth_manager() -> AuthManager:
    """Get or create auth manager instance"""
    global _auth_manager
    if _auth_manager is None:
        _auth_manager = AuthManager()
    return _auth_manager
