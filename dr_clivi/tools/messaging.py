"""
Messaging tool - Template message sending for WhatsApp Business API.
Based on SEND_MESSAGE tool analysis from exported flows.

Enhanced with specific template types identified in the analysis:
- WEIGHT_LOG_PAGE_AND_TEMPLATE
- END_SESSION_TEMPLATE  
- APPOINTMENTS templates
- MEASUREMENTS templates
- Interactive message support
"""

import logging
from typing import Any, Dict, Optional, List
import httpx
import json
from datetime import datetime

logger = logging.getLogger(__name__)


# Helper functions for specific message types

async def send_template_message(
    user_id: str,
    template_name: str,
    message_type: str = "TEMPLATE",
    action_type: str = "SEND_MESSAGE",
    parameters: Optional[List[str]] = None,
    phone_number: str = None
) -> Dict[str, Any]:
    """
    Enhanced template message sending function.
    Based on SEND_MESSAGE tool analysis with template patterns.
    """
    logger.info(f"Sending template message '{template_name}' to user {user_id}")
    
    # Simulate for now - will integrate with real WhatsApp API
    return {
        "success": True,
        "actionType": action_type,
        "templateName": template_name,
        "type": message_type,
        "userId": user_id,
        "messageId": f"msg_{user_id}_{datetime.now().timestamp()}",
        "timestamp": datetime.now().isoformat(),
        "parameters": parameters or {},
        "simulated": True
    }


async def send_interactive_menu(
    user_id: str,
    menu_title: str,
    menu_body: str,
    menu_options: List[Dict[str, Any]],
    menu_type: str = "list",
    phone_number: str = None
) -> Dict[str, Any]:
    """
    Send interactive menu based on SESSION_LIST pattern from flows analysis.
    Supports the menu structures used in diabetes and obesity main menus.
    """
    logger.info(f"Sending interactive menu to user {user_id}")
    
    # Simulate for now - will integrate with real WhatsApp API
    return {
        "success": True,
        "menuType": menu_type,
        "userId": user_id,
        "messageId": f"menu_{user_id}_{datetime.now().timestamp()}",
        "optionsCount": len(menu_options),
        "timestamp": datetime.now().isoformat(),
        "simulated": True
    }


async def send_weight_log_confirmation(user_id: str, weight: float, measurement_date: str) -> Dict[str, Any]:
    """Send weight log confirmation template"""
    return await send_template_message(
        user_id=user_id,
        template_name="WEIGHT_LOG_CONFIRMATION",
        parameters=[str(weight), measurement_date]
    )


async def send_glucose_log_confirmation(user_id: str, glucose_value: float, 
                                      measurement_type: str) -> Dict[str, Any]:
    """Send glucose log confirmation template"""
    return await send_template_message(
        user_id=user_id,
        template_name="GLUCOSE_LOG_CONFIRMATION", 
        parameters=[str(glucose_value), measurement_type]
    )


async def send_appointment_reminder(user_id: str, appointment_date: str, 
                                  doctor_name: str, appointment_type: str) -> Dict[str, Any]:
    """Send appointment reminder template"""
    return await send_template_message(
        user_id=user_id,
        template_name="APPOINTMENT_REMINDER",
        parameters=[appointment_date, doctor_name, appointment_type]
    )


async def send_session_end_summary(user_id: str, session_duration: str, 
                                 actions_completed: List[str]) -> Dict[str, Any]:
    """Send session end summary template"""
    actions_text = ", ".join(actions_completed[:3])  # Limit for template
    return await send_template_message(
        user_id=user_id,
        template_name="SESSION_END_SUMMARY",
        parameters=[session_duration, actions_text]
    )
    
    try:
        menu_payload = {
            "actionType": "SEND_MESSAGE",
            "type": "INTERACTIVE",
            "userId": user_id,
            "interactive": {
                "type": "list" if menu_data.get("type") == "SESSION_LIST" else "button",
                "header": {"text": header_text} if header_text else None,
                "body": {"text": body_text or menu_data.get("bodyText", "")},
                "action": menu_data.get("sections", [])
            }
        }
        
        response = await _simulate_whatsapp_api_call(menu_payload)
        
        return {
            "success": response.get("status") == "success",
            "message_id": response.get("message_id"),
            "menu_type": menu_data.get("type")
        }
        
    except Exception as e:
        logger.error(f"Error sending interactive menu: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


async def send_simple_text(
    user_id: str,
    text: str,
    action_type: str = "SEND_MESSAGE"
) -> Dict[str, Any]:
    """
    Send simple text message.
    """
    logger.info(f"Sending text message to user {user_id}")
    
    try:
        message_payload = {
            "actionType": action_type,
            "type": "TEXT",
            "userId": user_id,
            "text": text
        }
        
        response = await _simulate_whatsapp_api_call(message_payload)
        
        return {
            "success": response.get("status") == "success",
            "message_id": response.get("message_id"),
            "text": text
        }
        
    except Exception as e:
        logger.error(f"Error sending text message: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


async def _simulate_whatsapp_api_call(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Simulate WhatsApp Business API call.
    TODO: Replace with actual API integration.
    """
    import time
    import uuid
    
    # Simulate API delay
    await asyncio.sleep(0.1)
    
    # Simulate success response
    return {
        "status": "success",
        "message_id": f"msg_{uuid.uuid4().hex[:8]}",
        "timestamp": int(time.time()),
        "delivery_status": "sent"
    }


# Template message mappings based on analysis
TEMPLATE_MAPPINGS = {
    # Main menu templates
    "MAIN_MENU_DIABETES": {
        "name": "main_menu_diabetes",
        "variables": ["patient_name"]
    },
    "MAIN_MENU_OBESITY": {
        "name": "main_menu_obesity", 
        "variables": ["patient_name"]
    },
    
    # Appointment templates
    "APPOINTMENT_CONFIRMATION": {
        "name": "appointment_confirmed",
        "variables": ["appointment_date", "appointment_time", "specialist"]
    },
    "APPOINTMENT_REMINDER": {
        "name": "appointment_reminder",
        "variables": ["appointment_date", "appointment_time", "specialist"]
    },
    
    # Measurement templates
    "MEASUREMENT_LOGGED": {
        "name": "measurement_logged",
        "variables": ["measurement_type", "value", "unit"]
    },
    "MEASUREMENT_REMINDER": {
        "name": "measurement_reminder",
        "variables": ["measurement_type"]
    },
    
    # Report templates
    "REPORT_READY": {
        "name": "report_ready",
        "variables": ["report_type", "period"]
    },
    
    # Support templates
    "SUPPORT_TICKET_CREATED": {
        "name": "support_ticket_created",
        "variables": ["ticket_id", "estimated_response"]
    }
}


def get_template_config(template_name: str) -> Optional[Dict[str, Any]]:
    """Get template configuration by name"""
    return TEMPLATE_MAPPINGS.get(template_name)


# Import asyncio for async operations
import asyncio
