#!/usr/bin/env python3
"""
Dr. Clivi Telegram Bot - Main Entry Point
Prioritizes Telegram for development and testing while keeping WhatsApp for production.
"""

import asyncio
import logging
import os
import sys
from typing import Dict, Any

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import uvicorn

# Load environment variables first
from dotenv import load_dotenv
load_dotenv()

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dr_clivi.config import Config
from dr_clivi.telegram.telegram_handler import TelegramBotHandler


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Dr. Clivi Telegram Bot",
    description="Hybrid architecture bot for medical assistance via Telegram",
    version="1.0.0"
)

# Global handler instance
telegram_handler: TelegramBotHandler = None


@app.on_event("startup")
async def startup_event():
    """Initialize the application"""
    global telegram_handler
    
    # Load configuration
    config = Config()
    
    # Validate Telegram configuration
    if not config.telegram.bot_token:
        logger.error("TELEGRAM_BOT_TOKEN not configured! Set it in .env file")
        sys.exit(1)
    
    # Initialize handlers
    telegram_handler = TelegramBotHandler(config)
    
    logger.info("Dr. Clivi Telegram Bot initialized successfully")
    logger.info(f"Ready to receive webhooks for bot token: {config.telegram.bot_token[:10]}...")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "active",
        "service": "Dr. Clivi Telegram Bot",
        "version": "1.0.0",
        "description": "Hybrid medical assistance bot using ADK architecture"
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    global telegram_handler
    
    return {
        "status": "healthy",
        "telegram_configured": telegram_handler is not None,
        "services": {
            "coordinator": "active",
            "deterministic_flow": "active", 
            "telegram_api": "connected"
        }
    }


@app.post("/telegram/webhook")
async def telegram_webhook(request: Request):
    """
    Main webhook endpoint for Telegram Bot API.
    Processes all incoming updates and routes them through our hybrid architecture.
    """
    try:
        update_data = await request.json()
        logger.info(f"Received Telegram update: {update_data.get('update_id', 'unknown')}")
        
        if not telegram_handler:
            raise HTTPException(status_code=500, detail="Telegram handler not initialized")
        
        # Process the update through our hybrid architecture
        result = await telegram_handler.process_telegram_update(update_data)
        
        return JSONResponse(content={
            "status": "success",
            "result": result
        })
        
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        raise HTTPException(status_code=500, detail=f"Webhook processing error: {e}")


@app.post("/telegram/set_webhook")
async def set_telegram_webhook():
    """
    Helper endpoint to configure the webhook URL with Telegram.
    Call this once to register your ngrok URL with Telegram.
    """
    try:
        config = Config()
        
        if not config.telegram.webhook_url:
            raise HTTPException(status_code=400, detail="TELEGRAM_WEBHOOK_URL not configured")
        
        import httpx
        
        # Set webhook with Telegram
        telegram_api_url = f"https://api.telegram.org/bot{config.telegram.bot_token}/setWebhook"
        webhook_data = {
            "url": f"{config.telegram.webhook_url}/telegram/webhook",
            "drop_pending_updates": True
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(telegram_api_url, json=webhook_data)
            response.raise_for_status()
            result = response.json()
        
        if result.get("ok"):
            logger.info(f"Webhook successfully configured: {config.telegram.webhook_url}")
            return {
                "status": "success",
                "webhook_url": f"{config.telegram.webhook_url}/telegram/webhook",
                "telegram_response": result
            }
        else:
            logger.error(f"Failed to set webhook: {result}")
            raise HTTPException(status_code=400, detail=f"Telegram API error: {result}")
            
    except Exception as e:
        logger.error(f"Error setting webhook: {e}")
        raise HTTPException(status_code=500, detail=f"Webhook configuration error: {e}")


@app.delete("/telegram/webhook")
async def delete_telegram_webhook():
    """Helper endpoint to remove the webhook (for testing)"""
    try:
        config = Config()
        
        import httpx
        
        telegram_api_url = f"https://api.telegram.org/bot{config.telegram.bot_token}/deleteWebhook"
        
        async with httpx.AsyncClient() as client:
            response = await client.post(telegram_api_url)
            response.raise_for_status()
            result = response.json()
        
        logger.info("Webhook deleted successfully")
        return {
            "status": "success",
            "message": "Webhook deleted",
            "telegram_response": result
        }
        
    except Exception as e:
        logger.error(f"Error deleting webhook: {e}")
        raise HTTPException(status_code=500, detail=f"Webhook deletion error: {e}")


if __name__ == "__main__":
    # Check for required environment variables
    if not os.getenv("TELEGRAM_BOT_TOKEN"):
        print("❌ Error: TELEGRAM_BOT_TOKEN not found in environment")
        print("Please copy .env.example to .env and configure your Telegram bot token")
        print("Get a token from @BotFather on Telegram")
        sys.exit(1)
    
    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ Error: GOOGLE_API_KEY not found in environment")
        print("Please get an API key from https://aistudio.google.com")
        sys.exit(1)
    
    print("🤖 Starting Dr. Clivi Telegram Bot...")
    print("📱 Ready for Telegram integration")
    print("🏥 Hybrid medical assistance with ADK architecture")
    print("")
    print("Available endpoints:")
    print("  GET  /health - Health check")
    print("  POST /telegram/webhook - Main webhook (configure with Telegram)")
    print("  POST /telegram/set_webhook - Helper to configure webhook")
    print("  DELETE /telegram/webhook - Helper to remove webhook")
    print("")
    
    # Start the server
    uvicorn.run(
        "telegram_main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Enable for development
        log_level="info"
    )
