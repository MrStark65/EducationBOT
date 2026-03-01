#!/usr/bin/env python3
"""
Verify tomorrow's delivery schedule
"""

from datetime import datetime, timedelta
import pytz

IST = pytz.timezone('Asia/Kolkata')

# Tomorrow is Monday, March 2, 2026
tomorrow = datetime(2026, 3, 2, 6, 0, 0, tzinfo=IST)
tomorrow_weekday_python = tomorrow.weekday()  # 0 = Monday
tomorrow_weekday_our_system = (tomorrow_weekday_python + 1) % 7  # Convert to 0=Sunday

print(f"{'='*70}")
print(f"TOMORROW'S SCHEDULE VERIFICATION")
print(f"{'='*70}")
print(f"\nDate: {tomorrow.strftime('%A, %B %d, %Y')}")
print(f"Time: {tomorrow.strftime('%I:%M %p IST')}")
print(f"Python weekday: {tomorrow_weekday_python} (0=Monday)")
print(f"Our system weekday: {tomorrow_weekday_our_system} (0=Sunday, 1=Monday)")

# Schedule configuration from database
schedules = {
    'English': {
        'frequency': 'daily',
        'days': [0,1,2,3,4,5,6],  # All days
        'start_date': '2026-02-28',
        'last_sent': '2026-03-01'
    },
    'History': {
        'frequency': 'alternate',
        'days': [0,6],  # Sun, Sat
        'start_date': '2026-03-01',
        'last_sent': '2026-03-01'
    },
    'Polity': {
        'frequency': 'alternate',
        'days': [1,4],  # Mon, Thu
        'start_date': '2026-03-01',
        'last_sent': None
    },
    'Geography': {
        'frequency': 'alternate',
        'days': [2,5],  # Tue, Fri
        'start_date': '2026-03-01',
        'last_sent': None
    },
    'Economics': {
        'frequency': 'alternate',
        'days': [3],  # Wed
        'start_date': '2026-03-01',
        'last_sent': None
    },
    'MCQ-Playlist-English': {
        'frequency': 'daily',
        'days': [0,1,2,3,4,5,6],  # All days
        'start_date': '2026-03-10',
        'last_sent': None
    }
}

day_names = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']

print(f"\n{'='*70}")
print(f"SCHEDULE ANALYSIS FOR MONDAY (weekday={tomorrow_weekday_our_system})")
print(f"{'='*70}\n")

subjects_to_send = []

for subject, config in schedules.items():
    emoji = "📚" if 'English' in subject else "🏛️" if subject == 'History' else "⚖️" if subject == 'Polity' else "🌍" if subject == 'Geography' else "💰" if subject == 'Economics' else "📖"
    
    # Check if start date has passed
    start_date = datetime.strptime(config['start_date'], '%Y-%m-%d').date()
    tomorrow_date = tomorrow.date()
    
    if tomorrow_date < start_date:
        print(f"⏸️  {emoji} {subject}: Before start date ({config['start_date']})")
        continue
    
    # Check if today is in selected days
    if tomorrow_weekday_our_system not in config['days']:
        day_str = ', '.join([day_names[d] for d in config['days']])
        print(f"⏸️  {emoji} {subject}: Monday not in schedule days ({day_str})")
        continue
    
    # Check frequency
    if config['frequency'] == 'daily':
        print(f"✅ {emoji} {subject}: SEND (daily)")
        subjects_to_send.append(subject)
    elif config['frequency'] == 'alternate':
        last_sent = config['last_sent']
        
        if not last_sent:
            print(f"✅ {emoji} {subject}: SEND (first time)")
            subjects_to_send.append(subject)
        else:
            # Count days passed since last send
            last_sent_date = datetime.strptime(last_sent, '%Y-%m-%d').date()
            
            # For alternate, need to check if at least 2 selected days have passed
            days_passed = 0
            check_date = last_sent_date + timedelta(days=1)
            while check_date <= tomorrow_date:
                check_weekday = (check_date.weekday() + 1) % 7
                if check_weekday in config['days']:
                    days_passed += 1
                check_date += timedelta(days=1)
            
            if days_passed >= 2:
                print(f"✅ {emoji} {subject}: SEND ({days_passed} selected days passed since {last_sent})")
                subjects_to_send.append(subject)
            else:
                print(f"⏸️  {emoji} {subject}: SKIP (only {days_passed} selected day(s) passed since {last_sent}, need 2)")

print(f"\n{'='*70}")
print(f"FINAL DELIVERY LIST FOR TOMORROW")
print(f"{'='*70}\n")

if subjects_to_send:
    print(f"✅ {len(subjects_to_send)} subject(s) will be sent:\n")
    for subject in subjects_to_send:
        emoji = "📚" if 'English' in subject else "🏛️" if subject == 'History' else "⚖️" if subject == 'Polity' else "🌍" if subject == 'Geography' else "💰" if subject == 'Economics' else "📖"
        print(f"  {emoji} {subject}")
else:
    print("❌ No subjects scheduled!")

print(f"\n{'='*70}")
print(f"EXPECTED RESULT")
print(f"{'='*70}\n")
print("Based on configuration:")
print("  ✅ English (daily)")
print("  ✅ Polity (alternate, Mon/Thu, first time)")
print("  ❌ MCQ-Playlist-English (starts March 10)")
print("  ❌ History (alternate, Sun/Sat, not Monday)")
print("  ❌ Geography (alternate, Tue/Fri, not Monday)")
print("  ❌ Economics (alternate, Wed only, not Monday)")

print(f"\n{'='*70}")
if set(subjects_to_send) == {'English', 'Polity'}:
    print("✅ SCHEDULE CORRECT!")
else:
    print(f"⚠️  SCHEDULE MISMATCH!")
    print(f"   Expected: English, Polity")
    print(f"   Got: {', '.join(subjects_to_send)}")
print(f"{'='*70}\n")
