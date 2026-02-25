from typing import Tuple, Dict
import re


class VideoSelector:
    """Video selection and rotation logic"""
    
    def __init__(self):
        self.subjects = ["History", "Polity", "Geography", "Economics"]
    
    def select_next_english(self, current_index: int, playlist_url: str = "") -> Tuple[int, str]:
        """
        Return next English video number and URL
        
        Args:
            current_index: Current video index
            playlist_url: YouTube playlist URL
            
        Returns:
            Tuple of (video_number, video_url)
        """
        next_index = current_index + 1
        video_url = self._construct_video_url(playlist_url, next_index)
        return (next_index, video_url)
    
    def select_next_gk(
        self,
        rotation_index: int,
        subject_indices: Dict[str, int],
        playlists: Dict[str, str]
    ) -> Tuple[str, int, str]:
        """
        Return GK subject, video number, and URL
        
        Args:
            rotation_index: Current rotation index (0-3)
            subject_indices: Dict mapping subject names to their current indices
            playlists: Dict mapping subject names to playlist URLs
            
        Returns:
            Tuple of (subject_name, video_number, video_url)
        """
        subject = self.subjects[rotation_index]
        current_index = subject_indices.get(subject, 0)
        next_index = current_index + 1
        playlist_url = playlists.get(subject, "")
        video_url = self._construct_video_url(playlist_url, next_index)
        
        return (subject, next_index, video_url)
    
    def advance_rotation(self, current_index: int) -> int:
        """
        Return next rotation index (0-3)
        
        Args:
            current_index: Current rotation index
            
        Returns:
            Next rotation index
        """
        return (current_index + 1) % 4
    
    def _construct_video_url(self, playlist_url: str, video_index: int) -> str:
        """
        Construct video URL from playlist URL and index
        
        Args:
            playlist_url: YouTube playlist URL
            video_index: Video index in playlist
            
        Returns:
            Video URL or placeholder
        """
        if not playlist_url:
            return f"Video #{video_index}"
        
        # Extract playlist ID from URL
        match = re.search(r'list=([a-zA-Z0-9_-]+)', playlist_url)
        if match:
            playlist_id = match.group(1)
            return f"https://www.youtube.com/playlist?list={playlist_id}&index={video_index}"
        
        return f"Video #{video_index}"
