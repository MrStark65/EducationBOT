"""
Rate Limiting Middleware for API Protection

Implements token bucket algorithm for rate limiting
"""

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from collections import defaultdict
from datetime import datetime, timedelta
import asyncio
from typing import Dict, Tuple


class RateLimiter(BaseHTTPMiddleware):
    """Rate limiting middleware using token bucket algorithm"""
    
    def __init__(self, app, requests_per_minute: int = 60, requests_per_hour: int = 1000):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        
        # Store: {ip: [(timestamp, count_minute), (timestamp, count_hour)]}
        self.request_counts: Dict[str, Tuple[datetime, int, datetime, int]] = defaultdict(
            lambda: (datetime.now(), 0, datetime.now(), 0)
        )
        
        # Cleanup old entries every 5 minutes
        asyncio.create_task(self._cleanup_old_entries())
    
    async def dispatch(self, request: Request, call_next):
        """Process request with rate limiting"""
        
        # Skip rate limiting for health check
        if request.url.path == "/api/health":
            return await call_next(request)
        
        # Get client IP
        client_ip = request.client.host
        
        # Check rate limits
        if not self._check_rate_limit(client_ip):
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Rate limit exceeded. Please try again later.",
                    "retry_after": 60
                }
            )
        
        # Process request
        response = await call_next(request)
        return response
    
    def _check_rate_limit(self, ip: str) -> bool:
        """Check if request is within rate limits"""
        now = datetime.now()
        
        # Get current counts
        last_minute_time, minute_count, last_hour_time, hour_count = self.request_counts[ip]
        
        # Reset minute counter if needed
        if now - last_minute_time > timedelta(minutes=1):
            last_minute_time = now
            minute_count = 0
        
        # Reset hour counter if needed
        if now - last_hour_time > timedelta(hours=1):
            last_hour_time = now
            hour_count = 0
        
        # Check limits
        if minute_count >= self.requests_per_minute:
            return False
        
        if hour_count >= self.requests_per_hour:
            return False
        
        # Increment counts
        minute_count += 1
        hour_count += 1
        
        # Update storage
        self.request_counts[ip] = (last_minute_time, minute_count, last_hour_time, hour_count)
        
        return True
    
    async def _cleanup_old_entries(self):
        """Periodically clean up old entries"""
        while True:
            await asyncio.sleep(300)  # 5 minutes
            
            now = datetime.now()
            to_delete = []
            
            for ip, (last_minute_time, _, last_hour_time, _) in self.request_counts.items():
                # Remove if both counters are old
                if (now - last_minute_time > timedelta(minutes=5) and 
                    now - last_hour_time > timedelta(hours=2)):
                    to_delete.append(ip)
            
            for ip in to_delete:
                del self.request_counts[ip]


def get_rate_limiter(requests_per_minute: int = 60, requests_per_hour: int = 1000):
    """Factory function to create rate limiter"""
    def create_limiter(app):
        return RateLimiter(app, requests_per_minute, requests_per_hour)
    return create_limiter
