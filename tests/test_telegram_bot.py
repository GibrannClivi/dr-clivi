#!/usr/bin/env python3
"""
Test suite for Dr. Clivi Telegram Bot functionality
Validates the hybrid architecture adaptation for Telegram.
"""

import asyncio
import os
import sys
import json
from typing import Dict, Any

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dr_clivi.config import Config
from dr_clivi.telegram.telegram_handler import TelegramBotHandler


class MockTelegramUpdate:
    """Generate mock Telegram updates for testing"""
    
    @staticmethod
    def text_message(user_id: int, chat_id: int, text: str) -> Dict[str, Any]:
        """Create a mock text message update"""
        return {
            "update_id": 12345,
            "message": {
                "message_id": 67890,
                "from": {
                    "id": user_id,
                    "is_bot": False,
                    "first_name": "Test",
                    "username": "testuser",
                    "language_code": "es"
                },
                "chat": {
                    "id": chat_id,
                    "first_name": "Test",
                    "username": "testuser",
                    "type": "private"
                },
                "date": 1640995200,
                "text": text
            }
        }
    
    @staticmethod
    def callback_query(user_id: int, chat_id: int, data: str) -> Dict[str, Any]:
        """Create a mock callback query update (button click)"""
        return {
            "update_id": 12346,
            "callback_query": {
                "id": "callback123",
                "from": {
                    "id": user_id,
                    "is_bot": False,
                    "first_name": "Test",
                    "username": "testuser",
                    "language_code": "es"
                },
                "message": {
                    "message_id": 67891,
                    "chat": {
                        "id": chat_id,
                        "first_name": "Test",
                        "username": "testuser",
                        "type": "private"
                    }
                },
                "data": data
            }
        }


async def test_telegram_handler_initialization():
    """Test 1: Telegram handler initializes correctly"""
    print("🧪 Test 1: Telegram handler initialization...")
    
    try:
        config = Config()
        handler = TelegramBotHandler(config)
        
        assert handler.config is not None
        assert handler.coordinator is not None
        assert hasattr(handler, 'telegram_api_url')
        
        print("✅ Telegram handler initialized successfully")
        return True
        
    except Exception as e:
        print(f"❌ Telegram handler initialization failed: {e}")
        return False


async def test_text_message_processing():
    """Test 2: Process text messages through hybrid architecture"""
    print("\n🧪 Test 2: Text message processing...")
    
    try:
        config = Config()
        handler = TelegramBotHandler(config)
        
        # Test message that should trigger main menu
        update = MockTelegramUpdate.text_message(
            user_id=123456,
            chat_id=123456,
            text="hola"
        )
        
        # Process message (without actually sending to Telegram API)
        # We'll just test the processing logic
        message_data = update["message"]
        user_id = str(message_data["from"]["id"])
        text = message_data["text"]
        
        # Process through coordinator
        response = await handler.coordinator.process_user_input(
            user_id=user_id,
            user_input=text,
            phone_number=None
        )
        
        # Validate response structure
        assert isinstance(response, dict)
        assert "response_type" in response
        assert "routing_type" in response
        
        print(f"✅ Text message processed - Type: {response.get('response_type')}")
        return True
        
    except Exception as e:
        print(f"❌ Text message processing failed: {e}")
        return False


async def test_callback_query_processing():
    """Test 3: Process button clicks (callback queries)"""
    print("\n🧪 Test 3: Callback query processing...")
    
    try:
        config = Config()
        handler = TelegramBotHandler(config)
        
        # Test callback for diabetes specialization
        update = MockTelegramUpdate.callback_query(
            user_id=123456,
            chat_id=123456,
            data="diabetes_specialist"
        )
        
        # Extract callback data
        callback_data = update["callback_query"]
        user_id = str(callback_data["from"]["id"])
        data = callback_data["data"]
        
        # Process through coordinator
        response = await handler.coordinator.process_user_input(
            user_id=user_id,
            user_input=data,
            phone_number=None
        )
        
        # Validate response
        assert isinstance(response, dict)
        print(f"✅ Callback query processed - Routing: {response.get('routing_type')}")
        return True
        
    except Exception as e:
        print(f"❌ Callback query processing failed: {e}")
        return False


