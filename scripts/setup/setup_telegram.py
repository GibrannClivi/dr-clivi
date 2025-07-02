#!/usr/bin/env python3
"""
Dr. Clivi Telegram Bot - Quick Setup Script
Configures Telegram bot for development testing.
"""

import os
import sys
import asyncio
import httpx
from typing import Optional


def print_step(step: int, message: str):
    """Print a numbered setup step"""
    print(f"\n{step}. {message}")


def print_success(message: str):
    """Print a success message"""
    print(f"✅ {message}")


def print_error(message: str):
    """Print an error message"""
    print(f"❌ {message}")


def print_info(message: str):
    """Print an info message"""
    print(f"ℹ️  {message}")


async def check_telegram_bot(bot_token: str) -> bool:
    """Test if the bot token is valid"""
    try:
        url = f"https://api.telegram.org/bot{bot_token}/getMe"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            result = response.json()
            
            if result.get("ok"):
                bot_info = result.get("result", {})
                print_success(f"Bot token is valid: @{bot_info.get('username', 'unknown')}")
                return True
            else:
                print_error(f"Invalid bot token: {result}")
                return False
                
    except Exception as e:
        print_error(f"Error checking bot token: {e}")
        return False


async def set_telegram_webhook(bot_token: str, webhook_url: str) -> bool:
    """Configure webhook with Telegram"""
    try:
        url = f"https://api.telegram.org/bot{bot_token}/setWebhook"
        data = {
            "url": f"{webhook_url}/telegram/webhook",
            "drop_pending_updates": True
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data)
            response.raise_for_status()
            result = response.json()
            
            if result.get("ok"):
                print_success(f"Webhook configured: {webhook_url}/telegram/webhook")
                return True
            else:
                print_error(f"Failed to set webhook: {result}")
                return False
                
    except Exception as e:
        print_error(f"Error setting webhook: {e}")
        return False


def check_env_file() -> bool:
    """Check if .env file exists and has required variables"""
    env_path = ".env"
    
    if not os.path.exists(env_path):
        print_error(".env file not found")
        return False
    
    # Read .env file
    env_vars = {}
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env_vars[key] = value
    
    # Check required variables
    required_vars = ['GOOGLE_API_KEY', 'TELEGRAM_BOT_TOKEN']
    missing_vars = []
    
    for var in required_vars:
        if var not in env_vars or env_vars[var] in ['', 'your_api_key_here', 'your_telegram_bot_token_here']:
            missing_vars.append(var)
    
    if missing_vars:
        print_error(f"Missing or unconfigured variables in .env: {', '.join(missing_vars)}")
        return False
    
    print_success(".env file is properly configured")
    return True


async def main():
    """Main setup process"""
    print("🤖 Dr. Clivi Telegram Bot - Quick Setup")
    print("=====================================")
    
    # Step 1: Check .env file
    print_step(1, "Checking environment configuration...")
    
    if not check_env_file():
        print()
        print_info("Please complete the following steps:")
        print("   1. Copy .env.example to .env")
        print("   2. Get a Telegram bot token from @BotFather")
        print("   3. Get a Google AI Studio API key from https://aistudio.google.com")
        print("   4. Configure both tokens in your .env file")
        return
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    google_api_key = os.getenv("GOOGLE_API_KEY")
    webhook_url = os.getenv("TELEGRAM_WEBHOOK_URL", "")
    
    # Step 2: Test bot token
    print_step(2, "Validating Telegram bot token...")
    
    if not await check_telegram_bot(bot_token):
        print_info("Please check your TELEGRAM_BOT_TOKEN in .env file")
        return
    
    # Step 3: Check webhook URL (optional for local development)
    print_step(3, "Checking webhook configuration...")
    
    if webhook_url and webhook_url != "https://your-ngrok-url.ngrok.io/telegram/webhook":
        print_info(f"Webhook URL configured: {webhook_url}")
        
        # Try to set webhook
        if await set_telegram_webhook(bot_token, webhook_url):
            print_success("Webhook is ready for production testing")
        else:
            print_error("Failed to configure webhook")
    else:
        print_info("No webhook URL configured (OK for local development)")
        print_info("For production testing, configure TELEGRAM_WEBHOOK_URL in .env")
    
    # Step 4: Test dependencies
    print_step(4, "Checking dependencies...")
    
    try:
        import google.generativeai as genai
        genai.configure(api_key=google_api_key)
        print_success("Google AI Studio connection ready")
    except Exception as e:
        print_error(f"Google AI Studio error: {e}")
        return
    
    try:
        from dr_clivi.config import Config
        config = Config()
        print_success("Dr. Clivi configuration loaded")
    except Exception as e:
        print_error(f"Configuration error: {e}")
        return
    
    # Success!
    print()
    print("🎉 Setup Complete!")
    print("=================")
    print()
    print("Next steps:")
    print("1. Start the bot: python telegram_main.py")
    print("2. For local testing: Use polling mode or ngrok for webhooks")
    print("3. For production: Configure TELEGRAM_WEBHOOK_URL and deploy")
    print()
    print("Bot features:")
    print("✅ Hybrid architecture (deterministic + AI)")
    print("✅ Medical specialization (diabetes, obesity)")
    print("✅ Emergency detection")
    print("✅ Interactive menus via inline keyboards")
    print("✅ Session management")
    print()


if __name__ == "__main__":
    asyncio.run(main())
