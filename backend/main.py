"""
ZarbdorUn E-commerce Platform - Main Entry Point
Runs both Telegram Bot and FastAPI server concurrently
Windows Compatible - UTF-8 Encoding Support
"""

import asyncio
import logging
import os
import sys
from contextlib import asynccontextmanager

import uvicorn
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from fastapi import FastAPI

from config import BOT_TOKEN, API_HOST, API_PORT, UPLOAD_DIR
from database import init_db
from bot.handlers import register_all_handlers

# Windows compatibility and UTF-8 encoding fix
if sys.platform == 'win32':
    # Fix UTF-8 encoding for emoji support
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    # Use WindowsSelectorEventLoopPolicy for Windows
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('zarbdor.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)


# Global variables for bot and API
bot = None
dp = None
api_server = None


def create_uploads_directory():
    """Create uploads directory if it doesn't exist"""
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    logger.info(f"✅ Uploads directory ready: {UPLOAD_DIR}")


async def init_bot():
    """Initialize Telegram bot with handlers"""
    global bot, dp
    
    try:
        # Create bot instance with DefaultBotProperties (Aiogram 3.x)
        bot = Bot(
            token=BOT_TOKEN, 
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
        
        # Create dispatcher
        dp = Dispatcher()
        
        # Register all handlers
        register_all_handlers(dp)
        
        logger.info("✅ Telegram bot initialized successfully")
        return bot, dp
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize bot: {e}")
        raise


async def run_bot():
    """Run Telegram bot with polling"""
    global bot, dp
    
    try:
        logger.info("🤖 Starting Telegram bot polling...")
        
        # Delete webhook to use polling
        await bot.delete_webhook(drop_pending_updates=True)
        
        # Start polling
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
        
    except asyncio.CancelledError:
        logger.info("🛑 Bot polling stopped")
    except Exception as e:
        logger.error(f"❌ Bot error: {e}")
        raise
    finally:
        if bot:
            await bot.session.close()


async def run_api():
    """Run FastAPI server with uvicorn"""
    global api_server
    
    try:
        # Import FastAPI app
        from api.main import app
        
        # Configure uvicorn
        config = uvicorn.Config(
            app=app,
            host=API_HOST,
            port=API_PORT,
            log_level="info",
            access_log=True
        )
        
        api_server = uvicorn.Server(config)
        
        logger.info(f"🌐 Starting FastAPI server on {API_HOST}:{API_PORT}...")
        
        # Run server
        await api_server.serve()
        
    except asyncio.CancelledError:
        logger.info("🛑 API server stopped")
    except Exception as e:
        logger.error(f"❌ API server error: {e}")
        raise


async def shutdown():
    """Graceful shutdown handler"""
    logger.info("🛑 Shutting down gracefully...")
    
    # Stop bot
    if dp:
        await dp.stop_polling()
    
    if bot:
        await bot.session.close()
    
    # Stop API server
    if api_server:
        api_server.should_exit = True
    
    logger.info("✅ Shutdown complete")


async def main():
    """Main entry point - runs both bot and API concurrently"""
    try:
        # Initialize database
        logger.info("📦 Initializing database...")
        init_db()
        logger.info("✅ Database initialized")
        
        # Create uploads directory
        create_uploads_directory()
        
        # Initialize bot
        await init_bot()
        
        # Run both bot and API concurrently
        logger.info("🚀 Starting ZarbdorUn E-commerce Platform...")
        logger.info("=" * 60)
        
        tasks = [
            asyncio.create_task(run_bot(), name="telegram_bot"),
            asyncio.create_task(run_api(), name="fastapi_server")
        ]
        
        # Wait for tasks to complete
        await asyncio.gather(*tasks, return_exceptions=True)
        
    except KeyboardInterrupt:
        logger.info("⌨️  Keyboard interrupt received")
        await shutdown()
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}", exc_info=True)
        await shutdown()
        sys.exit(1)
    finally:
        logger.info("👋 Application terminated")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Goodbye!")
