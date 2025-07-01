"""
Telegram Bot Handler - Adaptation of WhatsApp webhook for Telegram Bot API
Reuses the entire hybrid architecture with minimal changes.
"""

import logging
from typing import Any, Dict, Optional, List
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import asyncio
import httpx

from ..agents.coordinator import IntelligentCoordinator
from ..config import Config

logger = logging.getLogger(__name__)

app = FastAPI(title="Dr. Clivi Telegram Bot")


class TelegramBotHandler:
    """
    Handles Telegram Bot API webhooks and routes messages appropriately.
    
    Reuses the entire hybrid architecture:
    - DeterministicFlowHandler for structured menu interactions
    - IntelligentCoordinator for complex medical queries
    - Emergency detection and specialist routing
    """
    
    def __init__(self, config: Config):
        self.config = config
        self.coordinator = IntelligentCoordinator(config)
        self.bot_token = config.telegram.bot_token
        self.telegram_api_url = f"https://api.telegram.org/bot{self.bot_token}"
    
    async def process_telegram_update(self, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process incoming Telegram webhook update.
        """
        try:
            # Handle different update types
            if 'message' in update_data:
                return await self._handle_message(update_data['message'])
            elif 'callback_query' in update_data:
                return await self._handle_callback_query(update_data['callback_query'])
            else:
                logger.info(f"Unhandled update type: {update_data}")
                return {"status": "ignored", "reason": "unknown_update_type"}
                
        except Exception as e:
            logger.error(f"Error processing Telegram update: {e}")
            raise HTTPException(status_code=500, detail=f"Update processing error: {e}")
    
    async def _handle_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming text messages"""
        user_id = str(message.get('from', {}).get('id'))
        chat_id = str(message.get('chat', {}).get('id'))
        text = message.get('text', '')
        
        logger.info(f"Processing message from user {user_id}: {text}")
        
        # Process through the hybrid coordinator (reusing all existing logic)
        response = await self.coordinator.process_user_input(
            user_id=user_id,
            user_input=text,
            phone_number=None  # Telegram doesn't require phone
        )
        
        # Send response back to user
        await self._send_response_to_user(chat_id, response)
        
        return {
            "status": "processed",
            "message_id": message.get('message_id'),
            "response_type": response.get("response_type"),
            "routing_type": response.get("routing_type")
        }
    
    async def _handle_callback_query(self, callback_query: Dict[str, Any]) -> Dict[str, Any]:
        """Handle inline keyboard button clicks"""
        user_id = str(callback_query.get('from', {}).get('id'))
        chat_id = str(callback_query.get('message', {}).get('chat', {}).get('id'))
        data = callback_query.get('data', '')
        
        logger.info(f"Processing callback from user {user_id}: {data}")
        
        # Answer the callback query to remove loading state
        await self._answer_callback_query(callback_query.get('id'))
        
        # Process the selection through coordinator
        response = await self.coordinator.process_user_input(
            user_id=user_id,
            user_input=data,  # Button data acts as user input
            phone_number=None
        )
        
        # Send response
        await self._send_response_to_user(chat_id, response)
        
        return {
            "status": "processed", 
            "callback_query_id": callback_query.get('id'),
            "response_type": response.get("response_type"),
            "routing_type": response.get("routing_type")
        }
    
    async def _send_response_to_user(self, chat_id: str, response: Dict[str, Any]) -> bool:
        """
        Send response back to user via Telegram Bot API.
        Adapts the hybrid coordinator responses to Telegram format.
        """
        try:
            response_type = response.get("response_type")
            logger.info(f"Sending response type '{response_type}' to chat {chat_id}")
            logger.debug(f"Full response: {response}")
            
            if response_type == "whatsapp_menu":
                # Convert WhatsApp menu to Telegram inline keyboard
                return await self._send_telegram_menu(chat_id, response)
            elif response_type == "page_navigation":
                # Handle page navigation by showing the target page menu
                return await self._handle_page_navigation(chat_id, response)
            elif response_type == "specialist_response":
                return await self._send_text_message(chat_id, response.get("response", {}).get("message", ""))
            elif response_type == "emergency":
                return await self._send_emergency_message(chat_id, response)
            elif response_type == "general_response":
                return await self._send_text_message(chat_id, response.get("response", ""))
            else:
                # Fallback
                logger.warning(f"Unknown response type: {response_type}, using fallback")
                return await self._send_text_message(chat_id, "Disculpa, ocurrió un error. ¿Puedes intentar de nuevo?")
                
        except Exception as e:
            logger.error(f"Error sending response to {chat_id}: {e}")
            return False
    
    async def _send_telegram_menu(self, chat_id: str, response: Dict[str, Any]) -> bool:
        """Convert WhatsApp interactive menu to Telegram inline keyboard"""
        try:
            menu_data = response.get("menu_data", {})
            interactive = menu_data.get("interactive", {})
            body_text = interactive.get("body", {}).get("text", "¿Cómo puedo ayudarte?")
            
            # Convert WhatsApp menu sections to Telegram inline keyboard
            sections = interactive.get("action", {}).get("sections", [])
            inline_keyboard = []
            
            for section in sections:
                for row in section.get("rows", []):
                    button = [{
                        "text": f"{row.get('title', '')} {row.get('description', '')}"[:64],
                        "callback_data": row.get('id', '')[:64]
                    }]
                    inline_keyboard.append(button)
            
            # Split into chunks of 2 buttons per row for better UX
            chunked_keyboard = []
            for i in range(0, len(inline_keyboard), 2):
                chunk = inline_keyboard[i:i+2]
                if len(chunk) == 2:
                    # Combine two buttons in one row
                    chunked_keyboard.append([chunk[0][0], chunk[1][0]])
                else:
                    chunked_keyboard.append(chunk[0])
            
            payload = {
                "chat_id": chat_id,
                "text": body_text,
                "reply_markup": {
                    "inline_keyboard": chunked_keyboard
                }
            }
            
            return await self._make_telegram_api_call("sendMessage", payload)
            
        except Exception as e:
            logger.error(f"Error sending Telegram menu to {chat_id}: {e}")
            return False
    
    async def _send_text_message(self, chat_id: str, text: str) -> bool:
        """Send simple text message"""
        try:
            payload = {
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "Markdown"
            }
            
            return await self._make_telegram_api_call("sendMessage", payload)
            
        except Exception as e:
            logger.error(f"Error sending text to {chat_id}: {e}")
            return False
    
    async def _send_emergency_message(self, chat_id: str, response: Dict[str, Any]) -> bool:
        """Send emergency response with priority formatting"""
        try:
            immediate_actions = response.get("immediate_actions", [])
            emergency_text = "\n".join(immediate_actions)
            
            # Format as emergency with emoji and markdown
            formatted_text = f"🚨 **EMERGENCIA MÉDICA** 🚨\n\n{emergency_text}"
            
            logger.critical(f"Sending EMERGENCY message to Telegram chat {chat_id}")
            
            payload = {
                "chat_id": chat_id,
                "text": formatted_text,
                "parse_mode": "Markdown"
            }
            
            return await self._make_telegram_api_call("sendMessage", payload)
            
        except Exception as e:
            logger.error(f"Error sending emergency message to {chat_id}: {e}")
            return False
    
    async def _handle_page_navigation(self, chat_id: str, page_data: Dict[str, Any]) -> bool:
        """
        Maneja la navegación de páginas para menús largos en Telegram usando inline keyboard.
        page_data debe contener:
            - 'body_text': texto del menú
            - 'inline_keyboard': lista de botones (ya paginados)
        """
        try:
            body_text = page_data.get("body_text", "¿Cómo puedo ayudarte?")
            inline_keyboard = page_data.get("inline_keyboard", [])

            payload = {
                "chat_id": chat_id,
                "text": body_text,
                "reply_markup": {
                    "inline_keyboard": inline_keyboard
                },
                "parse_mode": "Markdown"
            }
            logger.info(f"Enviando menú paginado a chat {chat_id}")
            return await self._make_telegram_api_call("sendMessage", payload)
        except Exception as e:
            logger.error(f"Error enviando menú paginado a {chat_id}: {e}")
            return False
    
    async def _answer_callback_query(self, callback_query_id: str) -> bool:
        """Answer callback query to remove loading state"""
        try:
            payload = {
                "callback_query_id": callback_query_id
            }
            
            return await self._make_telegram_api_call("answerCallbackQuery", payload)
            
        except Exception as e:
            logger.error(f"Error answering callback query {callback_query_id}: {e}")
            return False
    
    async def _make_telegram_api_call(self, method: str, payload: Dict[str, Any]) -> bool:
        """Make API call to Telegram Bot API"""
        try:
            url = f"{self.telegram_api_url}/{method}"
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload)
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("ok"):
                        logger.debug(f"Telegram API call {method} successful")
                        return True
                    else:
                        logger.error(f"Telegram API error for {method}: {result}")
                        return False
                else:
                    logger.error(f"Telegram API HTTP error for {method}: {response.status_code}")
                    logger.error(f"Response body: {response.text}")
                    logger.error(f"Payload sent: {payload}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error making Telegram API call {method}: {e}")
            return False
    
    async def set_webhook(self, webhook_url: str) -> bool:
        """Set webhook URL for the bot"""
        try:
            payload = {
                "url": f"{webhook_url}/telegram-webhook"
            }
            
            return await self._make_telegram_api_call("setWebhook", payload)
            
        except Exception as e:
            logger.error(f"Error setting webhook: {e}")
            return False
    
    async def get_bot_info(self) -> Dict[str, Any]:
        """Get bot information"""
        try:
            url = f"{self.telegram_api_url}/getMe"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return {"error": f"HTTP {response.status_code}"}
                    
        except Exception as e:
            logger.error(f"Error getting bot info: {e}")
            return {"error": str(e)}


