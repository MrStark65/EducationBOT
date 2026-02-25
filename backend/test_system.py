#!/usr/bin/env python3
"""Quick system test"""

import asyncio
from database import Database
from repository import Repository
from models import Config, DailyLog
from video_selector import VideoSelector
from streak_calculator import StreakCalculator
from completion_calculator import CompletionCalculator

async def test_system():
    print("🧪 Testing Officer Priya CDS System...")
    
    # Test database
    print("\n1. Testing database...")
    db = Database("test_system.db")
    repo = Repository(db)
    print("✅ Database initialized")
    
    # Test config
    print("\n2. Testing configuration...")
    config = Config(
        chat_id="1913237845",
        english_playlist="https://www.youtube.com/playlist?list=PLhrq-fv7kVgeyGNN5Y4p2iuNd5hLIPUST",
        history_playlist="https://www.youtube.com/playlist?list=PL3M0QAJjbrLhhy-PKTB3T2ZoA41ptNsfl",
        polity_playlist="https://www.youtube.com/playlist?list=PL3M0QAJjbrLj0dI6wXZad0C0qNrIhuH_W",
        geography_playlist="https://www.youtube.com/playlist?list=PL3M0QAJjbrLgfkfZlkaZnmQoJhXOL1c_V",
        economics_playlist="https://www.youtube.com/playlist?list=PL3M0QAJjbrLhs6obUK9RiZ2JKnOMvSzWh"
    )
    repo.update_config(config)
    loaded_config = repo.get_config()
    assert loaded_config.chat_id == "1913237845"
    print("✅ Configuration saved and loaded")
    
    # Test video selector
    print("\n3. Testing video selector...")
    selector = VideoSelector()
    eng_num, eng_url = selector.select_next_english(0, config.english_playlist)
    assert eng_num == 1
    print(f"✅ English video selected: #{eng_num}")
    
    gk_subject, gk_num, gk_url = selector.select_next_gk(
        0,
        {"History": 0, "Polity": 0, "Geography": 0, "Economics": 0},
        {
            "History": config.history_playlist,
            "Polity": config.polity_playlist,
            "Geography": config.geography_playlist,
            "Economics": config.economics_playlist
        }
    )
    assert gk_subject == "History"
    assert gk_num == 1
    print(f"✅ GK video selected: {gk_subject} #{gk_num}")
    
    # Test rotation
    next_rotation = selector.advance_rotation(0)
    assert next_rotation == 1
    print("✅ Rotation advanced correctly")
    
    # Test daily log
    print("\n4. Testing daily logs...")
    log = DailyLog(
        day_number=1,
        date="2024-01-01",
        english_video_number=1,
        gk_subject="History",
        gk_video_number=1,
        status="PENDING"
    )
    log_id = repo.insert_log(log)
    assert log_id > 0
    print("✅ Daily log created")
    
    # Test status update
    repo.update_log_status(1, "DONE")
    logs = repo.get_all_logs()
    assert logs[0].status == "DONE"
    print("✅ Status updated")
    
    # Test streak calculator
    print("\n5. Testing streak calculator...")
    streak_calc = StreakCalculator()
    streak = streak_calc.calculate_streak(logs)
    assert streak == 1
    print(f"✅ Streak calculated: {streak}")
    
    # Test completion calculator
    print("\n6. Testing completion calculator...")
    comp_calc = CompletionCalculator()
    overall = comp_calc.calculate_overall(logs)
    assert overall == 100.0
    print(f"✅ Completion calculated: {overall}%")
    
    # Clean up
    import os
    os.remove("test_system.db")
    
    print("\n🎉 All tests passed! System is ready to use.")
    print("\nNext steps:")
    print("1. Start the backend: uvicorn main:app --reload")
    print("2. Start the frontend: cd frontend && npm run dev")
    print("3. Open http://localhost:5173 in your browser")

if __name__ == "__main__":
    asyncio.run(test_system())
