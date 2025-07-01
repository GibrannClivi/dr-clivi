#!/usr/bin/env python3
"""
Prueba Local Real del Bot de Telegram - Dr. Clivi
Simula una conversación real siguiendo el flujo de agentes ADK
"""

import asyncio
import json
import logging
import sys
import os
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dr_clivi.config import Config
from dr_clivi.telegram.telegram_handler import TelegramBotHandler

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('telegram_local_test.log')
    ]
)
logger = logging.getLogger(__name__)


class TelegramLocalTester:
    """Simulador de conversación local con el bot de Telegram"""
    
    def __init__(self):
        self.config = Config()
        self.handler = TelegramBotHandler(self.config)
        self.test_user_id = "123456789"
        self.test_chat_id = "123456789"
        self.conversation_history = []
    
    def create_text_message(self, text: str, message_id: int = None) -> dict:
        """Crea un mensaje de texto simulado"""
        return {
            "update_id": message_id or len(self.conversation_history) + 1000,
            "message": {
                "message_id": message_id or len(self.conversation_history) + 100,
                "from": {
                    "id": int(self.test_user_id),
                    "is_bot": False,
                    "first_name": "Test",
                    "last_name": "User",
                    "username": "testuser",
                    "language_code": "es"
                },
                "chat": {
                    "id": int(self.test_chat_id),
                    "first_name": "Test",
                    "last_name": "User",
                    "username": "testuser",
                    "type": "private"
                },
                "date": int(datetime.now().timestamp()),
                "text": text
            }
        }
    
    def create_callback_query(self, callback_data: str, query_id: str = None) -> dict:
        """Crea un callback query simulado (botón presionado)"""
        return {
            "update_id": len(self.conversation_history) + 2000,
            "callback_query": {
                "id": query_id or f"callback_{len(self.conversation_history)}",
                "from": {
                    "id": int(self.test_user_id),
                    "is_bot": False,
                    "first_name": "Test",
                    "last_name": "User",
                    "username": "testuser",
                    "language_code": "es"
                },
                "message": {
                    "message_id": len(self.conversation_history) + 200,
                    "chat": {
                        "id": int(self.test_chat_id),
                        "first_name": "Test",
                        "last_name": "User",
                        "username": "testuser",
                        "type": "private"
                    },
                    "date": int(datetime.now().timestamp())
                },
                "data": callback_data
            }
        }
    
    async def send_message(self, text: str) -> dict:
        """Simula envío de mensaje de texto"""
        logger.info(f"🧪 USUARIO: {text}")
        
        update = self.create_text_message(text)
        
        # Interceptar las llamadas a la API de Telegram para no enviar realmente
        original_api_call = self.handler._make_telegram_api_call
        responses = []
        
        async def mock_api_call(method, payload):
            responses.append({
                "method": method,
                "payload": payload
            })
            logger.info(f"🤖 BOT ({method}): {payload.get('text', payload)}")
            return True
        
        self.handler._make_telegram_api_call = mock_api_call
        
        try:
            result = await self.handler.process_telegram_update(update)
            self.conversation_history.append({
                "type": "message",
                "input": text,
                "result": result,
                "bot_responses": responses,
                "timestamp": datetime.now().isoformat()
            })
            return result
        finally:
            self.handler._make_telegram_api_call = original_api_call
    
    async def press_button(self, callback_data: str) -> dict:
        """Simula presión de botón"""
        logger.info(f"🧪 BOTÓN PRESIONADO: {callback_data}")
        
        update = self.create_callback_query(callback_data)
        
        # Interceptar las llamadas a la API
        original_api_call = self.handler._make_telegram_api_call
        responses = []
        
        async def mock_api_call(method, payload):
            responses.append({
                "method": method,
                "payload": payload
            })
            logger.info(f"🤖 BOT ({method}): {payload.get('text', payload)}")
            return True
        
        self.handler._make_telegram_api_call = mock_api_call
        
        try:
            result = await self.handler.process_telegram_update(update)
            self.conversation_history.append({
                "type": "callback",
                "input": callback_data,
                "result": result,
                "bot_responses": responses,
                "timestamp": datetime.now().isoformat()
            })
            return result
        finally:
            self.handler._make_telegram_api_call = original_api_call
    
    def print_conversation_summary(self):
        """Imprime resumen de la conversación"""
        print("\n" + "="*60)
        print("📋 RESUMEN DE LA CONVERSACIÓN")
        print("="*60)
        
        for i, step in enumerate(self.conversation_history, 1):
            print(f"\n{i}. {step['type'].upper()}: {step['input']}")
            print(f"   Resultado: {step['result'].get('status')} - {step['result'].get('response_type')}")
            
            for response in step['bot_responses']:
                if response['method'] == 'sendMessage':
                    text = response['payload'].get('text', '')[:100]
                    print(f"   🤖 Respuesta: {text}...")
                    
                    reply_markup = response['payload'].get('reply_markup')
                    if reply_markup and 'inline_keyboard' in reply_markup:
                        buttons = []
                        for row in reply_markup['inline_keyboard']:
                            for button in row:
                                buttons.append(f"[{button['text']}]")
                        if buttons:
                            print(f"   🔘 Botones: {' '.join(buttons)}")
    
    def save_conversation_log(self, filename: str = None):
        """Guarda el log de la conversación"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"telegram_test_conversation_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.conversation_history, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📄 Conversación guardada en: {filename}")


async def test_complete_workflow():
    """Prueba completa del flujo de agentes ADK en Telegram"""
    
    print("🚀 INICIANDO PRUEBA LOCAL DEL BOT DE TELEGRAM")
    print("=" * 50)
    
    tester = TelegramLocalTester()
    
    try:
        # Test 1: Saludo inicial - Debe mostrar menú principal
        print("\n🧪 Test 1: Saludo inicial")
        result1 = await tester.send_message("Hola doctor")
        assert result1['status'] == 'processed'
        
        # Test 2: Consulta de diabetes - Debe rutear al especialista
        print("\n🧪 Test 2: Consulta sobre diabetes")
        result2 = await tester.send_message("Tengo diabetes y mi glucosa está en 180 mg/dl")
        assert result2['status'] == 'processed'
        
        # Test 3: Selección de especialista (simulando botón)
        print("\n🧪 Test 3: Selección de especialista diabetes")
        result3 = await tester.press_button("diabetes_specialist")
        assert result3['status'] == 'processed'
        
        # Test 4: Pregunta específica sobre medicamentos
        print("\n🧪 Test 4: Pregunta sobre medicamentos")
        result4 = await tester.send_message("¿Cuándo debo tomar la metformina?")
        assert result4['status'] == 'processed'
        
        # Test 5: Emergencia médica
        print("\n🧪 Test 5: Detección de emergencia")
        result5 = await tester.send_message("Tengo dolor en el pecho muy fuerte y no puedo respirar")
        assert result5['status'] == 'processed'
        
        # Test 6: Vuelta al menú principal
        print("\n🧪 Test 6: Regreso al menú principal")
        result6 = await tester.send_message("menú principal")
        assert result6['status'] == 'processed'
        
        # Test 7: Consulta sobre obesidad
        print("\n🧪 Test 7: Consulta sobre obesidad")
        result7 = await tester.send_message("Necesito ayuda para bajar de peso")
        assert result7['status'] == 'processed'
        
        print("\n✅ TODAS LAS PRUEBAS PASARON CORRECTAMENTE")
        
        # Mostrar resumen
        tester.print_conversation_summary()
        
        # Guardar log
        tester.save_conversation_log()
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en la prueba: {e}")
        print(f"\n❌ PRUEBA FALLÓ: {e}")
        
        # Mostrar resumen aunque falle
        tester.print_conversation_summary()
        tester.save_conversation_log("telegram_test_failed.json")
        
        return False


async def test_agent_routing():
    """Prueba específica del routing entre agentes"""
    
    print("\n🎯 PRUEBA DE ROUTING ENTRE AGENTES")
    print("=" * 40)
    
    tester = TelegramLocalTester()
    
    # Casos específicos para cada agente
    test_cases = [
        {
            "name": "Diabetes Agent",
            "input": "¿Cómo registro mi glucosa?",
            "expected_routing": "diabetes"
        },
        {
            "name": "Obesity Agent", 
            "input": "Quiero un plan para bajar de peso",
            "expected_routing": "obesity"
        },
        {
            "name": "General Agent",
            "input": "¿Qué es la hipertensión?",
            "expected_routing": "general"
        },
        {
            "name": "Emergency Detection",
            "input": "Me duele mucho el pecho",
            "expected_routing": "emergency"
        }
    ]
    
    for case in test_cases:
        print(f"\n🧪 Probando: {case['name']}")
        result = await tester.send_message(case['input'])
        
        routing_type = result.get('routing_type', 'unknown')
        response_type = result.get('response_type', 'unknown')
        
        print(f"   Input: {case['input']}")
        print(f"   Routing: {routing_type}")
        print(f"   Response: {response_type}")
        
        # Verificar que el routing sea correcto
        if case['expected_routing'] in routing_type.lower() or case['expected_routing'] in response_type.lower():
            print(f"   ✅ Routing correcto")
        else:
            print(f"   ⚠️  Routing inesperado (esperado: {case['expected_routing']})")
    
    tester.print_conversation_summary()
    tester.save_conversation_log("telegram_routing_test.json")


if __name__ == "__main__":
    print("🤖 DR. CLIVI - PRUEBA LOCAL DE TELEGRAM BOT")
    print("Verificando flujo completo de agentes ADK")
    print("=" * 60)
    
    # Verificar configuración
    try:
        # Cargar variables de entorno explícitamente
        from dotenv import load_dotenv
        load_dotenv()
        
        config = Config()
        
        # Verificar GOOGLE_API_KEY desde variable de entorno
        google_api_key = os.getenv("GOOGLE_API_KEY")
        if not google_api_key:
            print("❌ GOOGLE_API_KEY no configurado en .env")
            sys.exit(1)
        
        # Verificar token de Telegram
        telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not telegram_token:
            print("❌ TELEGRAM_BOT_TOKEN no configurado en .env")
            sys.exit(1)
            
        print("✅ Configuración verificada")
        print(f"   📊 Google API Key: {google_api_key[:20]}...")
        print(f"   🤖 Telegram Token: {telegram_token[:20]}...")
        print(f"   🎯 Config Telegram Token: {config.telegram.bot_token[:20] if config.telegram.bot_token else 'NO CARGADO'}...")
    except Exception as e:
        print(f"❌ Error de configuración: {e}")
        sys.exit(1)
    
    # Ejecutar pruebas
    asyncio.run(test_complete_workflow())
    print("\n" + "="*60)
    asyncio.run(test_agent_routing())
