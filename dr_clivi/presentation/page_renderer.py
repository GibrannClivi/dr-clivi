"""
Page Renderer - Handles the rendering of different page types
Separated from page definitions for better maintainability
"""

import logging
from typing import Any, Dict

from ..flows.pages.page_types import MessageType, ResponseType, RoutingType

logger = logging.getLogger(__name__)


class PageRenderer:
    """
    Handles rendering of pages according to their message type
    Supports WhatsApp interactive lists, Telegram button menus, and text messages
    """
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def render_page(self, page_name: str, page_def: Dict[str, Any], 
                   user_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Renders a page according to its message type
        """
        if not page_def or "entry_fulfillment" not in page_def:
            self.logger.error(f"Invalid page definition for: {page_name}")
            return self._render_fallback_page(user_context)
        
        entry_fulfillment = page_def["entry_fulfillment"]
        message_type = entry_fulfillment.get("message_type", "text")
        
        # Route to appropriate renderer
        if message_type == MessageType.INTERACTIVE_LIST.value:
            return self._render_interactive_list(entry_fulfillment, user_context, page_name)
        elif message_type == MessageType.BUTTON_MENU.value:
            return self._render_button_menu(entry_fulfillment, user_context, page_name)
        elif message_type == MessageType.BUTTONS.value:
            return self._render_buttons(entry_fulfillment, user_context, page_name)
        else:
            return self._render_text_message(entry_fulfillment, user_context, page_name)
    
    def _render_interactive_list(self, fulfillment: Dict[str, Any], 
                               user_context: Dict[str, Any], page_name: str) -> Dict[str, Any]:
        """Renders WhatsApp interactive list format"""
        try:
            # Format text with user context
            body_text = fulfillment["body_text"].format(**user_context)
        except KeyError as e:
            self.logger.warning(f"Missing context variable for formatting: {e}")
            body_text = fulfillment["body_text"]
        
        return {
            "response_type": ResponseType.WHATSAPP_MENU.value,
            "menu_data": {
                "interactive": {
                    "type": "list",
                    "header": {
                        "type": "text",
                        "text": "Dr. Clivi"
                    },
                    "body": {
                        "text": body_text
                    },
                    "action": {
                        "button": fulfillment.get("action_button_text", "Seleccionar"),
                        "sections": fulfillment.get("sections", [])
                    }
                }
            },
            "page": page_name,
            "routing_type": RoutingType.DETERMINISTIC.value
        }
    
    def _render_button_menu(self, fulfillment: Dict[str, Any], 
                          user_context: Dict[str, Any], page_name: str) -> Dict[str, Any]:
        """Renders Telegram inline keyboard format"""
        # Convert buttons to inline keyboard for Telegram
        inline_keyboard = []
        buttons = fulfillment.get("buttons", [])
        
        # Group buttons in rows of 2
        for i in range(0, len(buttons), 2):
            row = []
            for j in range(i, min(i + 2, len(buttons))):
                button = buttons[j]
                row.append({
                    "text": button["text"],
                    "callback_data": button["id"]
                })
            inline_keyboard.append(row)
        
        return {
            "response_type": ResponseType.PAGE_NAVIGATION.value,
            "body_text": fulfillment.get("text_body", ""),
            "inline_keyboard": inline_keyboard,
            "page": page_name,
            "routing_type": RoutingType.DETERMINISTIC.value
        }
    
    def _render_buttons(self, fulfillment: Dict[str, Any],
                       user_context: Dict[str, Any], page_name: str) -> Dict[str, Any]:
        """Renders simple buttons format"""
        buttons = fulfillment.get("buttons", [])
        inline_keyboard = [[{
            "text": button["text"],
            "callback_data": button["id"]
        }] for button in buttons]
        
        return {
            "response_type": ResponseType.PAGE_NAVIGATION.value,
            "body_text": fulfillment.get("body_text", ""),
            "inline_keyboard": inline_keyboard,
            "page": page_name,
            "routing_type": RoutingType.DETERMINISTIC.value
        }
    
    def _render_text_message(self, fulfillment: Dict[str, Any],
                           user_context: Dict[str, Any], page_name: str) -> Dict[str, Any]:
        """Renders simple text message"""
        try:
            # Format text with user context if possible
            text = fulfillment.get("text", "").format(**user_context)
        except (KeyError, ValueError):
            text = fulfillment.get("text", "Mensaje de texto")
        
        return {
            "response_type": ResponseType.GENERAL_RESPONSE.value,
            "response": text,
            "page": page_name,
            "routing_type": RoutingType.DETERMINISTIC.value
        }
    
    def _render_fallback_page(self, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback page when rendering fails"""
        return {
            "response_type": ResponseType.GENERAL_RESPONSE.value,
            "response": "Lo siento, ocurrió un error. Regresando al menú principal.",
            "suggested_action": "show_main_menu",
            "routing_type": RoutingType.ERROR_FALLBACK.value
        }
