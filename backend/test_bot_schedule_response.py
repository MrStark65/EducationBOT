#!/usr/bin/env python3
"""
Test AI bot's schedule response
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from bot_polling_simple import get_weekly_schedule
from datetime import datetime
import pytz
import json

IST = pytz.timezone('Asia/Kolkata')

print(f"\n{'='*70}")
print(f"AI BOT SCHEDULE RESPONSE TEST")
print(f"{'='*70}\n")

# Test 1: Get weekly schedule
print("TEST 1: Weekly Schedule Command")
print("-" * 70)

try:
    schedule_data = get_weekly_schedule()
    
    print(f"✅ Bot returned schedule data\n")
    print(f"Schedule Time: {schedule_data['schedule_time']}")
    print(f"Current Day: {schedule_data['current_day']}")
    
    print(f"\nWeekly Schedule:")
    for day in schedule_data['weekly_schedule']:
        subjects = ', '.join([s.upper() for s in day['subjects']])
        today_marker = " ← TODAY" if day['is_today'] else ""
        print(f"  {day['day_name']}: {subjects}{today_marker}")
    
    # Check tomorrow (Monday)
    print(f"\n{'='*70}")
    print("TOMORROW'S SCHEDULE (Monday)")
    print(f"{'='*70}")
    
    monday_schedule = None
    for day in schedule_data['weekly_schedule']:
        if day['day_name'] == 'Monday':
            monday_schedule = day
            break
    
    if monday_schedule:
        subjects = monday_schedule['subjects']
        print(f"\nSubjects for Monday:")
        for subject in subjects:
            emoji = "📚" if subject == 'english' else "🏛️" if subject == 'history' else "⚖️" if subject == 'polity' else "🌍" if subject == 'geography' else "💰" if subject == 'economics' else "📖"
            print(f"  {emoji} {subject.upper()}")
        
        # Verify expected subjects
        expected = ['english', 'polity']
        if set(subjects) == set(expected):
            print(f"\n✅ CORRECT! Monday schedule matches expected: English + Polity")
        else:
            print(f"\n❌ MISMATCH!")
            print(f"   Expected: {', '.join(expected)}")
            print(f"   Got: {', '.join(subjects)}")
    else:
        print("❌ Monday not found in schedule!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

# Test 2: Simulate user asking about schedule
print(f"\n{'='*70}")
print("TEST 2: Simulated User Questions")
print(f"{'='*70}\n")

test_questions = [
    "What's my schedule for tomorrow?",
    "When do I get my videos?",
    "What subjects on Monday?",
    "Show me weekly schedule"
]

print("User might ask:")
for q in test_questions:
    print(f"  • {q}")

print(f"\nBot should respond with:")
print(f"  • Schedule time: 06:00 AM IST")
print(f"  • Tomorrow (Monday): English + Polity")
print(f"  • Weekly schedule showing all days")

# Test 3: Check if bot has correct context
print(f"\n{'='*70}")
print("TEST 3: Bot Context Verification")
print(f"{'='*70}\n")

context_items = [
    ("Schedule Time", schedule_data.get('schedule_time') == '06:00 AM'),
    ("Current Day", schedule_data.get('current_day') == 2),
    ("Monday has English", 'english' in monday_schedule['subjects'] if monday_schedule else False),
    ("Monday has Polity", 'polity' in monday_schedule['subjects'] if monday_schedule else False),
    ("Monday has History", 'history' not in monday_schedule['subjects'] if monday_schedule else True),
]

all_correct = True
for item, is_correct in context_items:
    emoji = "✅" if is_correct else "❌"
    print(f"{emoji} {item}")
    if not is_correct:
        all_correct = False

print(f"\n{'='*70}")
if all_correct:
    print("✅ BOT HAS CORRECT CONTEXT - Ready to answer user questions!")
else:
    print("⚠️  BOT CONTEXT HAS ISSUES - May give wrong answers!")
print(f"{'='*70}\n")

# Test 4: Format bot message
print(f"{'='*70}")
print("TEST 4: Sample Bot Response")
print(f"{'='*70}\n")

print("If user asks: 'What's tomorrow's schedule?'\n")
print("Bot should respond:\n")
print("─" * 50)
print(f"📅 Tomorrow's Schedule (Monday)")
print(f"")
print(f"🕰️ Time: 06:00 AM IST")
print(f"")
print(f"📚 Subjects:")
if monday_schedule:
    for subject in monday_schedule['subjects']:
        emoji = "📚" if subject == 'english' else "⚖️" if subject == 'polity' else "📖"
        subject_name = subject.replace('_', ' ').title()
        print(f"  {emoji} {subject_name}")
print(f"")
print(f"Get ready to start your day with these subjects! 💪")
print(f"")
print(f"- Officer Priya 🎖️")
print("─" * 50)

print(f"\n{'='*70}")
print("✅ ALL BOT TESTS COMPLETE")
print(f"{'='*70}\n")
