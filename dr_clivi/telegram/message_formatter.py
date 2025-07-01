"""
Message Formatter - Convierte respuestas entre formatos WhatsApp y Telegram
"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class MessageFormatter:
    """Convierte mensajes entre diferentes formatos"""
    
    @staticmethod
    def whatsapp_menu_to_telegram(menu_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convierte menú interactivo de WhatsApp a inline keyboard de Telegram"""
        try:
            interactive = menu_data.get("interactive", {})
            body_text = interactive.get("body", {}).get("text", "¿Cómo puedo ayudarte?")
            
            # Extraer opciones
            sections = interactive.get("action", {}).get("sections", [])
            buttons = []
            
            for section in sections:
                for row in section.get("rows", []):
                    buttons.append({
                        "text": f"{row.get('title', '')} {row.get('description', '')}"[:64],
                        "callback_data": row.get('id', '')[:64]
                    })
            
            # Organizar en filas (2 botones por fila)
            inline_keyboard = MessageFormatter._chunk_buttons(buttons, 2)
            
            return {
                "text": body_text,
                "reply_markup": {"inline_keyboard": inline_keyboard}
            }
            
        except Exception as e:
            logger.error(f"Error converting WhatsApp menu: {e}")
            return {"text": "Error en el menú", "reply_markup": None}
    
    @staticmethod
    def format_emergency_message(immediate_actions: List[str]) -> str:
        """Formatea mensaje de emergencia"""
        emergency_text = "\n".join(immediate_actions)
        return f"🚨 **EMERGENCIA MÉDICA** 🚨\n\n{emergency_text}"
    
    @staticmethod
    def format_page_navigation(page_data: Dict[str, Any]) -> Dict[str, Any]:
        """Formatea datos de navegación de páginas"""
        return {
            "text": page_data.get("body_text", "¿Cómo puedo ayudarte?"),
            "reply_markup": {
                "inline_keyboard": page_data.get("inline_keyboard", [])
            }
        }
    
    @staticmethod
    def _chunk_buttons(buttons: List[Dict], chunk_size: int = 2) -> List[List[Dict]]:
        """Divide botones en filas"""
        chunked = []
        for i in range(0, len(buttons), chunk_size):
            chunk = buttons[i:i + chunk_size]
            chunked.append(chunk)
        return chunked
