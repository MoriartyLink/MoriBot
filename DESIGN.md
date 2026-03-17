# Moriarty's Bot System Design

## Overview
A dual-bot system consisting of a working userbot and a control bot for intelligent conversation management.

## Architecture

### Components
1. **Working Bot** (`working_bot.py`)
   - Main conversational AI using Groq API
   - Handles user interactions with intelligent responses
   - Features insult detection and witty comebacks
   - Maintains conversation history and context

2. **Control Bot** (`bot_api.py`)
   - Telegram bot for managing the working bot
   - Controls FREE/BUSY modes
   - Provides status monitoring and bot control commands

### Key Features

#### Working Bot
- **Intelligent Responses**: Uses Groq API with Llama 3.3 70B model
- **Memory System**: Maintains 20-message conversation history
- **Relationship Detection**: Adapts responses based on relationship type
- **Insult System**: Intelligent, witty responses to user insults
- **Message Splitting**: Handles long responses by splitting into chunks
- **Context Awareness**: Uses memory, relationship, and calendar context

#### Control Bot
- **Mode Management**: FREE MODE (responds) / BUSY MODE (ignores)
- **Status Monitoring**: Real-time bot status checks
- **Remote Control**: Start/stop working bot remotely
- **User Interface**: Inline buttons for easy control

### Data Flow
1. User sends message to working bot
2. Working bot processes message through Groq API
3. Response generated based on context and personality
4. If insult detected, intelligent insult response generated
5. Response delivered with appropriate formatting

### Configuration
- Environment variables stored in `.env`
- Session files for Telegram authentication
- Mode state stored in `data/mode.txt`
- Logs stored in `logs/` directory

### Security
- API keys stored in environment variables
- Session files excluded from version control
- Error handling for API failures
- Graceful fallbacks for system errors

## Personality System

### Relationship Types
- **Friend**: Bold, friendly, energetic
- **Mentor**: Wise, encouraging, authoritative
- **Partner**: Collaborative, enthusiastic, cooperative
- **Coworker**: Professional, helpful, competent
- **New**: Welcoming, curious, assessing

### Insult System
- Detects 25+ insult patterns
- 51 unique intelligent responses
- Context-aware based on relationship
- Third-level thinking responses

## Technical Specifications

### Dependencies
- `telethon` - Telegram userbot framework
- `python-telegram-bot` - Telegram bot framework
- `openai` - Groq API client
- `python-dotenv` - Environment variable management
- `asyncio` - Asynchronous operations

### API Configuration
- Groq API: Llama 3.3 70B Versatile model
- Temperature: 0.3 (balanced personality)
- Max tokens: 100 (concise responses)
- Top-p: 0.7 (diverse vocabulary)

### Performance
- Response time: ~1-2 seconds
- Memory usage: ~50MB per bot
- Conversation history: 20 messages per user
- Message splitting: 120 characters max

## Error Handling
- API failure fallbacks
- Network error recovery
- Invalid input handling
- Graceful degradation

## Future Enhancements
- Voice message support
- Image processing capabilities
- Multi-language support
- Advanced sentiment analysis
- Custom personality training
