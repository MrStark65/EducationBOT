import json
import traceback
from database import Database


class ErrorLogger:
    """Error logging system"""
    
    def __init__(self, db: Database):
        self.db = db
    
    def log_error(
        self,
        error_type: str,
        error_message: str,
        stack_trace: str = None,
        context: dict = None
    ):
        """
        Persist error to database
        
        Args:
            error_type: Type of error
            error_message: Error message
            stack_trace: Stack trace string
            context: Additional context dict
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO error_logs (error_type, error_message, stack_trace, context)
                VALUES (?, ?, ?, ?)
            """, (
                error_type,
                error_message,
                stack_trace or "",
                json.dumps(context) if context else "{}"
            ))
            conn.commit()
        except Exception as e:
            print(f"Failed to log error: {e}")
        finally:
            conn.close()
    
    def get_recent_errors(self, limit: int = 10):
        """Get recent error logs"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM error_logs 
            ORDER BY timestamp DESC 
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        errors = []
        for row in rows:
            errors.append({
                "id": row["id"],
                "timestamp": row["timestamp"],
                "error_type": row["error_type"],
                "error_message": row["error_message"],
                "stack_trace": row["stack_trace"],
                "context": row["context"]
            })
        
        return errors
