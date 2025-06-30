"""
WhatsApp Business API Webhook Handler
Manages incoming messages and routes between deterministic flows and intelligent routing.
"""

import logging
from typing import Any, Dict, Optional
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import hmac
import hashlib
import asyncio

from ..agents.coordinator import IntelligentCoordinator
from ..config import Config

logger = logging.getLogger(__name__)

app = FastAPI(title="Dr. Clivi WhatsApp Webhook")


class WhatsAppWebhookHandler:
    """
    Handles WhatsApp Business API webhooks and routes messages appropriately.
    
    Supports:
    - Message verification (Meta webhook security)
    - Text message processing
    - Interactive message handling (button selections)
    - Status updates and delivery receipts
    """
    
    def __init__(self, config: Config):
        self.config = config
        self.coordinator = IntelligentCoordinator(config)
        self.verify_token = config.whatsapp.verify_token
        self.app_secret = config.whatsapp.app_secret
    
    def verify_signature(self, payload: bytes, signature: str) -> bool:
        """Verify webhook signature from Meta"""
        if not self.app_secret:
            logger.warning("No app secret configured - skipping signature verification")
            return True
            
        expected_signature = hmac.new(
            self.app_secret.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(f"sha256={expected_signature}", signature)
    
    async def process_webhook_message(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process incoming WhatsApp webhook message.
        """
        try:
            # Extract message data
            entry = webhook_data.get('entry', [{}])[0]
            changes = entry.get('changes', [{}])[0]
            value = changes.get('value', {})
            
            # Handle different webhook types
            if 'messages' in value:
                return await self._handle_incoming_message(value)
            elif 'statuses' in value:
                return await self._handle_status_update(value)
            else:
                logger.info(f"Unhandled webhook type: {webhook_data}")
                return {"status": "ignored", "reason": "unknown_webhook_type"}
                
        except Exception as e:
            logger.error(f"Error processing webhook: {e}")
            raise HTTPException(status_code=500, detail=f"Webhook processing error: {e}")
    
    async def _handle_incoming_message(self, value: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming text or interactive messages"""
        messages = value.get('messages', [])
        
        for message in messages:
            user_phone = message.get('from')
            message_id = message.get('id')
            message_type = message.get('type')
            
            logger.info(f"Processing {message_type} message from {user_phone}")
            
            # Extract message content based on type
            if message_type == 'text':
                user_input = message.get('text', {}).get('body', '')
            elif message_type == 'interactive':
                # Handle button/list selections
                interactive_data = message.get('interactive', {})
                if interactive_data.get('type') == 'list_reply':
                    user_input = interactive_data.get('list_reply', {}).get('id', '')
                elif interactive_data.get('type') == 'button_reply':
                    user_input = interactive_data.get('button_reply', {}).get('id', '')
                else:
                    user_input = 'interactive_message'
            else:
                logger.warning(f"Unsupported message type: {message_type}")
                continue
            
            # Process through coordinator
            response = await self.coordinator.process_user_input(
                user_id=user_phone,
                user_input=user_input,
                phone_number=user_phone
            )
            
            # Send response back to user
            await self._send_response_to_user(user_phone, response)
            
            return {
                "status": "processed",
                "message_id": message_id,
                "response_type": response.get("response_type"),
                "routing_type": response.get("routing_type")
            }
    
    async def _handle_status_update(self, value: Dict[str, Any]) -> Dict[str, Any]:
        """Handle message status updates (delivered, read, etc.)"""
        statuses = value.get('statuses', [])
        
        for status in statuses:
            message_id = status.get('id')
            status_type = status.get('status')
            recipient_id = status.get('recipient_id')
            
            logger.info(f"Message {message_id} status: {status_type} for {recipient_id}")
            
            # Log for analytics (delivery rates, read rates, etc.)
            # Could update database with delivery status
        
        return {"status": "status_logged"}
    
    async def _send_response_to_user(self, phone_number: str, response: Dict[str, Any]) -> bool:
        """
        Send response back to user via WhatsApp Business API.
        """
        try:
            response_type = response.get("response_type")
            
            if response_type == "whatsapp_menu":
                return await self._send_interactive_menu(phone_number, response)
            elif response_type == "specialist_response":
                return await self._send_text_message(phone_number, response.get("response", {}).get("message", ""))
            elif response_type == "emergency":
                return await self._send_emergency_message(phone_number, response)
            elif response_type == "general_response":
                return await self._send_text_message(phone_number, response.get("response", ""))
            else:
                # Fallback text message
                return await self._send_text_message(phone_number, "Disculpa, ocurrió un error. ¿Puedes intentar de nuevo?")
                
        except Exception as e:
            logger.error(f"Error sending response to {phone_number}: {e}")
            return False
    
    async def _send_interactive_menu(self, phone_number: str, response: Dict[str, Any]) -> bool:
        """Send WhatsApp interactive menu"""
        try:
            menu_data = response.get("menu_data", {})
            
            # This would make the actual API call to WhatsApp Business API
            # For now, we'll log it
            logger.info(f"Sending interactive menu to {phone_number}: {menu_data}")
            
            # Simulate API call
            await asyncio.sleep(0.1)
            return True
            
        except Exception as e:
            logger.error(f"Error sending menu to {phone_number}: {e}")
            return False
    
    async def _send_text_message(self, phone_number: str, message: str) -> bool:
        """Send simple text message"""
        try:
            # This would make the actual API call to WhatsApp Business API
            logger.info(f"Sending text to {phone_number}: {message}")
            
            # Simulate API call
            await asyncio.sleep(0.1)
            return True
            
        except Exception as e:
            logger.error(f"Error sending text to {phone_number}: {e}")
            return False
    
    async def _send_emergency_message(self, phone_number: str, response: Dict[str, Any]) -> bool:
        """Send emergency response with priority"""
        try:
            immediate_actions = response.get("immediate_actions", [])
            emergency_text = "\n".join(immediate_actions)
            
            logger.critical(f"Sending EMERGENCY message to {phone_number}")
            
            # This would use priority/urgent message API if available
            return await self._send_text_message(phone_number, emergency_text)
            
        except Exception as e:
            logger.error(f"Error sending emergency message to {phone_number}: {e}")
            return False


# FastAPI webhook endpoints
webhook_handler = None

def init_webhook_handler(config: Config):
    """Initialize webhook handler with config"""
    global webhook_handler
    webhook_handler = WhatsAppWebhookHandler(config)

@app.get("/webhook")
async def verify_webhook(request: Request):
    """Webhook verification endpoint for Meta"""
    global webhook_handler
    
    if not webhook_handler:
        raise HTTPException(status_code=500, detail="Webhook handler not initialized")
    
    # Meta sends these parameters for verification
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token") 
    challenge = request.query_params.get("hub.challenge")
    
    if mode == "subscribe" and token == webhook_handler.verify_token:
        logger.info("Webhook verified successfully")
        return JSONResponse(content=int(challenge))
    else:
        logger.warning("Webhook verification failed")
        raise HTTPException(status_code=403, detail="Verification failed")

@app.post("/webhook")
async def receive_webhook(request: Request):
    """Receive webhook messages from WhatsApp"""
    global webhook_handler
    
    if not webhook_handler:
        raise HTTPException(status_code=500, detail="Webhook handler not initialized")
    
    # Get request body
    body = await request.body()
    
    # Verify signature (optional but recommended)
    signature = request.headers.get("X-Hub-Signature-256", "")
    if not webhook_handler.verify_signature(body, signature):
        logger.warning("Invalid webhook signature")
        raise HTTPException(status_code=403, detail="Invalid signature")
    
    # Parse JSON
    try:
        webhook_data = await request.json()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {e}")
    
    # Process webhook
    result = await webhook_handler.process_webhook_message(webhook_data)
    
    return JSONResponse(content={"status": "success", "result": result})

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "dr-clivi-whatsapp-webhook"}

if __name__ == "__main__":
    import uvicorn
    # Load config and initialize
    config = Config()
    init_webhook_handler(config)
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        log_level="info"
    )
