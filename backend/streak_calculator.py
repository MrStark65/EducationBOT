from typing import List
from models import DailyLog


class StreakCalculator:
    """Calculate and manage study streaks"""
    
    def calculate_streak(self, logs: List[DailyLog]) -> int:
        """
        Calculate consecutive DONE days from most recent
        
        Args:
            logs: List of daily logs ordered by day number descending
            
        Returns:
            Current streak count
        """
        if not logs:
            return 0
        
        streak = 0
        for log in logs:
            if log.is_completed():
                streak += 1
            else:
                break
        
        return streak
    
    def update_streak_on_completion(
        self,
        current_streak: int,
        new_status: str,
        previous_day_status: str
    ) -> int:
        """
        Update streak based on status change
        
        Args:
            current_streak: Current streak value
            new_status: New status (DONE, NOT_DONE, PENDING)
            previous_day_status: Status of previous day
            
        Returns:
            Updated streak value
        """
        if new_status == "DONE":
            if previous_day_status == "DONE":
                return current_streak + 1
            else:
                return 1
        elif new_status == "NOT_DONE":
            return 0
        else:
            return current_streak
