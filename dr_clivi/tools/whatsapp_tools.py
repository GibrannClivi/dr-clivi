"""
WhatsApp Tools for Dr. Clivi ADK Agent
ADK-compliant tools for WhatsApp Business API integration
"""

from typing import Any, Dict, Optional
import httpx
import logging

logger = logging.getLogger(__name__)


def send_whatsapp_message(
    phone_number: str,
    message: str,
    message_type: str = "text"
) -> Dict[str, Any]:
    """
    Send a WhatsApp message to a patient
    
    Args:
        phone_number: Patient's WhatsApp number
        message: Message content to send
        message_type: Type of message (text, interactive, etc.)
        
    Returns:
        Dict with send status and message ID
    """
    # TODO: Implement actual WhatsApp Business API call
    logger.info(f"Sending WhatsApp message to {phone_number}: {message}")
    
    return {
        "status": "sent",
        "message_id": f"msg_{phone_number}_{hash(message)}",
        "phone_number": phone_number,
        "message_type": message_type
    }


def get_user_context(phone_number: str) -> Dict[str, Any]:
    """
    Get user context and session data from phone number
    
    Args:
        phone_number: Patient's WhatsApp number
        
    Returns:
        Dict with user context including plan type, patient info, etc.
    """
    # TODO: Integrate with Clivi platform via n8n webhook
    logger.info(f"Getting user context for {phone_number}")
    
    # Mock response - replace with actual Clivi integration
    return {
        "user_id": f"user_{phone_number}",
        "patient_name": "Paciente",
        "plan": "PRO",
        "plan_status": "ACTIVE",
        "phone_number": phone_number,
        "last_interaction": "2025-01-04T10:00:00Z"
    }


def send_interactive_message(
    phone_number: str,
    body_text: str,
    action_button_text: str,
    sections: list
) -> Dict[str, Any]:
    """
    Send an interactive WhatsApp message with buttons/list
    
    Args:
        phone_number: Patient's WhatsApp number
        body_text: Main message text
        action_button_text: Text for action button
        sections: List of interactive sections
        
    Returns:
        Dict with send status
    """
    logger.info(f"Sending interactive WhatsApp message to {phone_number}")
    
    return {
        "status": "sent",
        "message_id": f"interactive_{phone_number}_{hash(body_text)}",
        "phone_number": phone_number,
        "message_type": "interactive"
    }
