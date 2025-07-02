#!/usr/bin/env python3
"""
Dr. Clivi Telegram Bot - Modo Polling (Sin webhook)
Ideal para desarrollo y testing local sin necesidad de ngrok
"""

import asyncio
import logging
import os
import sys
from typing import Dict, Any

# Add project root to path for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
os.chdir(project_root)  # Change to project root to find .env

from dr_clivi.config import Config
from dr_clivi.telegram.telegram_handler import TelegramBotHandler


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TelegramPollingBot:
    """
    Bot de Telegram en modo polling (sin webhooks)
    Perfecto para desarrollo y testing local
    """
    
    def __init__(self, config: Config):
        self.config = config
        self.handler = TelegramBotHandler(config)
        self.bot_token = config.telegram.bot_token
        self.running = False
        
    async def get_updates(self, offset: int = None):
        """Obtener updates de Telegram API"""
        import httpx
        
        url = f"https://api.telegram.org/bot{self.bot_token}/getUpdates"
        params = {
            "timeout": 30,  # Long polling
            "limit": 100
        }
        
        if offset:
            params["offset"] = offset
            
        try:
            async with httpx.AsyncClient(timeout=35) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error getting updates: {e}")
            return None
    
    async def process_update(self, update: Dict[str, Any]):
        """Procesar un update individual"""
        try:
            update_id = update.get("update_id")
            logger.info(f"Processing update {update_id}")
            
            # Usar el handler existente
            result = await self.handler.process_telegram_update(update)
            logger.info(f"Update {update_id} processed: {result.get('status', 'unknown')}")
            
        except Exception as e:
            logger.error(f"Error processing update {update.get('update_id')}: {e}")
    
    async def start_polling(self):
        """Iniciar polling loop"""
        logger.info("🤖 Starting Telegram bot in POLLING mode...")
        logger.info("✅ No webhook required - perfect for local development")
        logger.info("📱 Your bot is ready to receive messages!")
        logger.info("🛑 Press Ctrl+C to stop")
        
        self.running = True
        offset = None
        
        while self.running:
            try:
                # Obtener updates
                data = await self.get_updates(offset)
                
                if not data or not data.get("ok"):
                    logger.warning("No data received from Telegram")
                    await asyncio.sleep(1)
                    continue
                
                updates = data.get("result", [])
                
                if updates:
                    logger.info(f"📨 Received {len(updates)} update(s)")
                    
                    # Procesar cada update
                    for update in updates:
                        await self.process_update(update)
                        offset = update["update_id"] + 1
                else:
                    # No hay updates nuevos
                    await asyncio.sleep(0.1)
                    
            except KeyboardInterrupt:
                logger.info("🛑 Stopping bot...")
                self.running = False
                break
            except Exception as e:
                logger.error(f"Error in polling loop: {e}")
                await asyncio.sleep(5)  # Wait before retrying
    
    def stop(self):
        """Detener el bot"""
        self.running = False


async def main():
    """Main function"""
    # Check for required environment variables
    if not os.getenv("TELEGRAM_BOT_TOKEN"):
        print("❌ Error: TELEGRAM_BOT_TOKEN not found in environment")
        print("Please configure your .env file with your Telegram bot token")
        print("Get a token from @BotFather on Telegram")
        sys.exit(1)
    
    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ Error: GOOGLE_API_KEY not found in environment")
        print("Please get an API key from https://aistudio.google.com")
        sys.exit(1)
    
    # Initialize configuration
    config = Config()
    
    # Initialize bot
    bot = TelegramPollingBot(config)
    
    print("🏥 Dr. Clivi Telegram Bot - Polling Mode")
    print("=" * 45)
    print("✅ Google AI Studio configured")
    print("✅ Telegram bot configured")
    print("✅ Hybrid architecture ready")
    print("📱 Bot ready for testing!")
    print()
    print("How to test:")
    print("1. Open Telegram")
    print("2. Search for your bot")
    print("3. Send /start or 'hola'")
    print("4. Try the interactive menu!")
    print()
    
    try:
        await bot.start_polling()
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
    except Exception as e:
        print(f"\n❌ Bot error: {e}")
    finally:
        bot.stop()


if __name__ == "__main__":
    asyncio.run(main())
