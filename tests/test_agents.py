"""
Example usage and test script for Dr. Clivi agents.
Demonstrates the enhanced ADK-based implementation with analysis-driven features.
"""

import asyncio
import logging
from dr_clivi.config import Config
from dr_clivi.agents.coordinator import IntelligentCoordinator
from dr_clivi.agents.diabetes_agent import DiabetesAgent
from dr_clivi.agents.obesity_agent import ObesityAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_coordinator_routing():
    """Test coordinator routing logic based on plan status analysis"""
    config = Config()
    coordinator = IntelligentCoordinator(config)
    
    # Test case 1: Unknown user
    logger.info("=== Testing Unknown User Routing ===")
    result = await coordinator.check_plan_status("unknown_user_123")
    print(f"Unknown user result: {result}")
    
    # Test case 2: PRO plan active user  
    logger.info("=== Testing PRO Plan Active User ===")
    # Set up user context
    coordinator.update_session_context(
        "pro_user_123",
        patient={
            "name_display": "Juan Pérez",
            "plan": "PRO", 
            "plan_status": "ACTIVE",
            "patient_id": "PAT-123"
        },
        user_context="REGISTERED"
    )
    
    result = await coordinator.check_plan_status("pro_user_123")
    print(f"PRO active user result: {result}")
    
    # Test case 3: CLUB plan canceled user
    logger.info("=== Testing CLUB Plan Canceled User ===")
    coordinator.update_session_context(
        "club_user_456", 
        patient={
            "name_display": "María González",
            "plan": "CLUB",
            "plan_status": "CANCELED", 
            "patient_id": "PAT-456"
        },
        user_context="REGISTERED"
    )
    
    result = await coordinator.check_plan_status("club_user_456")
    print(f"CLUB canceled user result: {result}")


async def test_diabetes_agent_flows():
    """Test diabetes agent specific flows based on analysis"""
    config = Config()
    diabetes_agent = DiabetesAgent(config)
    
    # Set up user context
    diabetes_agent.update_session_context(
        "diabetes_user_789",
        patient={
            "name_display": "Carlos Ruiz",
            "plan": "PRO",
            "plan_status": "ACTIVE",
            "patient_id": "PAT-789"
        },
        user_context="REGISTERED"
    )
    
    logger.info("=== Testing Diabetes Main Menu ===")
    main_menu = await diabetes_agent.main_menu_flow("diabetes_user_789")
    print(f"Diabetes main menu: {main_menu}")
    
    logger.info("=== Testing Glucose Logging Flow ===")
    # Test glucose logging step by step
    step1 = await diabetes_agent.glucose_logging_flow("diabetes_user_789")
    print(f"Glucose logging step 1: {step1}")
    
    step2 = await diabetes_agent.glucose_logging_flow(
        "diabetes_user_789", 
        measurement_type="FASTING"
    )
    print(f"Glucose logging step 2: {step2}")
    
    step3 = await diabetes_agent.glucose_logging_flow(
        "diabetes_user_789",
        measurement_type="FASTING", 
        glucose_value=95.5
    )
    print(f"Glucose logging step 3: {step3}")


async def test_obesity_agent_flows():
    """Test obesity agent specific flows based on analysis"""
    config = Config()
    obesity_agent = ObesityAgent(config)
    
    # Set up user context
    obesity_agent.update_session_context(
        "obesity_user_456",
        patient={
            "name_display": "Ana Martínez",
            "plan": "PLUS",
            "plan_status": "ACTIVE", 
            "patient_id": "PAT-456"
        },
        user_context="REGISTERED"
    )
    
    logger.info("=== Testing Obesity Main Menu ===")
    main_menu = await obesity_agent.main_menu_flow("obesity_user_456")
    print(f"Obesity main menu: {main_menu}")
    
    logger.info("=== Testing Workout Signup Flow ===")
    # Test workout signup step by step
    step1 = await obesity_agent.workout_signup_flow("obesity_user_456")
    print(f"Workout signup step 1: {step1}")
    
    step2 = await obesity_agent.workout_signup_flow(
        "obesity_user_456",
        category="CARDIO"
    )
    print(f"Workout signup step 2: {step2}")
    
    step3 = await obesity_agent.workout_signup_flow(
        "obesity_user_456",
        category="CARDIO",
        level="INTERMEDIATE"
    )
    print(f"Workout signup step 3: {step3}")
    
    logger.info("=== Testing Nutrition Hotline Flow ===")
    # Test nutrition hotline
    hotline1 = await obesity_agent.nutrition_hotline_flow("obesity_user_456")
    print(f"Nutrition hotline step 1: {hotline1}")
    
    hotline2 = await obesity_agent.nutrition_hotline_flow(
        "obesity_user_456",
        consultation_type="MEAL_PLAN"
    )
    print(f"Nutrition hotline step 2: {hotline2}")
    
    hotline3 = await obesity_agent.nutrition_hotline_flow(
        "obesity_user_456",
        consultation_type="MEAL_PLAN",
        question="Necesito un plan de alimentación para bajar 10kg en 3 meses"
    )
    print(f"Nutrition hotline step 3: {hotline3}")


async def test_error_handling():
    """Test error handling and fallback scenarios"""
    config = Config()
    coordinator = IntelligentCoordinator(config)
    
    logger.info("=== Testing Error Handling ===")
    
    # Test no-match fallback
    no_match = await coordinator.handle_no_match_fallback(
        "test_user",
        "quiero algo que no entiendes"
    )
    print(f"No match fallback: {no_match}")
    
    # Test no-input timeout
    timeout = await coordinator.handle_no_input_timeout("test_user")
    print(f"No input timeout: {timeout}")


async def test_messaging_tools():
    """Test messaging tools with template patterns"""
    from dr_clivi.tools.messaging import (
        send_template_message,
        send_glucose_log_confirmation,
        send_weight_log_confirmation
    )
    
    logger.info("=== Testing Messaging Tools ===")
    
    # Test template message
    template_result = await send_template_message(
        user_id="test_user_123",
        template_name="GLUCOSE_LOG_CONFIRMATION",
        parameters=["125.5", "en ayunas"]
    )
    print(f"Template message result: {template_result}")
    
    # Test glucose log confirmation
    glucose_confirm = await send_glucose_log_confirmation(
        user_id="test_user_123",
        glucose_value=95.0,
        measurement_type="en ayunas"
    )
    print(f"Glucose confirmation: {glucose_confirm}")
    
    # Test weight log confirmation
    weight_confirm = await send_weight_log_confirmation(
        user_id="test_user_123",
        weight=75.5,
        measurement_date="2025-06-30"
    )
    print(f"Weight confirmation: {weight_confirm}")


async def main():
    """Run all test scenarios"""
    logger.info("🚀 Starting Dr. Clivi ADK Agent Tests")
    
    try:
        await test_coordinator_routing()
        print("\n" + "="*50 + "\n")
        
        await test_diabetes_agent_flows()
        print("\n" + "="*50 + "\n")
        
        await test_obesity_agent_flows()
        print("\n" + "="*50 + "\n")
        
        await test_error_handling()
        print("\n" + "="*50 + "\n")
        
        await test_messaging_tools()
        
        logger.info("✅ All tests completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
