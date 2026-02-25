from typing import List
from models import DailyLog


class CompletionCalculator:
    """Calculate completion percentages"""
    
    def calculate_overall(self, logs: List[DailyLog]) -> float:
        """
        Return percentage of DONE days out of total
        
        Args:
            logs: List of daily logs
            
        Returns:
            Completion percentage (0-100)
        """
        if not logs:
            return 0.0
        
        total = len(logs)
        completed = sum(1 for log in logs if log.is_completed())
        
        return round((completed / total) * 100, 1)
    
    def calculate_weekly(self, logs: List[DailyLog]) -> float:
        """
        Return percentage of DONE days in last 7 days
        
        Args:
            logs: List of daily logs ordered by day number descending
            
        Returns:
            Weekly completion percentage (0-100)
        """
        if not logs:
            return 0.0
        
        # Get last 7 days
        recent_logs = logs[:7] if len(logs) >= 7 else logs
        
        total = len(recent_logs)
        completed = sum(1 for log in recent_logs if log.is_completed())
        
        return round((completed / total) * 100, 1)
