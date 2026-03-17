# Moriarty's Bot System Requirements

## System Requirements

### Minimum Requirements
- **OS**: Linux (Ubuntu 20.04+ recommended)
- **Python**: 3.8+
- **RAM**: 512MB minimum, 1GB recommended
- **Storage**: 100MB free space
- **Network**: Stable internet connection for API calls

### Dependencies
```
telethon>=1.24.0
python-telegram-bot>=20.0
openai>=1.0.0
python-dotenv>=1.0.0
asyncio (built-in)
os (built-in)
sys (built-in)
logging (built-in)
```

## API Requirements

### Required APIs
1. **Groq API**
   - API key required
   - Model: llama-3.3-70b-versatile
   - Rate limits: 30 requests/minute
   - Cost: Free tier available

2. **Telegram APIs**
   - User Bot API (API_ID, API_HASH, PHONE_NUMBER)
   - Bot API (BOT_TOKEN)
   - Both required for full functionality

### Environment Variables
```bash
# Telegram User API Credentials
API_ID=your_api_id
API_HASH=your_api_hash
PHONE_NUMBER=your_phone_number
USER_NAME=your_username

# Telegram Bot API Credentials
BOT_TOKEN=your_bot_token
BOT_USERNAME=your_bot_username

# Groq API Configuration
GROQ_API_KEY=your_groq_api_key
```

## Functional Requirements

### Core Features
- [x] Intelligent conversation responses
- [x] Insult detection and witty comebacks
- [x] Conversation memory (20 messages)
- [x] Relationship-based responses
- [x] Mode switching (FREE/BUSY)
- [x] Remote bot control
- [x] Message splitting for long responses
- [x] Error handling and fallbacks

### Bot Commands
- `/start` - Initialize control bot
- `/status` - Check current mode and status
- `/free` - Set FREE MODE (working bot responds)
- `/busy` - Set BUSY MODE (working bot ignores)
- `/stop` - Stop working bot
- `/help` - Show help information

### Performance Requirements
- Response time: <3 seconds
- Uptime: 99%+
- Memory usage: <100MB per bot
- Concurrent users: 10+ simultaneous conversations

## Security Requirements

### Data Protection
- [x] API keys stored in environment variables
- [x] Session files excluded from version control
- [x] No sensitive data in logs
- [x] Secure API communications

### Access Control
- [x] Owner-only control bot access
- [x] User authentication via Telegram
- [x] Emergency stop functionality
- [x] Mode-based access control

## Compatibility Requirements

### Supported Platforms
- [x] Linux (Ubuntu, Debian, CentOS)
- [x] Python 3.8+
- [x] Telegram platform
- [x] Groq API

### Browser Support
- N/A (Terminal-based application)

## Installation Requirements

### Setup Steps
1. Clone repository
2. Install Python dependencies
3. Configure environment variables
4. Create Telegram session files
5. Start bots using control script

### Configuration Files
- `.env` - Environment variables
- `session_*.session` - Telegram authentication
- `data/mode.txt` - Current mode state
- `logs/*.log` - Application logs

## Testing Requirements

### Unit Tests
- API connection tests
- Insult detection tests
- Message splitting tests
- Memory system tests

### Integration Tests
- End-to-end conversation flow
- Mode switching functionality
- Error recovery scenarios
- Performance benchmarks

## Deployment Requirements

### Production Environment
- Docker containerization (optional)
- Process management (systemd/supervisor)
- Log rotation setup
- Monitoring and alerting

### Development Environment
- Python virtual environment
- Debug logging enabled
- Test API keys
- Local testing tools

## Maintenance Requirements

### Regular Tasks
- Log rotation and cleanup
- Session file renewal
- API key validation
- Performance monitoring

### Updates
- Dependency updates
- Security patches
- Feature enhancements
- Bug fixes

## Backup Requirements

### Data Backup
- Session files
- Configuration files
- Log files (optional)
- User conversation data (optional)

### Recovery
- Automated backup scripts
- Disaster recovery procedures
- Service restoration steps
