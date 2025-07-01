"""
Telegram API Client - Maneja exclusivamente las llamadas a la API de Telegram
"""

import logging
from typing import Any, Dict, List
import httpx

logger = logging.getLogger(__name__)


class TelegramAPIClient:
    """Cliente optimizado para la API de Telegram"""
    
    def __init__(self, bot_token: str):
        self.bot_token = bot_token
        self.api_url = f"https://api.telegram.org/bot{bot_token}"
    
    async def send_message(self, chat_id: str, text: str, reply_markup: Dict = None, parse_mode: str = "Markdown") -> bool:
        """Envía mensaje de texto"""
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode
        }
        if reply_markup:
            payload["reply_markup"] = reply_markup
            
        return await self._api_call("sendMessage", payload)
    
    async def answer_callback_query(self, callback_query_id: str, text: str = "") -> bool:
        """Responde a callback query"""
        return await self._api_call("answerCallbackQuery", {
            "callback_query_id": callback_query_id,
            "text": text
        })
    
    async def set_webhook(self, webhook_url: str) -> bool:
        """Configura webhook"""
        return await self._api_call("setWebhook", {"url": webhook_url})
    
    async def get_me(self) -> Dict[str, Any]:
        """Obtiene info del bot"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.api_url}/getMe")
                return response.json() if response.status_code == 200 else {"error": response.status_code}
        except Exception as e:
            logger.error(f"Error getting bot info: {e}")
            return {"error": str(e)}
    
    async def _api_call(self, method: str, payload: Dict[str, Any]) -> bool:
        """Llamada genérica a la API"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(f"{self.api_url}/{method}", json=payload)
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("ok"):
                        logger.debug(f"API call {method} successful")
                        return True
                    else:
                        logger.error(f"API error for {method}: {result}")
                        return False
                else:
                    logger.error(f"HTTP error for {method}: {response.status_code}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error in API call {method}: {e}")
            return False
