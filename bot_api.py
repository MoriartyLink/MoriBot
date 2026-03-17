#!/usr/bin/env python3
"""
Moriarty's Assistant Bot - Control Bot
For managing the working userbot modes
"""

import os
import sys
import asyncio
import logging
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from datetime import datetime

# Load environment variables
load_dotenv()

# Bot configuration
BOT_TOKEN = os.getenv('BOT_TOKEN')
BOT_USERNAME = os.getenv('BOT_USERNAME')

# Project paths
PROJECT_DIR = "/home/moriarty/Projects/bots"
MODE_FILE = f"{PROJECT_DIR}/data/mode.txt"

# Ensure data directory exists
os.makedirs(f"{PROJECT_DIR}/data", exist_ok=True)

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def get_current_mode():
    """Get current mode from file"""
    try:
        if os.path.exists(MODE_FILE):
            with open(MODE_FILE, 'r') as f:
                return f.read().strip()
        return "busy"  # Default mode
    except Exception as e:
        logger.error(f"Error reading mode file: {e}")
        return "busy"

def set_mode(mode):
    """Set mode to file"""
    try:
        with open(MODE_FILE, 'w') as f:
            f.write(mode)
        return True
    except Exception as e:
        logger.error(f"Error writing mode file: {e}")
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    welcome_text = (
        "🤖 **Moriarty's Assistant Bot**\n\n"
        "I control the working userbot mode.\n\n"
        "Commands:\n"
        "/status - Check current mode\n"
        "/free - Set FREE MODE (userbot responds)\n"
        "/busy - Set BUSY MODE (userbot ignores)\n"
        "/help - Show this help"
    )
    
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /status command"""
    mode = get_current_mode()
    mode_emoji = "🟢" if mode == "free" else "🔴"
    mode_text = "FREE MODE" if mode == "free" else "BUSY MODE"
    
    status_text = (
        f"📊 **Bot Status**\n\n"
        f"Current Mode: {mode_emoji} {mode_text}\n\n"
        f"🟢 **FREE MODE**: Working bot responds to messages\n"
        f"🔴 **BUSY MODE**: Working bot ignores messages\n\n"
        f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    
    keyboard = [
        [InlineKeyboardButton("🟢 Set Free Mode", callback_data="set_free")],
        [InlineKeyboardButton("🔴 Set Busy Mode", callback_data="set_busy")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(status_text, parse_mode='Markdown', reply_markup=reply_markup)

async def set_free_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /free command"""
    if set_mode("free"):
        await update.message.reply_text(
            "🟢 **FREE MODE Activated**\n\n"
            "Working bot will now respond to messages.",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text("❌ Failed to set mode")

async def set_busy_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /busy command"""
    if set_mode("busy"):
        await update.message.reply_text(
            "🔴 **BUSY MODE Activated**\n\n"
            "Working bot will now ignore messages.",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text("❌ Failed to set mode")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_text = (
        "🤖 **Moriarty's Assistant Bot Help**\n\n"
        "**Commands:**\n"
        "/start - Start the bot\n"
        "/status - Check current mode\n"
        "/free - Set FREE MODE\n"
        "/busy - Set BUSY MODE\n"
        "/stop - Stop the working bot\n"
        "/help - Show this help\n\n"
        "**What is this bot?**\n"
        "This bot controls the working userbot's behavior:\n"
        "• 🟢 **FREE MODE**: Userbot responds to all messages\n"
        "• 🔴 **BUSY MODE**: Userbot ignores all messages\n\n"
        "**Bot Info:**\n"
        f"Username: @{BOT_USERNAME}\n"
        f"Status: Active"
    )
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def stop_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /stop command"""
    try:
        # Read the working bot PID
        with open(f"{PROJECT_DIR}/working_bot.pid", 'r') as f:
            working_pid = f.read().strip()
        
        # Kill the working bot process
        os.system(f"kill -9 {working_pid} 2>/dev/null")
        
        # Remove PID file
        try:
            os.remove(f"{PROJECT_DIR}/working_bot.pid")
        except:
            pass
        
        await update.message.reply_text(
            "🛑 **Working Bot Stopped**\n\n"
            "The working userbot has been terminated.\n"
            "Use /free and then start it again to reactivate.",
            parse_mode='Markdown'
        )
        
        logger.info(f"Working bot stopped by command from @{update.effective_user.username}")
        
    except FileNotFoundError:
        await update.message.reply_text("❌ Working bot is not running")
    except Exception as e:
        logger.error(f"Error stopping working bot: {e}")
        await update.message.reply_text("❌ Failed to stop working bot")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline button callbacks"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "set_free":
        if set_mode("free"):
            await query.edit_message_text(
                "🟢 **FREE MODE Activated**\n\n"
                "Working bot will now respond to messages.",
                parse_mode='Markdown'
            )
        else:
            await query.edit_message_text("❌ Failed to set mode")
    
    elif query.data == "set_busy":
        if set_mode("busy"):
            await query.edit_message_text(
                "🔴 **BUSY MODE Activated**\n\n"
                "Working bot will now ignore messages.",
                parse_mode='Markdown'
            )
        else:
            await query.edit_message_text("❌ Failed to set mode")

def main():
    """Main function to run the bot"""
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN not found in environment variables")
        sys.exit(1)
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("status", status))
    application.add_handler(CommandHandler("free", set_free_mode))
    application.add_handler(CommandHandler("busy", set_busy_mode))
    application.add_handler(CommandHandler("stop", stop_bot))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Start bot
    logger.info(f"Starting @{BOT_USERNAME}...")
    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
