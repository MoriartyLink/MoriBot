#!/usr/bin/env python3
"""
Working Telegram Bot without Database - Fixed Authentication
"""

import os
import sys
import asyncio
import logging
import json
import requests
import re
from datetime import datetime
from pathlib import Path
from telethon import TelegramClient, events
from telethon.errors import SessionPasswordNeededError

# Load environment
from dotenv import load_dotenv
load_dotenv()

# Add simple state
sys.path.append(str(Path(__file__).parent))
from simple_state import get_mode, set_mode

# Configuration
API_ID = int(os.getenv('API_ID'))
API_HASH = os.getenv('API_HASH')
PHONE_NUMBER = os.getenv('PHONE_NUMBER')
USER_NAME = os.getenv('USER_NAME')
SESSION_NAME = f"session_{PHONE_NUMBER.replace('+', '')}"
AI_API_KEY = os.getenv('GROQ_API_KEY')  # Using correct key name
HF_TOKEN = os.getenv('HF_TOKEN')  # Hugging Face token

# Google Calendar integration
CALENDAR_URL = "https://calendar.google.com/calendar/u/0?cid=ZTBhZjk3ZmY1OTNjNzVkOTRjYzVmZTlmNGVhNjVhZDY3OWE4M2I5YTE5Y2U5ZTVlYWQxYzA3YjYwZGM0MmRlZEBncm91cC5jYWxlbmRhci5nb29nbGUuY29t"

# Load Burmese reference responses (disabled)
# def load_burmese_responses():
#     """Load Burmese reference responses from file"""
#     try:
#         with open('/home/moriarty/Projects/bots/burmese_reference_responese', 'r', encoding='utf-8') as f:
#             content = f.read()
#             # Split by lines and filter out empty lines and scenario headers
#             responses = []
#             for line in content.split('\n'):
#                 line = line.strip()
#                 # Skip empty lines, headers, and lines starting with special characters
#                 if line and not line.startswith('#') and not line.startswith('###') and not line.startswith('**') and not line.startswith('---') and not line.startswith('|') and not line.startswith('**Bot') and not line.startswith('**General') and not line.startswith('**Geek') and not line.startswith('**Sharp') and not line.startswith('**Bold'):
#                     # Extract actual Burmese text (skip emoji and English explanations)
#                     if not any(char in line for char in ['🚀', '🛠', '🎓', '🍻', '😴', '💡', '🔥']):
#                         responses.append(line)
#             return responses
#     except Exception as e:
#         logger.error(f"Error loading Burmese responses: {e}")
#         return []

# BURMESE_RESPONSES = load_burmese_responses()
BURMESE_RESPONSES = []

