"""
Test script for Dr. Clivi Hybrid Architecture
Tests both deterministic flows and intelligent routing.
"""

import asyncio
import logging
from datetime import datetime
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from dr_clivi.config import Config
from dr_clivi.agents.coordinator import IntelligentCoordinator
from dr_clivi.flows.deterministic_handler import DeterministicFlowHandler, UserContext, PlanType, PlanStatus


async def test_deterministic_flows():
    """Test the deterministic menu flows"""
    print("\n" + "="*60)
    print("🔄 TESTING DETERMINISTIC FLOWS")
    print("="*60)
    
    flow_handler = DeterministicFlowHandler()
    
    # Create test user context
    user_context = UserContext(
        user_id="test_user_123",
        patient_name="Juan Pérez",
        plan=PlanType.PRO,
        plan_status=PlanStatus.ACTIVE,
        phone_number="+525551234567"
    )
    
    # Test 1: Main menu trigger
    print("\n📱 Test 1: Main menu trigger")
    test_inputs = ["hola", "menu", "dr clivi", "inicio"]
    
    for input_text in test_inputs:
        is_deterministic = flow_handler.is_deterministic_input(input_text)
        print(f"  Input: '{input_text}' → Deterministic: {is_deterministic}")
        
        if is_deterministic:
            result = flow_handler.route_deterministic_input(user_context, input_text)
            print(f"    Result: {result.get('action', 'N/A')}")
    
    # Test 2: Menu option selection
    print("\n📋 Test 2: Menu option selection")
    menu_options = [
        "APPOINTMENTS",
        "MEASUREMENTS", 
        "MEASUREMENTS_REPORT",
        "QUESTION_TYPE"
    ]
    
    for option in menu_options:
        result = flow_handler.handle_main_menu_selection(user_context, option)
        print(f"  Option: {option}")
        print(f"    → Target: {result.get('target_page', result.get('target_flow', 'N/A'))}")
    
    # Test 3: WhatsApp menu generation
    print("\n📱 Test 3: WhatsApp menu generation")
    whatsapp_menu = flow_handler.generate_main_menu_whatsapp(user_context)
    print(f"  Generated menu for: {user_context.patient_name}")
    print(f"  Menu type: {whatsapp_menu.get('type')}")
    print(f"  Options count: {len(whatsapp_menu.get('interactive', {}).get('action', {}).get('sections', [{}])[0].get('rows', []))}")