# FastAPI webhook endpoints for Telegram
telegram_handler = None

def init_telegram_handler(config: Config):
    """Initialize Telegram handler with config"""
    global telegram_handler
    telegram_handler = TelegramBotHandler(config)

@app.post("/telegram-webhook")
async def receive_telegram_webhook(request: Request):
    """Receive webhook updates from Telegram"""
    global telegram_handler
    
    if not telegram_handler:
        raise HTTPException(status_code=500, detail="Telegram handler not initialized")
    
    # Parse JSON
    try:
        update_data = await request.json()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {e}")
    
    # Process update
    result = await telegram_handler.process_telegram_update(update_data)
    
    return JSONResponse(content={"status": "success", "result": result})

@app.get("/telegram-bot-info")
async def get_telegram_bot_info():
    """Get Telegram bot information"""
    global telegram_handler
    
    if not telegram_handler:
        raise HTTPException(status_code=500, detail="Telegram handler not initialized")
    
    bot_info = await telegram_handler.get_bot_info()
    return JSONResponse(content=bot_info)

@app.post("/set-telegram-webhook")
async def set_telegram_webhook(webhook_data: Dict[str, str]):
    """Set Telegram webhook URL"""
    global telegram_handler
    
    if not telegram_handler:
        raise HTTPException(status_code=500, detail="Telegram handler not initialized")
    
    webhook_url = webhook_data.get("webhook_url")
    if not webhook_url:
        raise HTTPException(status_code=400, detail="webhook_url required")
    
    success = await telegram_handler.set_webhook(webhook_url)
    
    return JSONResponse(content={
        "success": success,
        "webhook_url": webhook_url
    })

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "dr-clivi-telegram-bot"}

if __name__ == "__main__":
    import uvicorn
    # Load config and initialize
    config = Config()
    init_telegram_handler(config)
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        log_level="info"
    )