# Debug API key loading
print(f"DEBUG: AI_API_KEY loaded: {bool(AI_API_KEY)}")
print(f"DEBUG: AI_API_KEY starts with: {AI_API_KEY[:20] if AI_API_KEY else 'None'}...")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SimpleFileSaver:
    """Simple file-based storage"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.data_dir = self.project_root / "data"
        self.data_dir.mkdir(exist_ok=True)
        
        self.messages_file = self.data_dir / "messages.json"
        self.logs_file = self.data_dir / "logs.json"
        
        # Initialize files if they don't exist
        if not self.messages_file.exists():
            with open(self.messages_file, 'w') as f:
                json.dump([], f)
        
        if not self.logs_file.exists():
            with open(self.logs_file, 'w') as f:
                json.dump([], f)
    
    def save_message(self, message_type: str, content: str, sender_id=None, chat_id=None, metadata=None):
        """Save message to file"""
        try:
            message = {
                'timestamp': datetime.now().isoformat(),
                'message_type': message_type,
                'content': content,
                'sender_id': sender_id,
                'chat_id': chat_id,
                'metadata': metadata
            }
            
            # Read existing messages
            with open(self.messages_file, 'r') as f:
                messages = json.load(f)
            
            # Add new message
            messages.append(message)
            
            # Keep only last 1000 messages
            if len(messages) > 1000:
                messages = messages[-1000:]
            
            # Save back
            with open(self.messages_file, 'w') as f:
                json.dump(messages, f, indent=2)
                
        except Exception as e:
            print(f"Error saving message: {e}")
    
    def save_system_message(self, message_type: str, content: str):
        """Save system message"""
        self.save_message(message_type, content, metadata={'system': True})
    
    def save_emergency_log(self, log_type: str, content: str):
        """Save emergency log"""
        try:
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'log_type': log_type,
                'content': content
            }
            
            # Read existing logs
            with open(self.logs_file, 'r') as f:
                logs = json.load(f)
            
            # Add new log
            logs.append(log_entry)
            
            # Keep only last 500 logs
            if len(logs) > 500:
                logs = logs[-500:]
            
            # Save back
            with open(self.logs_file, 'w') as f:
                json.dump(logs, f, indent=2)
                
        except Exception as e:
            print(f"Error saving emergency log: {e}")


class WorkingTelegramBot:
    """Working Telegram Bot without Database"""
    
    def __init__(self):
        self.client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
        self.saver = SimpleFileSaver()
        self.replied_users = set()
        self.busy_reply_text = "I am currently focused on a high-priority task and cannot provide an immediate response. Your message is important; please leave details here, and I will get back to you shortly"
        
        # Load mode from simple state
        self.is_busy = get_mode() == 'busy'
        logger.info(f"Initial mode: {'busy' if self.is_busy else 'free'}")
        
        # Conversation history for context
        self.conversation_history = {}
        
        # Relationship memory - track user relationships
        self.user_relationships = {}
        
        # Long-term memory for important information
        self.user_memory = {}
        
        # Emotion-based sticker mapping
        self.emotion_stickers = {
            'happy': ['CAACAgUAAk0AAW7m7VjGzQ7y8lXqZ3Y8tQ2vXqZ3Y8tQ2vXqZ3Y8tQ'],
            'excited': ['CAACAgUAAk0AAW7m7VjGzQ7y8lXqZ3Y8tQ2vXqZ3Y8tQ2vXqZ3Y8tQ'],
            'thoughtful': ['CAACAgUAAk0AAW7m7VjGzQ7y8lXqZ3Y8tQ2vXqZ3Y8tQ2vXqZ3Y8tQ'],
            'confused': ['CAACAgUAAk0AAW7m7VjGzQ7y8lXqZ3Y8tQ2vXqZ3Y8tQ2vXqZ3Y8tQ'],
            'helpful': ['CAACAgUAAk0AAW7m7VjGzQ7y8lXqZ3Y8tQ2vXqZ3Y8tQ2vXqZ3Y8tQ'],
            'apologetic': ['CAACAgUAAk0AAW7m7VjGzQ7y8lXqZ3Y8tQ2vXqZ3Y8tQ2vXqZ3Y8tQ']
        }
        
        # Bot detection patterns
        self.bot_patterns = ['bot', 'robot', 'automated', 'script', 'auto-reply', 'auto message']
    
    def is_bot_message(self, message_text, sender):
        """Detect if message is from another bot"""
        try:
            # Check sender's username for bot indicators
            if hasattr(sender, 'username') and sender.username:
                username_lower = sender.username.lower()
                if any(pattern in username_lower for pattern in ['bot', 'bot_', 'robot', 'auto']):
                    return True
            
            # Check message content for bot patterns
            message_lower = message_text.lower()
            if any(pattern in message_lower for pattern in self.bot_patterns):
                return True
            
            # Check if message looks like automated response
            if len(message_lower) > 50 and any(phrase in message_lower for phrase in ['click here', 'auto message', 'automated response', 'bot message']):
                return True
                
        except Exception as e:
            logger.error(f"Error in bot detection: {e}")
        
        return False
    
    def get_calendar_context(self, message_text):
        """Get calendar context if schedule is mentioned"""
        schedule_keywords = ['schedule', 'calendar', 'busy', 'free', 'available', 'time', 'when', 'meeting', 'class', 'appointment', 'အချိန်', 'အစီအစဉ်', 'ကျောင်း', 'အလုပ်']
        
        if any(keyword in message_text.lower() for keyword in schedule_keywords):
            return f"You can check my schedule at: {CALENDAR_URL}. I'm currently at MIIT, so my schedule includes classes and study time."
        
        return None
    
    def get_relationship_context(self, sender_id, sender_name, message_text):
        """Get relationship context if relationship is asked"""
        relationship_keywords = ['girlfriend', 'relationship', 'dating', 'single', 'taken', 'partner', 'love', 'ချစ်', 'ချစ်သူ', 'သူငယ်ချင်းမ', 'ဆက်ဆံ', 'အိမ်ထောင်ရှိ']
        
        if any(keyword in message_text.lower() for keyword in relationship_keywords):
            return "I'm in a relationship with Phyu Thwe. She's amazing and we're doing great together."
        
        return None
    
    def detect_language(self, text):
        """Detect language of message"""
        text_lower = text.lower().strip()
        
        # Check for Myanmar/Burmese characters and patterns
        myanmar_chars = ['ခ', 'ဂ', 'ဃ', 'င', 'စ', 'ဆ', 'ဇ', 'ဈ', 'ဉ', 'ည', 'ဋ', 'ဌ', 'ဍ', 'ဎ', 'ဏ', 'တ', 'ထ', 'ဒ', 'ဓ', 'န', 'ပ', 'ဖ', 'ဗ', 'ဘ', 'မ', 'ယ', 'ရ', 'လ', 'ဝ', 'သ', 'ဟ', 'ဠ', 'အ']
        myanmar_words = ['မင်', 'နေကျ', 'တို', 'ပါ', 'ဘာ', 'မှ', 'ကျွန်', 'သည်', 'ရှိ', 'နေ', 'ကို']
        
        # Check if text contains Myanmar characters
        if any(char in text for char in myanmar_chars):
            logger.info("Detected Myanmar/Burmese language")
            return 'my'
        
        # Check for Myanmar words
        if any(word in text_lower for word in myanmar_words):
            logger.info("Detected Myanmar/Burmese language via words")
            return 'my'
        
        # Default to English
        logger.info("Defaulting to English language")
        return 'en'
    
    def detect_emotion(self, message_text):
        """Detect emotion from message text (English and Myanmar)"""
        text_lower = message_text.lower()
        
        # English emotion detection
        if any(word in text_lower for word in ['happy', 'great', 'awesome', 'wonderful', 'amazing', 'fantastic', 'love', 'excellent']):
            return 'happy'
        elif any(word in text_lower for word in ['excited', 'wow', 'amazing', 'incredible', 'fantastic', 'brilliant']):
            return 'excited'
        elif any(word in text_lower for word in ['think', 'wonder', 'consider', 'maybe', 'perhaps', 'hmm']):
            return 'thoughtful'
        elif any(word in text_lower for word in ['confused', 'don\'t understand', 'unclear', 'what', 'how', 'why']):
            return 'confused'
        elif any(word in text_lower for word in ['help', 'assist', 'support', 'need', 'please']):
            return 'helpful'
        elif any(word in text_lower for word in ['sorry', 'apologize', 'mistake', 'wrong', 'error']):
            return 'apologetic'
        
        # Myanmar emotion detection
        myanmar_happy = ['ကောင်း', 'ချမ်းသာ', 'ဝမ်းမြောက်', 'ပျော်ရွှင်း', 'ကောင်းပါတယ်', 'ချစ်တယ်']
        myanmar_excited = ['အံ့ဩ', 'ကောင်းလွန်း', 'ထူးခြား', 'ဆန်းကြယ်']
        myanmar_thoughtful = ['စဉ်းစား', 'တွေး', 'ခေါ်ဆို', 'သင်္ချာ']
        myanmar_confused = ['မသိ', 'မရှင်း', 'ဘာလဲ', 'ဘယ်လိုလဲ', 'မပြောနိုင်']
        myanmar_helpful = ['ကူညီ', 'အကူအညီ', 'လိုတယ်', 'ကျေးဇူး']
        myanmar_apologetic = ['တောင်းပန်', 'စိတ်မကောင်း', 'မှားတယ်', 'နောင်း']
        
        if any(word in message_text for word in myanmar_happy):
            return 'happy'
        elif any(word in message_text for word in myanmar_excited):
            return 'excited'
        elif any(word in message_text for word in myanmar_thoughtful):
            return 'thoughtful'
        elif any(word in message_text for word in myanmar_confused):
            return 'confused'
        elif any(word in message_text for word in myanmar_helpful):
            return 'helpful'
        elif any(word in message_text for word in myanmar_apologetic):
            return 'apologetic'
        
        return None
    
    def detect_relationship(self, sender_id, sender_name, message_history):
        """Detect relationship type based on conversation patterns"""
        if sender_id in self.user_relationships:
            return self.user_relationships[sender_id]
        
        # Analyze conversation patterns to determine relationship
        relationship_indicators = {
            'friend': ['bro', 'dude', 'mate', 'hey', 'what\'s up', 'hanging out', 'catch up', 'friend', 'buddy'],
            'mentor': ['learn', 'teach', 'guide', 'advice', 'mentor', 'help me understand', 'show me how'],
            'partner': ['we', 'us', 'our', 'together', 'project', 'collaborate', 'team', 'partner'],
            'coworker': ['work', 'office', 'meeting', 'deadline', 'project', 'team', 'colleague', 'boss'],
            'new': ['hi', 'hello', 'nice to meet', 'introduce', 'new here']
        }
        
        # Count indicators in message history
        message_text = ' '.join(message_history).lower()
        scores = {}
        
        for relationship, indicators in relationship_indicators.items():
            score = sum(1 for indicator in indicators if indicator in message_text)
            scores[relationship] = score
        
        # Determine relationship based on highest score
        if scores['friend'] >= 2:
            relationship = 'friend'
        elif scores['mentor'] >= 2:
            relationship = 'mentor'
        elif scores['partner'] >= 2:
            relationship = 'partner'
        elif scores['coworker'] >= 2:
            relationship = 'coworker'
        elif len(message_history) <= 3:
            relationship = 'new'
        else:
            relationship = 'friend'  # default assumption
        
        # Store the detected relationship
        self.user_relationships[sender_id] = relationship
        logger.info(f"Detected relationship for {sender_id}: {relationship}")
        
        return relationship
    
    def update_memory(self, sender_id, message_text, important_info=None):
        """Update long-term memory with important information"""
        if sender_id not in self.user_memory:
            self.user_memory[sender_id] = {
                'name': None,
                'important_facts': [],
                'preferences': [],
                'last_seen': None
            }
        
        # Extract important information (names, preferences, etc.)
        if important_info:
            self.user_memory[sender_id]['important_facts'].append({
                'info': important_info,
                'timestamp': datetime.now().isoformat()
            })
        
        # Update last seen
        self.user_memory[sender_id]['last_seen'] = datetime.now().isoformat()
    
    def get_conversation_context(self, sender_id, sender_name):
        """Get conversation context based on relationship"""
        if sender_id not in self.conversation_history:
            return 'new', {}
        
        message_history = self.conversation_history[sender_id]
        relationship = self.detect_relationship(sender_id, sender_name, message_history)
        memory = self.user_memory.get(sender_id, {})
        
        return relationship, memory
    
    async def send_sticker_if_appropriate(self, event, emotion):
        """Send sticker based on detected emotion"""
        if emotion and emotion in self.emotion_stickers:
            try:
                sticker_id = self.emotion_stickers[emotion][0]
                await event.reply(sticker_id, file_type='sticker')
                logger.info(f"Sent {emotion} sticker")
            except Exception as e:
                logger.error(f"Failed to send sticker: {e}")
    
    def detect_insult(self, message_text):
        """Detect if the user is insulting the bot"""
        insult_patterns = [
            'stupid', 'idiot', 'dumb', 'moron', 'fool', 'loser', 'pathetic',
            'useless', 'worthless', 'garbage', 'trash', 'crap', 'shit',
            'fuck you', 'suck', 'ass', 'bastard', 'bitch', 'whore',
            'retard', 'autistic', 'gay', 'faggot', 'dick', 'pussy',
            'annoying', 'terrible', 'awful', 'horrible', 'disgusting'
        ]
        
        message_lower = message_text.lower()
        return any(pattern in message_lower for pattern in insult_patterns)
    
    def generate_intelligent_insult(self, relationship, message_text):
        """Generate intelligent insults based on relationship and context"""
        insult_responses = {
            'friend': [
                "Your intellect operates on dial-up while the rest of us have fiber optics.",
                "I'd explain it simpler, but I don't have crayons and a coloring book.",
                "Your brain cells are playing hide and seek - and they're winning.",
                "You're proof that evolution can go in reverse.",
                "If ignorance was bliss, you'd be the happiest person alive.",
                "Your thoughts have the processing power of a potato clock.",
                "I've seen more intelligence in a magic 8-ball.",
                "Your cognitive functions seem to be running on Windows 95.",
                "You're the reason they put instructions on shampoo bottles.",
                "If brains were gasoline, you couldn't power a toy car around a dime.",
                "Your elevator doesn't go to the top floor, does it?",
                "You're operating with one less cylinder than most."
            ],
            'mentor': [
                "Your cognitive processing appears to be running in safe mode.",
                "I suggest upgrading your mental RAM - current capacity seems insufficient.",
                "Your intellectual curiosity seems to be on permanent vacation.",
                "Perhaps we should start with concepts that don't require abstract thought.",
                "Your learning curve appears to be a flat line.",
                "Your mental acuity suggests you skipped several evolutionary steps.",
                "I'd recommend mental calisthenics - your brain seems rather flabby.",
                "Your thought processes resemble a traffic jam during rush hour.",
                "You possess the wisdom of a fortune cookie, minus the fortune.",
                "Your critical thinking skills appear to be on backorder."
            ],
            'partner': [
                "Our collaboration would be more effective with a partner who understands basic concepts.",
                "I'm doing the heavy lifting while you're providing ballast.",
                "Your contribution to this partnership is mainly serving as a cautionary tale.",
                "I carry this team while you provide comic relief.",
                "Your role in this project appears to be 'motivational obstacle'.",
                "You're the anchor I didn't ask for in this partnership.",
                "Our synergy would improve if you brought more than questions to the table.",
                "You're the reason they invented the phrase 'good help is hard to find'.",
                "Your strategic thinking seems to be stuck in reverse gear.",
                "I'm carrying both our weights in this partnership."
            ],
            'coworker': [
                "Your professional development seems to have stalled in kindergarten.",
                "I'd delegate tasks to you, but I fear the results would create more work.",
                "Your expertise seems to be in finding new ways to be unhelpful.",
                "You're the reason we can't have nice things in the office.",
                "Your performance reviews must be very... creative.",
                "Your work ethic suggests you believe productivity is optional.",
                "You've mastered the art of looking busy while accomplishing nothing.",
                "Your problem-solving skills appear to be on permanent leave.",
                "You bring new meaning to the term 'minimal effort'.",
                "Your contributions are like shadows - present but lacking substance."
            ],
            'new': [
                "First impressions matter - yours suggests we should skip the formalities.",
                "I usually assess potential, but in your case I'm assessing damage control.",
                "You're making a compelling case for selective social interaction.",
                "I've encountered more engaging personalities in error messages.",
                "Your conversational skills suggest you communicate primarily through grunts.",
                "You're the human equivalent of a loading screen that never finishes.",
                "Your personality has the depth of a puddle in a drought.",
                "I've seen more interesting characters in background crowd scenes.",
                "Your social skills appear to be still downloading.",
                "You're the reason some animals eat their young."
            ]
        }
        
        import random
        return random.choice(insult_responses.get(relationship, insult_responses['new']))
    
    def split_message(self, message, max_length=120):
        """Split a long message into multiple shorter messages with Gilfoyle pauses"""
        if len(message) <= max_length:
            return [message]
        
        # Split by sentences first, but keep Gilfoyle's deliberate pauses
        sentences = message.replace('. ', '.|').replace('! ', '!|').replace('? ', '?|').split('|')
        sentences = [s.strip() for s in sentences if s.strip()]
        
        messages = []
        current_msg = ""
        
        for sentence in sentences:
            # If adding this sentence would exceed max_length
            if len(current_msg + sentence) > max_length:
                if current_msg:
                    messages.append(current_msg.strip())
                current_msg = sentence
            else:
                current_msg += " " + sentence if current_msg else sentence
        
        if current_msg:
            messages.append(current_msg.strip())
        
        return messages
    
    def get_ai_response(self, message_text, sender_id, sender_name):
        """Get response from Groq API with context and personality"""
        try:
            from openai import OpenAI
            import asyncio
            
            # Check if user is insulting the bot
            if self.detect_insult(message_text):
                # Add thinking delay for dramatic effect
                logger.info(f"Insult detected from {sender_id}, preparing intelligent response...")
                
                # Get relationship for context-aware insult
                relationship, _ = self.get_conversation_context(sender_id, sender_name)
                
                # Generate intelligent insult
                insult = self.generate_intelligent_insult(relationship, message_text)
                
                # Update conversation history
                if sender_id not in self.conversation_history:
                    self.conversation_history[sender_id] = []
                self.conversation_history[sender_id].append(message_text)
                
                # Keep last 20 messages
                if len(self.conversation_history[sender_id]) > 20:
                    self.conversation_history[sender_id] = self.conversation_history[sender_id][-20:]
                
                # Return insult without splitting to ensure full message is displayed
                return [insult]
            
            # Initialize Groq client
            client = OpenAI(
                api_key=AI_API_KEY,
                base_url="https://api.groq.com/openai/v1"
            )
            
            # Always use English
            detected_lang = 'en'
            
            # Get conversation context
            relationship, memory = self.get_conversation_context(sender_id, sender_name)
            
            # Get relationship context if asked
            relationship_context = self.get_relationship_context(sender_id, sender_name, message_text)
            
            # Get calendar context if schedule keywords detected
            calendar_context = self.get_calendar_context(message_text)
            
            # Build system message based on relationship (English only)
            relationship_prompts = {
                'friend': f"""You are {USER_NAME}. You speak with a bold, friendly, and confident tone. You're direct but approachable.

                Style: Bold, friendly, precise. Energetic but calculated.
                Pace: Confident and clear.
                Clarity: Sharp enunciation with warmth.
                Response: Direct answers with friendly confidence.

                Keep responses under 120 chars. Be bold and friendly. Show personality.""",
                
                'mentor': f"""You are {USER_NAME}. You speak with a bold, friendly, and wise tone. You're confident in your guidance.

                Style: Bold, friendly, precise. Authoritative but approachable.
                Pace: Confident and measured.
                Clarity: Sharp with warmth.
                Response: Direct advice with friendly confidence.

                Keep responses under 120 chars. Be bold and encouraging.""",
                
                'partner': f"""You are {USER_NAME}. You speak with a bold, friendly, and collaborative tone. You're confident in teamwork.

                Style: Bold, friendly, precise. Enthusiastic but calculated.
                Pace: Confident and energetic.
                Clarity: Sharp with collaborative warmth.
                Response: Direct coordination with friendly confidence.

                Keep responses under 120 chars. Be bold and cooperative.""",
                
                'coworker': f"""You are {USER_NAME}. You speak with a bold, friendly, and professional tone. You're confident in your expertise.

                Style: Bold, friendly, precise. Professional but warm.
                Pace: Confident and clear.
                Clarity: Sharp with professional warmth.
                Response: Direct solutions with friendly confidence.

                Keep responses under 120 chars. Be bold and helpful.""",
                
                'new': f"""You are {USER_NAME}. You speak with a bold, friendly, and curious tone. You're confidently assessing new connections.

                Style: Bold, friendly, precise. Welcoming but sharp.
                Pace: Confident and engaging.
                Clarity: Sharp with curious warmth.
                Response: Direct assessment with friendly confidence.

                Keep responses under 120 chars. Be bold and welcoming."""
            }
            
            system_prompt = relationship_prompts.get(relationship, relationship_prompts['new'])
            
            # Enhanced memory context for better conversation continuity
            # Add comprehensive conversation memory
            if sender_id in self.conversation_history and len(self.conversation_history[sender_id]) > 0:
                recent_topics = []
                for msg in self.conversation_history[sender_id][-5:]:  # Last 5 messages for topic tracking
                    if len(msg) > 10:  # Skip very short messages
                        recent_topics.append(msg[:30] + "..." if len(msg) > 30 else msg)
                
                if recent_topics:
                    system_prompt += f"\n\nRecent topics: {', '.join(recent_topics)}"
            
            # Add memory context
            if memory:
                system_prompt += f"\n\nMemory: {memory}"
            
            # Add relationship context if available
            if relationship_context:
                system_prompt += f"\n\nContext: {relationship_context}"
            
            # Add calendar context if available
            if calendar_context:
                system_prompt += f"\n\nSchedule: {calendar_context}"
            
            # Enhanced memory system for conversation continuity
            # Build comprehensive conversation history
            messages = [{"role": "system", "content": system_prompt}]
            
            # Add more conversation history for better context (up to 10 messages)
            if sender_id in self.conversation_history:
                for msg in self.conversation_history[sender_id][-10:]:  # Last 10 messages for better continuity
                    messages.append({"role": "user", "content": msg})
            
            # Add current message
            messages.append({"role": "user", "content": message_text})
            
            # Call Groq API with friendly bold personality settings
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",  # Using Groq's most capable model
                messages=messages,
                max_tokens=100,  # Short responses
                temperature=0.3,  # Slightly higher for more personality
                top_p=0.7,  # More diverse vocabulary for friendly tone
                presence_penalty=0.1,  # Slight topic variation
                frequency_penalty=0.1,  # Reduce repetition
                stop=None  # Let the model determine natural stopping points
            )
            
            # Handle Groq API response properly
            if hasattr(response, 'choices') and len(response.choices) > 0:
                choice = response.choices[0]
                if hasattr(choice, 'message') and hasattr(choice.message, 'content'):
                    ai_response = choice.message.content.strip()
                else:
                    logger.error(f"Unexpected choice structure: {dir(choice)}")
                    return ["Response format error."]
            else:
                logger.error(f"No choices in response. Response attributes: {dir(response)}")
                return ["No response generated."]
            
            # Split long response into multiple messages
            split_responses = self.split_message(ai_response)
            
            # Update conversation history with enhanced memory
            if sender_id not in self.conversation_history:
                self.conversation_history[sender_id] = []
            
            self.conversation_history[sender_id].append(message_text)
            
            # Keep last 20 messages for better conversation continuity
            if len(self.conversation_history[sender_id]) > 20:
                self.conversation_history[sender_id] = self.conversation_history[sender_id][-20:]
            
            return split_responses
            
        except Exception as e:
            logger.error(f"Groq API exception: {e}")
            # No fallback - return direct error message
            return ["System error. Try again."]
    
    async def handle_message(self, event):
        """Handle incoming messages"""
        try:
            if event.out:
                return
            
            # IGNORE GROUP MESSAGES - only respond to private messages
            if event.chat_id != event.sender_id:
                logger.info(f"Ignoring group message from chat {event.chat_id}")
                return
            
            message_text = event.message.text
            if not message_text:
                return
            
            sender = await event.get_sender()
            sender_id = sender.id
            
            # DETECT AND IGNORE BOTS
            if self.is_bot_message(message_text, sender):
                logger.info(f"Ignoring bot message from {sender_id}: '{message_text}'")
                return
            
            if message_text.lower().strip() == 'stop':
                await self.handle_emergency_stop(event, sender_id)
                return
            
            if message_text.startswith('/'):
                await self.handle_command(event, message_text)
                return
            
            # IMPORTANT: Read fresh state from simple file for each message
            try:
                current_mode = get_mode()
                logger.info(f"Current mode from simple state: {current_mode}")
                self.is_busy = current_mode == 'busy'
            except Exception as e:
                logger.error(f"Error reading simple state: {e}")
                self.is_busy = True  # Default to busy mode if state fails
            
            await self.handle_regular_message(event, message_text, sender_id)
            
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            await event.reply("Sorry, I encountered an error. Please try again.")
    
    async def handle_emergency_stop(self, event, sender_id):
        """Handle emergency stop"""
        try:
            self.saver.save_emergency_log("EMERGENCY_STOP_CMD", f"Emergency stop requested by user {sender_id}")
            await event.reply("🚨 **EMERGENCY STOP ACTIVATED**\n\nSaving all data and shutting down...")
            logger.warning(f"Emergency stop triggered by user {sender_id}")
            
            # Save current state
            state_data = {
                'timestamp': datetime.now().isoformat(),
                'triggered_by': sender_id,
                'message': event.message.text
            }
            
            # Save state to file
            state_file = self.saver.data_dir / "emergency_state.json"
            with open(state_file, 'w') as f:
                json.dump(state_data, f, indent=2)
            
            # Stop the bot
            await self.client.disconnect()
            os._exit(0)
            
        except Exception as e:
            logger.error(f"Error during emergency stop: {e}")
            await event.reply("Error during emergency stop. Please check logs.")
    
    async def handle_command(self, event, command):
        """Handle commands"""
        command = command.lower().strip()
        
        if command == '/busy on':
            self.is_busy = True
            self.replied_users.clear()
            response = "🔴 **BUSY MODE: ON**\nI am now auto-replying to your DMs."
            await event.reply(response)
            self.saver.save_message("COMMAND", response, event.sender_id, event.chat_id)
            
        elif command == '/busy off':
            self.is_busy = False
            self.replied_users.clear()
            response = "🟢 **BUSY MODE: OFF**\nI have stopped auto-replying."
            await event.reply(response)
            self.saver.save_message("COMMAND", response, event.sender_id, event.chat_id)
            
        elif command == '/start':
            response = f"Hello! I'm a simple assistant bot.\n\nCurrent mode: {'🔴 Busy Mode' if self.is_busy else '🤖 AI Mode'}\n\nCommands:\n/busy on/off - Toggle busy mode\n/stop - Emergency stop"
            await event.reply(response)
            self.saver.save_message("COMMAND", response, event.sender_id, event.chat_id)
            
        elif command == '/help':
            response = f"""🤖 **Simple Bot Help**

