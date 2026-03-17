#!/bin/bash
# Simple Bot Control Script

PROJECT_DIR="/home/moriarty/Projects/bots"
WORKING_BOT_SCRIPT="$PROJECT_DIR/working_bot.py"
CONTROL_BOT_SCRIPT="$PROJECT_DIR/bot_api.py"
LOG_DIR="$PROJECT_DIR/logs"

# Create necessary directories
mkdir -p "$LOG_DIR"

case "$1" in
    start)
        echo "🚀 Starting Bots..."
        
        # Start control bot in background
        nohup "$PROJECT_DIR/.venv/bin/python" "$CONTROL_BOT_SCRIPT" > "$LOG_DIR/control_bot.log" 2>&1 &
        CONTROL_PID=$!
        echo $CONTROL_PID > "$PROJECT_DIR/control_bot.pid"
        
        # Start working bot in background
        nohup "$PROJECT_DIR/.venv/bin/python" "$WORKING_BOT_SCRIPT" > "$LOG_DIR/working_bot.log" 2>&1 &
        WORKING_PID=$!
        echo $WORKING_PID > "$PROJECT_DIR/working_bot.pid"
        
        echo "✅ Control Bot started with PID: $CONTROL_PID"
        echo "✅ Working Bot started with PID: $WORKING_PID"
        echo "📋 Check status with: $0 status"
        ;;
    
    stop)
        echo "🛑 Stopping Bots..."
        
        # Stop working bot
        if [ -f "$PROJECT_DIR/working_bot.pid" ]; then
            WORKING_PID=$(cat "$PROJECT_DIR/working_bot.pid")
            if ps -p $WORKING_PID > /dev/null 2>&1; then
                kill -TERM $WORKING_PID
                echo "✅ Working Bot stopped"
            fi
            rm -f "$PROJECT_DIR/working_bot.pid"
        fi
        
        # Stop control bot
        if [ -f "$PROJECT_DIR/control_bot.pid" ]; then
            CONTROL_PID=$(cat "$PROJECT_DIR/control_bot.pid")
            if ps -p $CONTROL_PID > /dev/null 2>&1; then
                kill -TERM $CONTROL_PID
                echo "✅ Control Bot stopped"
            fi
            rm -f "$PROJECT_DIR/control_bot.pid"
        fi
        ;;
    
    restart)
        echo "🔄 Restarting Bots..."
        $0 stop
        sleep 2
        $0 start
        ;;
    
    status)
        echo "🤖 Bot Status Check"
        echo "============================"
        
        # Check control bot
        if [ -f "$PROJECT_DIR/control_bot.pid" ]; then
            CONTROL_PID=$(cat "$PROJECT_DIR/control_bot.pid")
            if ps -p $CONTROL_PID > /dev/null 2>&1; then
                echo "✅ Control Bot is RUNNING (PID: $CONTROL_PID)"
            else
                echo "❌ Control Bot is NOT running (stale PID file)"
                rm -f "$PROJECT_DIR/control_bot.pid"
            fi
        else
            echo "❌ Control Bot is NOT running (no PID file)"
        fi
        
        echo ""
        
        # Check working bot
        if [ -f "$PROJECT_DIR/working_bot.pid" ]; then
            WORKING_PID=$(cat "$PROJECT_DIR/working_bot.pid")
            if ps -p $WORKING_PID > /dev/null 2>&1; then
                echo "✅ Working Bot is RUNNING (PID: $WORKING_PID)"
            else
                echo "❌ Working Bot is NOT running (stale PID file)"
                rm -f "$PROJECT_DIR/working_bot.pid"
            fi
        else
            echo "❌ Working Bot is NOT running (no PID file)"
        fi
        
        echo ""
        echo "📊 Mode Status:"
        if [ -f "$PROJECT_DIR/data/mode.txt" ]; then
            MODE=$(cat "$PROJECT_DIR/data/mode.txt")
            if [ "$MODE" = "free" ]; then
                echo "Current mode: 🟢 FREE MODE"
            else
                echo "Current mode: 🔴 BUSY MODE"
            fi
        else
            echo "Current mode: 🔴 BUSY MODE (default)"
        fi
        
        echo ""
        echo "📁 Session Files:"
        ls -la "$PROJECT_DIR"/session*.session 2>/dev/null | wc -l | xargs echo "Session files:"
        ;;
    
    logs)
        echo "📋 Control Bot Logs (Ctrl+C to exit):"
        tail -f "$LOG_DIR/control_bot.log" 2>/dev/null || echo "❌ No control bot log file found"
        ;;
    
    working-logs)
        echo "📋 Working Bot Logs (Ctrl+C to exit):"
        tail -f "$LOG_DIR/working_bot.log" 2>/dev/null || echo "❌ No working bot log file found"
        ;;
    
    *)
        echo "🤖 Simple Bot Control"
        echo "=================="
        echo ""
        echo "Usage: $0 {start|stop|restart|status|logs|working-logs}"
        echo ""
        echo "Commands:"
        echo "  start         - Start both bots"
        echo "  stop          - Stop both bots"
        echo "  restart       - Restart both bots"
        echo "  status        - Show detailed status"
        echo "  logs          - Follow control bot logs"
        echo "  working-logs - Follow working bot logs"
        echo ""
        echo "Bots:"
        echo "  🎛 Control Bot: https://t.me/moriartys_assistant_bot (mode control)"
        echo "  🤖 Working Bot: User bot (responds to messages)"
        echo "  📊 Mode File: data/mode.txt (shared state)"
        exit 1
        ;;
esac

exit 0