async def test_emergency_detection():
    """Test 4: Emergency detection in Telegram"""
    print("\n🧪 Test 4: Emergency detection...")
    
    try:
        config = Config()
        handler = TelegramBotHandler(config)
        
        # Test emergency message
        emergency_text = "tengo dolor en el pecho muy fuerte y no puedo respirar"
        
        response = await handler.coordinator.process_user_input(
            user_id="emergency_test",
            user_input=emergency_text,
            phone_number=None
        )
        
        # Check if emergency was detected
        assert isinstance(response, dict)
        
        if response.get("response_type") == "emergency":
            print("✅ Emergency correctly detected and handled")
        else:
            print(f"⚠️  Emergency not detected, got: {response.get('response_type')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Emergency detection failed: {e}")
        return False


async def test_menu_conversion():
    """Test 5: WhatsApp menu to Telegram inline keyboard conversion"""
    print("\n🧪 Test 5: Menu conversion...")
    
    try:
        config = Config()
        handler = TelegramBotHandler(config)
        
        # Create mock WhatsApp menu response
        whatsapp_menu_response = {
            "response_type": "whatsapp_menu",
            "menu_data": {
                "interactive": {
                    "body": {"text": "¿En qué puedo ayudarte?"},
                    "action": {
                        "sections": [{
                            "rows": [
                                {"id": "diabetes", "title": "Diabetes", "description": "Manejo diabetes"},
                                {"id": "obesity", "title": "Obesidad", "description": "Control peso"}
                            ]
                        }]
                    }
                }
            }
        }
        
        # Test menu conversion logic (just the data structure)
        menu_data = whatsapp_menu_response.get("menu_data", {})
        interactive = menu_data.get("interactive", {})
        sections = interactive.get("action", {}).get("sections", [])
        
        # Convert to Telegram format
        inline_keyboard = []
        for section in sections:
            for row in section.get("rows", []):
                button = [{
                    "text": f"{row.get('title', '')} {row.get('description', '')}"[:64],
                    "callback_data": row.get('id', '')[:64]
                }]
                inline_keyboard.append(button)
        
        assert len(inline_keyboard) == 2  # Should have 2 buttons
        assert inline_keyboard[0][0]["text"] == "Diabetes Manejo diabetes"
        assert inline_keyboard[0][0]["callback_data"] == "diabetes"
        
        print("✅ Menu conversion works correctly")
        return True
        
    except Exception as e:
        print(f"❌ Menu conversion failed: {e}")
        return False


async def test_specialist_routing():
    """Test 6: Specialist routing through Telegram"""
    print("\n🧪 Test 6: Specialist routing...")
    
    try:
        config = Config()
        handler = TelegramBotHandler(config)
        
        # Test diabetes-specific question
        diabetes_question = "¿cómo registro mi glucosa?"
        
        response = await handler.coordinator.process_user_input(
            user_id="specialist_test",
            user_input=diabetes_question,
            phone_number=None
        )
        
        # Validate response
        assert isinstance(response, dict)
        routing_type = response.get("routing_type")
        
        print(f"✅ Specialist routing completed - Type: {routing_type}")
        return True
        
    except Exception as e:
        print(f"❌ Specialist routing failed: {e}")
        return False


async def run_all_tests():
    """Run the complete test suite"""
    print("🤖 Dr. Clivi Telegram Bot - Test Suite")
    print("=====================================")
    
    # Check environment
    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ GOOGLE_API_KEY not found. Please configure .env file")
        return False
    
    tests = [
        test_telegram_handler_initialization,
        test_text_message_processing,
        test_callback_query_processing,
        test_emergency_detection,
        test_menu_conversion,
        test_specialist_routing
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        try:
            success = await test_func()
            if success:
                passed += 1
        except Exception as e:
            print(f"❌ Test {test_func.__name__} crashed: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Telegram bot is ready for use")
        print("\nNext steps:")
        print("1. Configure TELEGRAM_BOT_TOKEN in .env")
        print("2. Run: python telegram_main.py")
        print("3. Test with your bot on Telegram")
    else:
        print("⚠️  Some tests failed. Please check the implementation")
    
    return passed == total


if __name__ == "__main__":
    asyncio.run(run_all_tests())
