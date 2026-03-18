# MoriBot 

A dual-bot system with intelligent conversation capabilities.
<img width="100" height="100" alt="image" src="https://github.com/user-attachments/assets/8d0ffee8-8f4c-4a88-98e5-1a3f11a91c4e" />



## Quick Start

### Option 1: Docker (Recommended)
```bash
# Method 1: Direct run with sudo
./docker-run.sh

# Method 2: Local build (if registry issues)
./docker-local.sh

# Method 3: Manual setup
docker pull ghcr.io/moriartylink/moribot:latest
docker-compose up -d

# Or manual run
docker run -d \
  --name moribot \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/.env:/app/.env:ro \
  -v $(pwd)/session_*.session:/app/session_*.session \
  ghcr.io/moriartylink/moribot:latest
```

### Option 2: Local Setup
```bash
# Install Dependencies
pip install -r requirements.txt

# Configure Environment
cp .env_example .env
# Edit .env with your API keys and credentials

# Start the Bots
./simple_control.sh start
```

### 3. Control the Bot
Use the control bot (@moriartysassistantbot) with these commands:
- `/status` - Check current mode
- `/free` - Enable responses (FREE MODE)
- `/busy` - Disable responses (BUSY MODE)
- `/stop` - Stop the working bot
- `/help` - Show all commands

## Features

- **Intelligent Responses** - Powered by Groq AI with Llama 3.3
- **Witty Insults** - Clever comebacks when users insult the bot
- **Memory System** - Remembers conversation context
- **Personality Adaptation** - Adapts to different relationship types
- **Dual Bot System** - Working bot + Control bot
- **Mode Switching** - FREE/BUSY modes for availability control

## Requirements

- Python 3.8+
- Groq API key
- Telegram User API credentials
- Telegram Bot API credentials

## Configuration

Copy `.env_example` to `.env` and fill in:

```bash
# Telegram User API
API_ID=your_api_id
API_HASH=your_api_hash
PHONE_NUMBER=+959xxxxxxxxx
USER_NAME=your_username

# Telegram Bot API
BOT_TOKEN=your_bot_token
BOT_USERNAME=your_bot_username

# Groq API
GROQ_API_KEY=your_groq_api_key
```

## Control Commands

```bash
./simple_control.sh start    # Start both bots
./simple_control.sh stop     # Stop both bots
./simple_control.sh restart  # Restart both bots
./simple_control.sh status   # Check status
```

## Bot Personality

The working bot has different personalities based on relationship:
- **Friend**: Bold, friendly, energetic
- **Mentor**: Wise, encouraging, authoritative
- **Partner**: Collaborative, enthusiastic
- **Coworker**: Professional, helpful
- **New**: Welcoming, curious

## Security

- API keys stored in environment variables
- Session files excluded from git
- No sensitive data in logs
- Secure authentication

## Documentation

- `DESIGN.md` - System architecture and design
- `REQUIREMENT.md` - Detailed requirements
- `.env_example` - Environment template

## Troubleshooting

1. **Authentication fails**: Check API credentials in `.env`
2. **Bot not responding**: Check mode with `/status`
3. **Session issues**: Delete `*.session` files and restart
4. **API errors**: Verify Groq API key is valid

## License

MIT License
