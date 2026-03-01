#!/usr/bin/env python3
"""
Test weekday conversion fix
"""

from datetime import datetime
import pytz

IST = pytz.timezone('Asia/Kolkata')

# Today is Sunday, March 1, 2026
today = datetime(2026, 3, 1, 12, 0, 0, tzinfo=IST)

print(f"Today: {today.strftime('%A, %B %d, %Y')}")
print(f"Python weekday(): {today.weekday()} (0=Monday, 6=Sunday)")

# Convert to 0=Sunday convention
converted_weekday = (today.weekday() + 1) % 7
print(f"Converted weekday: {converted_weekday} (0=Sunday, 1=Monday, 6=Saturday)")

# Test with schedule data
schedules = {
    'english': [0,1,2,3,4,5,6],  # All days
    'history': [0,6],  # Sun, Sat
    'polity': [1,4],  # Mon, Thu
    'geography': [2,5],  # Tue, Fri
    'economics': [3],  # Wed
}

day_names = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']

print(f"\n{'='*60}")
print(f"SCHEDULE CHECK FOR SUNDAY (weekday={converted_weekday})")
print(f"{'='*60}")

for subject, days in schedules.items():
    should_send = converted_weekday in days
    day_str = ', '.join([day_names[d] for d in days])
    emoji = "✅" if should_send else "❌"
    print(f"{emoji} {subject.upper()}: {day_str} - {'SEND' if should_send else 'SKIP'}")

print(f"\n{'='*60}")
print(f"EXPECTED RESULTS:")
print(f"{'='*60}")
print(f"✅ English: Should send (daily)")
print(f"✅ History: Should send (Sunday is in [Sun, Sat])")
print(f"❌ Polity: Should NOT send (Sunday not in [Mon, Thu])")
print(f"❌ Geography: Should NOT send (Sunday not in [Tue, Fri])")
print(f"❌ Economics: Should NOT send (Sunday not in [Wed])")