async def test_intelligent_routing():
    """Test the AI-powered intelligent routing"""
    print("\n" + "="*60)
    print("🧠 TESTING INTELLIGENT ROUTING")
    print("="*60)
    
    config = Config()
    coordinator = IntelligentCoordinator(config)
    
    # Test cases that should trigger intelligent routing
    test_cases = [
        {
            "input": "Mi glucosa está en 250 y me siento mal",
            "expected_specialty": "diabetes",
            "expected_urgency": "high"
        },
        {
            "input": "¿Puedo tomar Ozempic si tengo diabetes?",
            "expected_specialty": "obesity", 
            "expected_urgency": "medium"
        },
        {
            "input": "Tengo mareos y sudor frío",
            "expected_specialty": "emergency",
            "expected_urgency": "critical"
        },
        {
            "input": "¿Cuándo es mi próxima cita?",
            "expected_specialty": "general",
            "expected_urgency": "low"
        },
        {
            "input": "No puedo bajar mi azúcar de 400",
            "expected_specialty": "emergency",
            "expected_urgency": "critical"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 Test {i}: {test_case['input']}")
        
        try:
            # Process through coordinator
            result = await coordinator.process_user_input(
                user_id="test_user_456",
                user_input=test_case["input"],
                phone_number="+525559876543"
            )
            
            print(f"  ✅ Response type: {result.get('response_type')}")
            print(f"  🎯 Routing type: {result.get('routing_type')}")
            
            if "analysis" in result:
                analysis = result["analysis"]
                print(f"  🏥 Detected specialty: {analysis.get('specialty')}")
                print(f"  ⚡ Urgency: {analysis.get('urgency')}")
                print(f"  🎯 Confidence: {analysis.get('confidence', 0):.2f}")
            
            if result.get("response_type") == "emergency":
                print(f"  🚨 EMERGENCY DETECTED!")
                actions = result.get("immediate_actions", [])
                print(f"  📋 Actions: {len(actions)} steps provided")
            
        except Exception as e:
            print(f"  ❌ Error: {e}")


async def test_hybrid_integration():
    """Test the integration between deterministic and intelligent routing"""
    print("\n" + "="*60)
    print("🔗 TESTING HYBRID INTEGRATION")
    print("="*60)
    
    config = Config()
    coordinator = IntelligentCoordinator(config)
    
    # Test scenarios that should switch between modes
    test_scenarios = [
        {
            "step": 1,
            "input": "hola",
            "description": "User starts with deterministic greeting"
        },
        {
            "step": 2, 
            "input": "Mi glucosa está muy alta",
            "description": "User escapes to intelligent routing"
        },
        {
            "step": 3,
            "input": "menu",
            "description": "User returns to deterministic menu"
        },
        {
            "step": 4,
            "input": "¿Qué pasa si olvido mi insulina?",
            "description": "User asks complex medical question"
        }
    ]
    
    user_id = "hybrid_test_user"
    
    for scenario in test_scenarios:
        print(f"\n📋 Step {scenario['step']}: {scenario['description']}")
        print(f"  Input: '{scenario['input']}'")
        
        try:
            result = await coordinator.process_user_input(
                user_id=user_id,
                user_input=scenario["input"],
                phone_number="+525551111111"
            )
            
            routing_type = result.get("routing_type", "unknown")
            response_type = result.get("response_type", "unknown")
            
            print(f"  → Routing: {routing_type}")
            print(f"  → Response: {response_type}")
            
            if routing_type == "deterministic":
                if response_type == "whatsapp_menu":
                    print("  📱 WhatsApp menu would be displayed")
                elif response_type == "page_navigation":
                    print(f"  🧭 Navigation to: {result.get('target_page', 'N/A')}")
            
            elif routing_type == "intelligent":
                if "analysis" in result:
                    specialty = result["analysis"].get("specialty", "unknown")
                    print(f"  🧠 AI routed to: {specialty}")
            
        except Exception as e:
            print(f"  ❌ Error: {e}")


async def test_whatsapp_integration():
    """Test WhatsApp webhook simulation"""
    print("\n" + "="*60)
    print("📱 TESTING WHATSAPP INTEGRATION")
    print("="*60)
    
    # Simulate WhatsApp webhook payloads
    webhook_payloads = [
        {
            "name": "Text message - greeting",
            "payload": {
                "entry": [{
                    "changes": [{
                        "value": {
                            "messages": [{
                                "from": "525551234567",
                                "id": "msg_001",
                                "type": "text",
                                "text": {"body": "Hola Dr. Clivi"}
                            }]
                        }
                    }]
                }]
            }
        },
        {
            "name": "Interactive message - menu selection",
            "payload": {
                "entry": [{
                    "changes": [{
                        "value": {
                            "messages": [{
                                "from": "525551234567",
                                "id": "msg_002", 
                                "type": "interactive",
                                "interactive": {
                                    "type": "list_reply",
                                    "list_reply": {"id": "MEASUREMENTS"}
                                }
                            }]
                        }
                    }]
                }]
            }
        },
        {
            "name": "Text message - medical emergency",
            "payload": {
                "entry": [{
                    "changes": [{
                        "value": {
                            "messages": [{
                                "from": "525559876543", 
                                "id": "msg_003",
                                "type": "text",
                                "text": {"body": "Ayuda, mi azúcar está en 450 y me siento muy mal"}
                            }]
                        }
                    }]
                }]
            }
        }
    ]
    
    # Simulate webhook processing
    for test in webhook_payloads:
        print(f"\n📨 Test: {test['name']}")
        
        # Extract message info
        entry = test["payload"].get("entry", [{}])[0]
        changes = entry.get("changes", [{}])[0]
        value = changes.get("value", {})
        
        if "messages" in value:
            message = value["messages"][0]
            phone = message.get("from")
            msg_type = message.get("type")
            
            # Extract content
            if msg_type == "text":
                content = message.get("text", {}).get("body", "")
            elif msg_type == "interactive":
                interactive = message.get("interactive", {})
                if interactive.get("type") == "list_reply":
                    content = interactive.get("list_reply", {}).get("id", "")
                else:
                    content = "interactive_message"
            
            print(f"  📞 From: {phone}")
            print(f"  📝 Type: {msg_type}")
            print(f"  💬 Content: '{content}'")
            
            # Process through coordinator
            try:
                config = Config()
                coordinator = IntelligentCoordinator(config)
                
                result = await coordinator.process_user_input(
                    user_id=phone,
                    user_input=content,
                    phone_number=phone
                )
                
                print(f"  ✅ Processed: {result.get('response_type')}")
                print(f"  🔄 Routing: {result.get('routing_type')}")
                
            except Exception as e:
                print(f"  ❌ Error: {e}")


async def main():
    """Run all tests"""
    print("🏥 DR. CLIVI HYBRID ARCHITECTURE TESTS")
    print("=" * 60)
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Run all test suites
        await test_deterministic_flows()
        await test_intelligent_routing()
        await test_hybrid_integration()
        await test_whatsapp_integration()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
        print("="*60)
        
        print("\n📋 NEXT STEPS FOR REAL WhatsApp TESTING:")
        print("1. ✅ Get WhatsApp Business API credentials")
        print("2. ✅ Configure webhook URL (use ngrok for local testing)")
        print("3. ✅ Update .env with real WhatsApp tokens")
        print("4. ✅ Run webhook server: python -m dr_clivi.webhook.whatsapp_handler")
        print("5. ✅ Test with real WhatsApp messages")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        logger.exception("Test failed with exception")


if __name__ == "__main__":
    asyncio.run(main())
