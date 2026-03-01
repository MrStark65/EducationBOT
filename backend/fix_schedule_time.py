#!/usr/bin/env python3
"""Fix schedule time in database - set to 06:00"""

import sqlite3

def fix_schedule_time():
    db_path = "officer_priya_multi.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check current value
    cursor.execute("SELECT schedule_time FROM global_config WHERE id = 1")
    row = cursor.fetchone()
    if row:
        print(f"Current schedule_time: {row[0]}")
    
    # Update to 06:00
    cursor.execute("UPDATE global_config SET schedule_time = '06:00' WHERE id = 1")
    conn.commit()
    
    # Verify
    cursor.execute("SELECT schedule_time FROM global_config WHERE id = 1")
    row = cursor.fetchone()
    if row:
        print(f"Updated schedule_time: {row[0]}")
    
    conn.close()
    print("✅ Schedule time fixed to 06:00")

if __name__ == "__main__":
    fix_schedule_time()
