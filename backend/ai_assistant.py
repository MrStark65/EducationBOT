#!/usr/bin/env python3
"""AI Assistant using Groq API for intelligent bot responses"""

import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

class AIAssistant:
    """AI-powered assistant for natural conversations"""
    
    def __init__(self):
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

Key information:
- Students receive daily study materials (videos/documents)
- They mark completion with Done/Not Done buttons
- System tracks streaks and completion rates
- Subjects: English, History, Polity, Geography, Economics

Guidelines:
- Keep responses concise (2-3 sentences for simple queries)
- Use emojis appropriately (but not excessively)
- Be motivational and positive
- If asked about technical issues, suggest contacting admin
- For study content questions, provide helpful general advice
- Don't make up specific video content or materials

Tone: Friendly, supportive, professional, motivating"""
    
    def get_response(self, user_message: str, user_context: dict = None) -> str:
        """
        Get AI response for user message
        
        Args:
            user_message: User's message text
            user_context: Optional context (streak, completion_rate, pending_tasks, etc.)
            
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
                if 'streak' in user_context:
                    context_info += f"- Current streak: {user_context['streak']} days\n"
                if 'completion_rate' in user_context:
                    context_info += f"- Completion rate: {user_context['completion_rate']:.0f}%\n"
                if 'pending_tasks' in user_context:
                    context_info += f"- Pending tasks: {user_context['pending_tasks']}\n"
                if 'total_days' in user_context:
                    context_info += f"- Total days: {user_context['total_days']}\n"
                if 'first_name' in user_context:
                    context_info += f"- User name: {user_context['first_name']}\n"
                
                messages.append({"role": "system", "content": context_info})
            
            # Add user message
            messages.append({"role": "user", "content": user_message})
            
            # Get AI response
            chat_completion = self.client.chat.completions.create(
                messages=messages,
                model="llama-3.3-70b-versatile",  # Fast and capable model
                temperature=0.7,
                max_tokens=300,  # Keep responses concise
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
