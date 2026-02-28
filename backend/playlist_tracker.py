#!/usr/bin/env python3
"""
Playlist Tracker - Monitor playlist completion and notify users/admin
"""

import requests
import re
from typing import Optional, Dict
from logger import app_logger


class PlaylistTracker:
    """Track playlist progress and detect completion"""
    
    def __init__(self):
        self.cache = {}  # Cache playlist lengths
    
    def get_playlist_length(self, playlist_url: str, youtube_api_key: Optional[str] = None) -> Optional[int]:
        """
        Get total number of videos in a YouTube playlist
        
        Args:
            playlist_url: YouTube playlist URL
            youtube_api_key: Optional YouTube Data API key
            
        Returns:
            Number of videos or None if cannot determine
        """
        if not playlist_url:
            return None
        
        # Check cache first
        if playlist_url in self.cache:
            return self.cache[playlist_url]
        
        # Extract playlist ID
        match = re.search(r'list=([a-zA-Z0-9_-]+)', playlist_url)
        if not match:
            return None
        
        playlist_id = match.group(1)
        
        # If API key provided, use YouTube Data API
        if youtube_api_key:
            try:
                url = f"https://www.googleapis.com/youtube/v3/playlists"
                params = {
                    'part': 'contentDetails',
                    'id': playlist_id,
                    'key': youtube_api_key
                }
                response = requests.get(url, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('items'):
                        count = data['items'][0]['contentDetails']['itemCount']
                        self.cache[playlist_url] = count
                        app_logger.info(f"Playlist {playlist_id} has {count} videos")
                        return count
            except Exception as e:
                app_logger.warning(f"Failed to get playlist length via API: {e}")
        
        # Fallback: Try to scrape from playlist page (less reliable)
        try:
            response = requests.get(playlist_url, timeout=10)
            if response.status_code == 200:
                # Look for video count in page
                match = re.search(r'"videoCount":"(\d+)"', response.text)
                if match:
                    count = int(match.group(1))
                    self.cache[playlist_url] = count
                    app_logger.info(f"Playlist {playlist_id} has {count} videos (scraped)")
                    return count
        except Exception as e:
            app_logger.warning(f"Failed to scrape playlist length: {e}")
        
        return None
    
    def is_playlist_completed(
        self, 
        current_index: int, 
        playlist_url: str,
        youtube_api_key: Optional[str] = None
    ) -> tuple[bool, Optional[int]]:
        """
        Check if playlist is completed
        
        Args:
            current_index: Current video index (1-based)
            playlist_url: YouTube playlist URL
            youtube_api_key: Optional YouTube Data API key
            
        Returns:
            Tuple of (is_completed, total_videos)
        """
        total = self.get_playlist_length(playlist_url, youtube_api_key)
        
        if total is None:
            # Cannot determine, assume not completed
            return (False, None)
        
        is_completed = current_index >= total
        return (is_completed, total)
    
    def get_completion_percentage(
        self,
        current_index: int,
        playlist_url: str,
        youtube_api_key: Optional[str] = None
    ) -> Optional[float]:
        """
        Get completion percentage for a playlist
        
        Args:
            current_index: Current video index (1-based)
            playlist_url: YouTube playlist URL
            youtube_api_key: Optional YouTube Data API key
            
        Returns:
            Completion percentage (0-100) or None
        """
        total = self.get_playlist_length(playlist_url, youtube_api_key)
        
        if total is None or total == 0:
            return None
        
        percentage = (current_index / total) * 100
        return min(percentage, 100.0)
    
    def get_remaining_videos(
        self,
        current_index: int,
        playlist_url: str,
        youtube_api_key: Optional[str] = None
    ) -> Optional[int]:
        """
        Get number of remaining videos
        
        Args:
            current_index: Current video index (1-based)
            playlist_url: YouTube playlist URL
            youtube_api_key: Optional YouTube Data API key
            
        Returns:
            Number of remaining videos or None
        """
        total = self.get_playlist_length(playlist_url, youtube_api_key)
        
        if total is None:
            return None
        
        remaining = max(0, total - current_index)
        return remaining
    
    def clear_cache(self):
        """Clear the playlist length cache"""
        self.cache.clear()
        app_logger.info("Playlist cache cleared")


# Singleton instance
_playlist_tracker = None

def get_playlist_tracker() -> PlaylistTracker:
    """Get or create playlist tracker instance"""
    global _playlist_tracker
    if _playlist_tracker is None:
        _playlist_tracker = PlaylistTracker()
    return _playlist_tracker