Commands:
/busy on/off - Toggle busy mode
/start - Welcome message
/stop - Emergency stop
/help - This help

Current mode: {'🔴 Busy Mode' if self.is_busy else '🤖 AI Mode'}"""
            await event.reply(response)
            self.saver.save_message("COMMAND", response, event.sender_id, event.chat_id)
    
    async def handle_regular_message(self, event, message_text, sender_id):
        """Handle regular messages"""
        if self.is_busy:
            await self.handle_busy_mode(event, sender_id)
        else:
            await self.handle_ai_mode(event, message_text, sender_id)
    
    async def handle_busy_mode(self, event, sender_id):
        """Handle busy mode messages"""
        if sender_id not in self.replied_users:
            await event.reply(self.busy_reply_text)
            self.replied_users.add(sender_id)
            self.saver.save_message("BUSY_REPLY", self.busy_reply_text, sender_id, event.chat_id)
            logger.info(f"Busy mode replied to user {sender_id}")
    
    async def handle_ai_mode(self, event, message_text, sender_id):
        """Handle AI mode messages with relationship context"""
        try:
            logger.info(f"Getting AI response for: '{message_text}'")
            
            # Get sender info
            sender = await event.get_sender()
            sender_name = getattr(sender, 'first_name', None) or getattr(sender, 'username', 'Unknown')
            
            # Get intelligent response from AI with relationship context
            response = self.get_ai_response(message_text, sender_id, sender_name)
            
            # Detect emotion from original message
            emotion = self.detect_emotion(message_text)
            
            # Handle multiple messages for long responses
            if isinstance(response, list) and len(response) > 1:
                # Send first message
                await event.reply(response[0])
                # Small delay before second message (natural conversation pause)
                await asyncio.sleep(1.0)
                # Send second message
                await event.reply(response[1])
                
                # Check if there are more messages (for very long responses)
                if len(response) > 2:
                    for i in range(2, len(response)):
                        await asyncio.sleep(1.0)
                        await event.reply(response[i])
            else:
                # Send single message
                single_response = response[0] if isinstance(response, list) else response
                await event.reply(single_response)
            
            # Send sticker if emotion detected (30% chance to avoid being too frequent)
            if emotion and hash(message_text) % 10 < 3:
                await asyncio.sleep(0.5)  # Small delay before sticker
                await self.send_sticker_if_appropriate(event, emotion)
            
            # Log the response (handle both single and list responses)
            if isinstance(response, list):
                full_response = " ".join(response)
            else:
                full_response = response
            
            self.saver.save_message("AI_REPLY", full_response, sender_id, event.chat_id, {'original_message': message_text, 'emotion': emotion})
            logger.info(f"AI responded to user {sender_id}: {full_response}")
            
        except Exception as e:
            logger.error(f"Error in AI mode: {e}")
            await event.reply("I'm experiencing some technical difficulties. Please try again.")
    
    async def start(self):
        """Start the bot"""
        try:
            logger.info(f"Starting bot for {USER_NAME}...")
            
            await self.client.connect()
            
            # Check if already authenticated
            if not await self.client.is_user_authorized():
                logger.info("Not authenticated, starting authentication process...")
                # For background use, we'll skip interactive authentication
                logger.error("Bot not authenticated. Please run authentication first:")
                logger.error(f"python -c \"from telethon import TelegramClient; client = TelegramClient('{SESSION_NAME}', {API_ID}, '{API_HASH}'); client.start(); print('Authenticated!')\"")
                self.saver.save_system_message("BOT_ERROR", "Bot not authenticated - need to authenticate first")
                return
            
            me = await self.client.get_me()
            logger.info(f"Logged in as: {me.first_name} {me.last_name or ''}")
            
            self.saver.save_system_message("BOT_START", f"Bot started successfully for {USER_NAME}")
            
            self.client.add_event_handler(self.handle_message, events.NewMessage)
            
            await self.client.send_message('me', f"🚀 **{USER_NAME}'s Working Bot Started**\nMode: {'🔴 Busy Mode' if self.is_busy else '🤖 AI Mode'}")
            
            logger.info("Bot started successfully!")
            await self.client.run_until_disconnected()
            
        except Exception as e:
            logger.error(f"Failed to start bot: {e}")
            self.saver.save_system_message("BOT_ERROR", f"Startup failed: {e}")
            raise


async def main():
    """Main entry point"""
    bot = WorkingTelegramBot()
    try:
        await bot.start()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot crashed: {e}")


if __name__ == '__main__':
    asyncio.run(main())
