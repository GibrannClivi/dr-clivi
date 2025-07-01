#!/usr/bin/env python3
"""
Pruebas unitarias para TelegramBotHandler
Pruebas específicas para cada método del handler
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
import json
from typing import Dict, Any

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dr_clivi.config import Config
from dr_clivi.telegram.telegram_handler import TelegramBotHandler


@pytest.fixture
def mock_config():
    """Mock config for testing"""
    config = Mock(spec=Config)
    config.telegram = Mock()
    config.telegram.bot_token = "test_bot_token"
    return config


@pytest.fixture
def telegram_handler(mock_config):
    """Create telegram handler instance for testing"""
    with patch('dr_clivi.telegram.telegram_handler.IntelligentCoordinator'):
        handler = TelegramBotHandler(mock_config)
        handler.coordinator = AsyncMock()
        return handler


class TestTelegramBotHandler:
    
    def test_initialization(self, mock_config):
        """Test 1: Handler se inicializa correctamente"""
        with patch('dr_clivi.telegram.telegram_handler.IntelligentCoordinator'):
            handler = TelegramBotHandler(mock_config)
            
            assert handler.config == mock_config
            assert handler.bot_token == "test_bot_token"
            assert handler.telegram_api_url == "https://api.telegram.org/bottest_bot_token"
    
    @pytest.mark.asyncio
    async def test_process_telegram_update_message(self, telegram_handler):
        """Test 2: Procesa correctamente mensajes de texto"""
        update_data = {
            "message": {
                "message_id": 123,
                "from": {"id": 456, "first_name": "Test"},
                "chat": {"id": 456, "type": "private"},
                "text": "hola"
            }
        }
        
        # Mock el método _handle_message
        telegram_handler._handle_message = AsyncMock(return_value={"status": "processed"})
        
        result = await telegram_handler.process_telegram_update(update_data)
        
        assert result["status"] == "processed"
        telegram_handler._handle_message.assert_called_once_with(update_data["message"])
    
    @pytest.mark.asyncio
    async def test_process_telegram_update_callback(self, telegram_handler):
        """Test 3: Procesa correctamente callback queries"""
        update_data = {
            "callback_query": {
                "id": "callback123",
                "from": {"id": 456},
                "message": {"chat": {"id": 456}},
                "data": "diabetes_specialist"
            }
        }
        
        telegram_handler._handle_callback_query = AsyncMock(return_value={"status": "processed"})
        
        result = await telegram_handler.process_telegram_update(update_data)
        
        assert result["status"] == "processed"
        telegram_handler._handle_callback_query.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_handle_message(self, telegram_handler):
        """Test 4: _handle_message procesa mensaje correctamente"""
        message = {
            "message_id": 123,
            "from": {"id": 456},
            "chat": {"id": 456},
            "text": "¿Cómo estás?"
        }
        
        # Mock coordinator response
        mock_response = {
            "response_type": "general_response",
            "response": "Hola! ¿En qué puedo ayudarte?"
        }
        telegram_handler.coordinator.process_user_input.return_value = mock_response
        telegram_handler._send_response_to_user = AsyncMock(return_value=True)
        
        result = await telegram_handler._handle_message(message)
        
        assert result["status"] == "processed"
        assert result["message_id"] == 123
        assert result["response_type"] == "general_response"
        
        # Verificar que se llamó al coordinator
        telegram_handler.coordinator.process_user_input.assert_called_once_with(
            user_id="456",
            user_input="¿Cómo estás?",
            phone_number=None
        )
    
    @pytest.mark.asyncio
    async def test_handle_callback_query(self, telegram_handler):
        """Test 5: _handle_callback_query procesa botones correctamente"""
        callback_query = {
            "id": "callback123",
            "from": {"id": 456},
            "message": {"chat": {"id": 456}},
            "data": "diabetes_specialist"
        }
        
        mock_response = {
            "response_type": "specialist_response",
            "routing_type": "diabetes_specialist"
        }
        telegram_handler.coordinator.process_user_input.return_value = mock_response
        telegram_handler._answer_callback_query = AsyncMock(return_value=True)
        telegram_handler._send_response_to_user = AsyncMock(return_value=True)
        
        result = await telegram_handler._handle_callback_query(callback_query)
        
        assert result["status"] == "processed"
        assert result["callback_query_id"] == "callback123"
        assert result["response_type"] == "specialist_response"
        
        # Verificar que se respondió al callback
        telegram_handler._answer_callback_query.assert_called_once_with("callback123")
    
    @pytest.mark.asyncio
    async def test_send_response_whatsapp_menu(self, telegram_handler):
        """Test 6: Convierte menú WhatsApp a Telegram correctamente"""
        response = {
            "response_type": "whatsapp_menu",
            "menu_data": {
                "interactive": {
                    "body": {"text": "¿En qué puedo ayudarte?"},
                    "action": {
                        "sections": [{
                            "rows": [
                                {"id": "diabetes", "title": "Diabetes", "description": "Manejo"},
                                {"id": "obesity", "title": "Obesidad", "description": "Control"}
                            ]
                        }]
                    }
                }
            }
        }
        
        telegram_handler._send_telegram_menu = AsyncMock(return_value=True)
        
        result = await telegram_handler._send_response_to_user("456", response)
        
        assert result is True
        telegram_handler._send_telegram_menu.assert_called_once_with("456", response)
    
    @pytest.mark.asyncio
    async def test_send_response_emergency(self, telegram_handler):
        """Test 7: Maneja emergencias correctamente"""
        response = {
            "response_type": "emergency",
            "immediate_actions": [
                "Llama al 911 inmediatamente",
                "No te muevas hasta que llegue ayuda"
            ]
        }
        
        telegram_handler._send_emergency_message = AsyncMock(return_value=True)
        
        result = await telegram_handler._send_response_to_user("456", response)
        
        assert result is True
        telegram_handler._send_emergency_message.assert_called_once_with("456", response)
    
    @pytest.mark.asyncio
    async def test_send_telegram_menu_conversion(self, telegram_handler):
        """Test 8: Conversión de menú WhatsApp a inline keyboard"""
        response = {
            "menu_data": {
                "interactive": {
                    "body": {"text": "Selecciona una opción:"},
                    "action": {
                        "sections": [{
                            "rows": [
                                {"id": "opt1", "title": "Opción 1", "description": "Desc 1"},
                                {"id": "opt2", "title": "Opción 2", "description": "Desc 2"},
                                {"id": "opt3", "title": "Opción 3", "description": "Desc 3"}
                            ]
                        }]
                    }
                }
            }
        }
        
        telegram_handler._make_telegram_api_call = AsyncMock(return_value=True)
        
        result = await telegram_handler._send_telegram_menu("456", response)
        
        assert result is True
        
        # Verificar que se llamó con el payload correcto
        call_args = telegram_handler._make_telegram_api_call.call_args
        assert call_args[0][0] == "sendMessage"
        
        payload = call_args[0][1]
        assert payload["chat_id"] == "456"
        assert payload["text"] == "Selecciona una opción:"
        
        # Verificar estructura del inline keyboard
        inline_keyboard = payload["reply_markup"]["inline_keyboard"]
        assert len(inline_keyboard) == 2  # 3 botones en 2 filas (2+1)
        
        # Primera fila: 2 botones
        assert len(inline_keyboard[0]) == 2
        assert inline_keyboard[0][0]["text"] == "Opción 1 Desc 1"
        assert inline_keyboard[0][0]["callback_data"] == "opt1"
        
        # Segunda fila: 1 botón
        assert len(inline_keyboard[1]) == 1
        assert inline_keyboard[1][0]["text"] == "Opción 3 Desc 3"
    
    @pytest.mark.asyncio
    async def test_send_emergency_message(self, telegram_handler):
        """Test 9: Formato de mensaje de emergencia"""
        response = {
            "immediate_actions": [
                "Acción 1",
                "Acción 2"
            ]
        }
        
        telegram_handler._make_telegram_api_call = AsyncMock(return_value=True)
        
        result = await telegram_handler._send_emergency_message("456", response)
        
        assert result is True
        
        call_args = telegram_handler._make_telegram_api_call.call_args
        payload = call_args[0][1]
        
        assert "🚨 **EMERGENCIA MÉDICA** 🚨" in payload["text"]
        assert "Acción 1" in payload["text"]
        assert "Acción 2" in payload["text"]
        assert payload["parse_mode"] == "Markdown"
    
    @pytest.mark.asyncio
    async def test_handle_page_navigation(self, telegram_handler):
        """Test 10: Navegación de páginas"""
        page_data = {
            "body_text": "Página 2 de opciones:",
            "inline_keyboard": [
                [{"text": "Opción 4", "callback_data": "opt4"}],
                [{"text": "← Anterior", "callback_data": "prev_page"}]
            ]
        }
        
        telegram_handler._make_telegram_api_call = AsyncMock(return_value=True)
        
        result = await telegram_handler._handle_page_navigation("456", page_data)
        
        assert result is True
        
        call_args = telegram_handler._make_telegram_api_call.call_args
        payload = call_args[0][1]
        
        assert payload["text"] == "Página 2 de opciones:"
        assert payload["reply_markup"]["inline_keyboard"] == page_data["inline_keyboard"]
    
    @pytest.mark.asyncio
    @patch('httpx.AsyncClient')
    async def test_make_telegram_api_call_success(self, mock_client, telegram_handler):
        """Test 11: API call exitosa"""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"ok": True, "result": {}}
        
        mock_client_instance = AsyncMock()
        mock_client_instance.post.return_value = mock_response
        mock_client.return_value.__aenter__.return_value = mock_client_instance
        
        payload = {"chat_id": "456", "text": "test"}
        result = await telegram_handler._make_telegram_api_call("sendMessage", payload)
        
        assert result is True
        mock_client_instance.post.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('httpx.AsyncClient')
    async def test_make_telegram_api_call_error(self, mock_client, telegram_handler):
        """Test 12: API call con error"""
        # Mock error response
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        
        mock_client_instance = AsyncMock()
        mock_client_instance.post.return_value = mock_response
        mock_client.return_value.__aenter__.return_value = mock_client_instance
        
        payload = {"chat_id": "456", "text": "test"}
        result = await telegram_handler._make_telegram_api_call("sendMessage", payload)
        
        assert result is False


# Ejecutar pruebas si se ejecuta directamente
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
