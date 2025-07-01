"""
Telegram Handler Optimizado - Versión refactorizada más corta y eficiente
"""

import logging
from typing import Any, Dict
from functools import wraps

from ..agents.coordinator import IntelligentCoordinator
from ..config import Config
from .api_client import TelegramAPIClient
from .message_formatter import MessageFormatter

logger = logging.getLogger(__name__)


def handle_errors(func):
    """Decorador para manejo centralizado de errores"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}")
            return False
    return wrapper


class TelegramHandlerOptimized:
    """
    Handler de Telegram optimizado - 90% menos código haciendo lo mismo
    """
    
    # Mapeo de tipos de respuesta a métodos
    RESPONSE_HANDLERS = {
        "whatsapp_menu": "_send_menu",
        "page_navigation": "_send_page_navigation", 
        "emergency": "_send_emergency",
        "specialist_response": "_send_specialist_response",
        "general_response": "_send_text_response"
    }
    
    def __init__(self, config: Config):
        self.config = config
        self.coordinator = IntelligentCoordinator(config)
        self.api = TelegramAPIClient(config.telegram.bot_token)
        self.formatter = MessageFormatter()
    
    async def process_update(self, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Procesa update de Telegram"""
        if 'message' in update_data:
            return await self._handle_message(update_data['message'])
        elif 'callback_query' in update_data:
            return await self._handle_callback(update_data['callback_query'])
        else:
            return {"status": "ignored", "reason": "unknown_update_type"}
    
    @handle_errors
    async def _handle_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Procesa mensaje de texto"""
        user_id = str(message.get('from', {}).get('id'))
        chat_id = str(message.get('chat', {}).get('id'))
        text = message.get('text', '')
        
        logger.info(f"Message from {user_id}: {text}")
        
        # Procesar con coordinator
        response = await self.coordinator.process_user_input(
            user_id=user_id, user_input=text, phone_number=None
        )
        
        # Enviar respuesta
        await self._send_response(chat_id, response)
        
        return {
            "status": "processed",
            "message_id": message.get('message_id'),
            "response_type": response.get("response_type")
        }
    
    @handle_errors
    async def _handle_callback(self, callback_query: Dict[str, Any]) -> Dict[str, Any]:
        """Procesa callback query"""
        user_id = str(callback_query.get('from', {}).get('id'))
        chat_id = str(callback_query.get('message', {}).get('chat', {}).get('id'))
        data = callback_query.get('data', '')
        
        logger.info(f"Callback from {user_id}: {data}")
        
        # Responder callback query
        await self.api.answer_callback_query(callback_query.get('id'))
        
        # Procesar selección
        response = await self.coordinator.process_user_input(
            user_id=user_id, user_input=data, phone_number=None
        )
        
        await self._send_response(chat_id, response)
        
        return {
            "status": "processed",
            "callback_query_id": callback_query.get('id'),
            "response_type": response.get("response_type")
        }
    
    async def _send_response(self, chat_id: str, response: Dict[str, Any]) -> bool:
        """Envía respuesta usando el handler apropiado"""
        response_type = response.get("response_type")
        handler_name = self.RESPONSE_HANDLERS.get(response_type, "_send_fallback")
        handler = getattr(self, handler_name)
        
        logger.info(f"Sending {response_type} to {chat_id}")
        return await handler(chat_id, response)
    
    async def _send_menu(self, chat_id: str, response: Dict[str, Any]) -> bool:
        """Envía menú interactivo"""
        menu_data = response.get("menu_data", {})
        formatted = self.formatter.whatsapp_menu_to_telegram(menu_data)
        return await self.api.send_message(
            chat_id, formatted["text"], formatted["reply_markup"]
        )
    
    async def _send_page_navigation(self, chat_id: str, response: Dict[str, Any]) -> bool:
        """Envía navegación de páginas"""
        formatted = self.formatter.format_page_navigation(response)
        return await self.api.send_message(
            chat_id, formatted["text"], formatted["reply_markup"]
        )
    
    async def _send_emergency(self, chat_id: str, response: Dict[str, Any]) -> bool:
        """Envía mensaje de emergencia"""
        immediate_actions = response.get("immediate_actions", [])
        text = self.formatter.format_emergency_message(immediate_actions)
        logger.critical(f"EMERGENCY message to {chat_id}")
        return await self.api.send_message(chat_id, text)
    
    async def _send_specialist_response(self, chat_id: str, response: Dict[str, Any]) -> bool:
        """Envía respuesta de especialista"""
        text = response.get("response", {}).get("message", "")
        return await self.api.send_message(chat_id, text)
    
    async def _send_text_response(self, chat_id: str, response: Dict[str, Any]) -> bool:
        """Envía respuesta de texto simple"""
        text = response.get("response", "")
        return await self.api.send_message(chat_id, text)
    
    async def _send_fallback(self, chat_id: str, response: Dict[str, Any]) -> bool:
        """Fallback para tipos desconocidos"""
        logger.warning(f"Unknown response type: {response.get('response_type')}")
        return await self.api.send_message(
            chat_id, "Disculpa, ocurrió un error. ¿Puedes intentar de nuevo?"
        )
    
    # Métodos de utilidad
    async def set_webhook(self, webhook_url: str) -> bool:
        return await self.api.set_webhook(f"{webhook_url}/telegram-webhook")
    
    async def get_bot_info(self) -> Dict[str, Any]:
        return await self.api.get_me()
