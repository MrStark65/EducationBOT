from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Config:
    """Configuration model for the system"""
    id: int = 1
    chat_id: str = ""
    english_playlist: str = ""
    history_playlist: str = ""
    polity_playlist: str = ""
    geography_playlist: str = ""
    economics_playlist: str = ""
    english_index: int = 0
    history_index: int = 0
    polity_index: int = 0
    geography_index: int = 0
    economics_index: int = 0
    gk_rotation_index: int = 0
    day_count: int = 0
    streak: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def get_current_gk_subject(self) -> str:
        """Get current GK subject based on rotation index"""
        subjects = ["History", "Polity", "Geography", "Economics"]
        return subjects[self.gk_rotation_index]
    
    def get_gk_index(self, subject: str) -> int:
        """Get video index for a specific GK subject"""
        mapping = {
            "History": self.history_index,
            "Polity": self.polity_index,
            "Geography": self.geography_index,
            "Economics": self.economics_index
        }
        return mapping[subject]


@dataclass
class DailyLog:
    """Daily log model for tracking study sessions"""
    id: Optional[int] = None
    day_number: int = 0
    date: str = ""
    english_video_number: int = 0
    gk_subject: str = ""
    gk_video_number: int = 0
    status: str = "PENDING"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def is_completed(self) -> bool:
        """Check if the day is completed"""
        return self.status == "DONE"
    
    def is_pending(self) -> bool:
        """Check if the day is pending"""
        return self.status == "PENDING"
