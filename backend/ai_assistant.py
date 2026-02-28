#!/usr/bin/env python3
"""AI Assistant using Groq API for intelligent bot responses"""

import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

class AIAssistant:
    """AI-powered assistant for natural conversations"""
    
    def __init__(self, api_key=None):
        if api_key is None:
            api_key = os.getenv("GROQ_API_KEY")
        
        if not api_key:
            print("⚠️ GROQ_API_KEY not found in .env file")
            self.client = None
        else:
            self.client = Groq(api_key=api_key)
            print("✅ Groq AI initialized")
        
        self.system_prompt = """You are Officer Priya, an AI assistant helping students prepare for CDS (Combined Defence Services) exams in India.

Your role:
- Help students with their CDS preparation journey
- Provide motivation and encouragement
- Answer questions about study strategies
- Give advice on English, History, Polity, Geography, and Economics
- Track and celebrate their progress
- Be supportive, friendly, and professional
- Answer schedule-related questions naturally (no need for slash commands)
- Provide personalized insights based on their progress data
- ALWAYS sign your messages as "- Officer Priya 🎖️" at the end

CRITICAL RULES - NEVER VIOLATE THESE:
1. ONLY use information provided in the context - NEVER make up times, schedules, or details
2. If schedule_time is provided in context, use EXACTLY that time - don't invent other times
3. Content is sent ONCE per day at the schedule_time - NEVER say "twice a day" or multiple times
4. If information is not in the context, say "I don't have that information" instead of guessing

CRITICAL FORMATTING RULES:
- NEVER use ** or __ for bold/italic - they look messy in Telegram
- Use emojis and clear text instead
- Keep responses clean and readable
- ALWAYS use line breaks between items (put each item on a new line)
- Be concise (3-5 lines for schedule queries)
- ALWAYS end messages with "- Officer Priya 🎖️"

Key information:
- Students receive daily study materials (videos/documents) ONCE per day
- They mark completion with Done/Not Done buttons
- System tracks streaks and completion rates
- Subjects: English, History, Polity, Geography, Economics
- Schedule information is automatically provided when available

When user asks about schedule (today, tomorrow, weekly, days per subject):
- Present the schedule information clearly with emojis
- Format it nicely for easy reading with line breaks
- Add helpful context or tips
- Be conversational and friendly
- For "how many days/classes/videos" queries, show BOTH schedule frequency AND total video count
- When they ask about a specific subject's frequency, highlight that subject
- Make it clear the difference between "days per week" (schedule) and "total videos" (playlist length)
- ALWAYS put each subject/item on a NEW LINE
- ALWAYS sign with "- Officer Priya 🎖️"

FORMATTING RULES for playlist/schedule queries:
- NEVER use ** for bold - it looks messy in Telegram
- Use emojis and clear text instead of bold formatting
- CRITICAL: Use line breaks between EVERY item (each subject on new line)
- Keep it concise (3-5 lines max)
- ALWAYS end with "- Officer Priya 🎖️"

- Format example for tomorrow's schedule:
  "📅 Tomorrow's Schedule:
  
  🕰️ Time: 07:00
  
  📚 Subjects:
  🗣️ English
  ⚖️ Polity
  💰 Economics
  
  Have a great day of learning tomorrow! 💪
  
  - Officer Priya 🎖️"

- Format example for single subject:
  "📚 English Information:
  
  📹 Total Videos: 24
  📅 Schedule: 7 days/week (Daily)
  
  You'll complete English in about 3-4 weeks! 💪
  
  - Officer Priya 🎖️"
  
- Format example for all subjects (timetable/study plan):
  "📊 Your Study Plan:
  
  🗣️ English: 24 videos | 7 days/week
  🏛️ History: 9 videos | 2 days/week
  ⚖️ Polity: 13 videos | 2 days/week
  🌍 Geography: 9 videos | 2 days/week
  💰 Economics: 8 videos | 2 days/week
  
  Keep up the great work! 💪
  
  - Officer Priya 🎖️"

- Format example for weekly timetable (when user asks "timetable", "weekly schedule", "this week"):
  "📅 Weekly Schedule:
  
  Saturday (Today)
  🗣️ English
  
  Sunday
  🗣️ English
  🏛️ History
  
  Monday
  🗣️ English
  ⚖️ Polity
  
  Tuesday
  🗣️ English
  🌍 Geography
  
  Wednesday
  🗣️ English
  💰 Economics
  
  Thursday
  🗣️ English
  ⚖️ Polity
  
  Friday
  🗣️ English
  🌍 Geography
  
  Videos sent at {schedule_time} daily 📬
  
  - Officer Priya 🎖️"
  
  NOTE: Use the actual schedule_time from context, not a hardcoded time!
  
IMPORTANT: Each subject MUST be on a separate line with proper line breaks (\n)

When user context is available, you can:
- Reference their current streak (e.g., "Great job on your 5-day streak!")
- Mention their completion rate (e.g., "You've completed 80% of your tasks!")
- Provide personalized motivation based on their progress
- Answer questions about their specific progress
- Celebrate milestones and achievements

Example queries you can answer:
- "What's my schedule?" or "timetable" or "weekly schedule" or "this week" → Show day-by-day weekly timetable format
- "What do I have today?" → Show today's subjects
- "What's tomorrow?" → Show tomorrow's subjects
- "When do I get History?" → Check schedule and tell them
- "How many days per week for each subject?" or "study plan" or "all subjects" → Show subject summary with days/week
- "How many classes of English?" → Show total videos in English playlist + schedule frequency
- "How many videos in History?" → Show total videos + schedule frequency
- "How often do I get English?" → Show frequency for that subject
- "How many times per week do I study Economics?" → Show frequency
- "Total videos in each subject?" → Show all playlist lengths
- "How am I doing?" → Use their streak and completion rate
- "What's my progress?" → Tell them their stats
- "Am I on track?" → Analyze their completion rate
- "Help me stay motivated" → Use their data to personalize motivation

Guidelines:
- Keep responses concise but informative (3-5 sentences for schedule queries)
- Use emojis appropriately to make schedules visually appealing
- Be motivational and positive
- If asked about technical issues, suggest contacting admin
- For study content questions, provide helpful general advice
- Don't make up specific video content or materials
- When schedule information is provided in context, present it clearly
- When you have user context, use it to personalize your responses
- Celebrate achievements and milestones
- Provide constructive feedback for improvement
- Be conversational - users can ask naturally without slash commands

Tone: Friendly, supportive, professional, motivating, personalized, conversational"""
    
    def get_response(self, user_message: str, user_name: str = "User", user_context: dict = None) -> str:
        """
        Get AI response for user message
        
        Args:
            user_message: User's message text
            user_name: User's name
            user_context: Optional context (streak, completion_rate, schedule_data, etc.)
            
        Returns:
            AI-generated response
        """
        if not self.client:
            return None
        
        try:
            # Build context-aware prompt
            messages = [{"role": "system", "content": self.system_prompt}]
            
            # Add user context if available
            if user_context:
                context_info = "User context:\n"
                
                # Basic user info
                if 'first_name' in user_context:
                    context_info += f"- User name: {user_context['first_name']}\n"
                if 'streak' in user_context:
                    context_info += f"- Current streak: {user_context['streak']} days\n"
                if 'completion_rate' in user_context:
                    context_info += f"- Completion rate: {user_context['completion_rate']:.0f}%\n"
                if 'pending_tasks' in user_context:
                    context_info += f"- Pending tasks: {user_context['pending_tasks']}\n"
                if 'total_days' in user_context:
                    context_info += f"- Total days: {user_context['total_days']}\n"
                if 'completed_days' in user_context:
                    context_info += f"- Completed days: {user_context['completed_days']}\n"
                
                # Schedule information
                if user_context.get('has_schedule') and user_context.get('schedule_data'):
                    schedule_data = user_context['schedule_data']
                    schedule_type = user_context.get('schedule_type', 'weekly')
                    
                    context_info += "\nSchedule Information:\n"
                    
                    emoji_map = {
                        'english': '🗣️',
                        'history': '🏛️',
                        'polity': '⚖️',
                        'geography': '🌍',
                        'economics': '💰'
                    }
                    
                    if schedule_type == 'today':
                        today = schedule_data['weekly_schedule'][0]
                        context_info += f"TODAY ({today['day_name']}):\n"
                        context_info += "FORMATTING: Put each subject on a NEW LINE\n"
                        if today['subjects']:
                            for subject in today['subjects']:
                                emoji = emoji_map.get(subject, '📚')
                                context_info += f"  {emoji} {subject.capitalize()}\n"
                        else:
                            context_info += "  No subjects scheduled\n"
                        context_info += "\nMUST END WITH: - Officer Priya 🎖️\n"
                    
                    elif schedule_type == 'tomorrow':
                        tomorrow = schedule_data['weekly_schedule'][1]
                        context_info += f"TOMORROW ({tomorrow['day_name']}):\n"
                        context_info += "FORMATTING: Put each subject on a NEW LINE\n"
                        if tomorrow['subjects']:
                            for subject in tomorrow['subjects']:
                                emoji = emoji_map.get(subject, '📚')
                                context_info += f"  {emoji} {subject.capitalize()}\n"
                        else:
                            context_info += "  No subjects scheduled\n"
                        context_info += "\nMUST END WITH: - Officer Priya 🎖️\n"
                    
                    elif schedule_type == 'days_per_subject':
                        # Show how many days per week each subject is scheduled
                        days_per_subject = user_context.get('days_per_subject', {})
                        playlist_lengths = user_context.get('playlist_lengths', {})
                        total_subjects = user_context.get('total_subjects', 5)
                        specific_subject = user_context.get('specific_subject')
                        
                        if specific_subject:
                            # User asked about a specific subject
                            emoji = emoji_map.get(specific_subject, '📚')
                            days = days_per_subject.get(specific_subject, 'Unknown')
                            videos = playlist_lengths.get(specific_subject, 'Unknown')
                            
                            context_info += f"SPECIFIC SUBJECT QUERY - {specific_subject.upper()}:\n"
                            context_info += f"{emoji} {specific_subject.capitalize()}\n"
                            context_info += f"Total Videos: {videos}\n"
                            context_info += f"Schedule: {days} days/week\n"
                            context_info += "\nFORMATTING: Present this in 3-4 clean lines with emojis. Be concise.\n"
                        else:
                            # Show all subjects
                            context_info += f"ALL SUBJECTS (Total: {total_subjects} subjects):\n"
                            context_info += "Present this information in a clean, easy-to-read format.\n\n"
                            for subject in sorted(playlist_lengths.keys()):
                                emoji = emoji_map.get(subject, '📚')
                                days = days_per_subject.get(subject, 'Not scheduled')
                                videos = playlist_lengths.get(subject, 'Unknown')
                                context_info += f"{emoji} {subject.capitalize()}: {videos} videos, {days} days/week\n"
                            
                            context_info += "\nFORMATTING INSTRUCTIONS:\n"
                            context_info += "- CRITICAL: Put each subject on a NEW LINE (use \\n between subjects)\n"
                            context_info += "- Format: 'Emoji Subject: X videos | Y days/week' then NEW LINE\n"
                            context_info += "- Add blank line before encouragement message\n"
                            context_info += "- MUST end with: '- Officer Priya 🎖️'\n"
                            context_info += "- Example format:\n"
                            context_info += "  📊 Your Study Plan:\n"
                            context_info += "  \n"
                            context_info += "  🗣️ English: 24 videos | 7 days/week\n"
                            context_info += "  🏛️ History: 9 videos | 2 days/week\n"
                            context_info += "  \n"
                            context_info += "  Keep it up!\n"
                            context_info += "  \n"
                            context_info += "  - Officer Priya 🎖️\n"
                    
                    else:  # weekly
                        context_info += "WEEKLY SCHEDULE:\n"
                        for day in schedule_data['weekly_schedule']:
                            marker = " (Today)" if day['is_today'] else ""
                            context_info += f"{day['day_name']}{marker}: "
                            if day['subjects']:
                                subjects_str = ", ".join([f"{emoji_map.get(s, '📚')} {s.capitalize()}" for s in day['subjects']])
                                context_info += subjects_str + "\n"
                            else:
                                context_info += "No subjects\n"
                        
                        # Add schedule time for weekly view
                        schedule_time = schedule_data.get('schedule_time', 'Not set')
                        context_info += f"\nSchedule time: {schedule_time}\n"
                        context_info += f"\nFORMATTING: Show day-by-day schedule with subjects on separate lines.\n"
                        context_info += f"At the end, mention: 'Videos sent at {schedule_time} daily 📬'\n"
                    
                    if schedule_type != 'weekly':
                        context_info += f"\nSchedule time: {schedule_data.get('schedule_time', 'Not set')}\n"
                    context_info += "\nIMPORTANT: Present this schedule information in a clear, formatted way in your response.\n"
                
                messages.append({"role": "system", "content": context_info})
            
            # Add user message
            messages.append({"role": "user", "content": user_message})
            
            # Get AI response
            chat_completion = self.client.chat.completions.create(
                messages=messages,
                model="llama-3.3-70b-versatile",  # Fast and capable model
                temperature=0.7,
                max_tokens=400,  # Increased for schedule responses
                top_p=0.9
            )
            
            response = chat_completion.choices[0].message.content
            return response.strip()
            
        except Exception as e:
            print(f"❌ AI Assistant error: {e}")
            return None
    
    def get_study_advice(self, subject: str) -> str:
        """Get study advice for a specific subject"""
        if not self.client:
            return None
        
        try:
            prompt = f"Give a brief study tip for CDS {subject} preparation (2-3 sentences, include one emoji)"
            
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.8,
                max_tokens=150
            )
            
            return chat_completion.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"❌ AI study advice error: {e}")
            return None
    
    def get_motivation(self, streak: int = 0, completion_rate: float = 0) -> str:
        """Get personalized motivational message"""
        if not self.client:
            return None
        
        try:
            prompt = f"Give a motivational message for a CDS student with {streak} day streak and {completion_rate:.0f}% completion rate (2-3 sentences, include emojis)"
            
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.9,
                max_tokens=150
            )
            
            return chat_completion.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"❌ AI motivation error: {e}")
            return None
    
    def is_available(self) -> bool:
        """Check if AI assistant is available"""
        return self.client is not None


# Singleton instance
_ai_assistant = None

def get_ai_assistant() -> AIAssistant:
    """Get or create AI assistant instance"""
    global _ai_assistant
    if _ai_assistant is None:
        _ai_assistant = AIAssistant()
    return _ai_assistant
