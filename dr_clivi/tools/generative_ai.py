"""
Generative AI tool - Ask generative AI for specialized responses.
Based on "Ask OpenAI" tool analysis, migrated to Vertex AI.
"""

import logging
from typing import Any, Dict, Optional
import json

logger = logging.getLogger(__name__)


async def ask_generative_ai(
    user_request: str,
    context: str,
    user_id: str,
    function_name: str = "ASK_GENERATIVE_AI",
    action_type: str = "CALL_FUNCTION",
    model: str = "gemini-2.5-flash"
) -> Dict[str, Any]:
    """
    Send user request to generative AI and return response.
    
    Based on "Ask OpenAI" tool analysis:
    - actionType: "CALL_FUNCTION"
    - functionName: "ASK_GENERATIVE_AI"
    - userRequest: User's question/request
    - context: Additional context for the AI
    
    Migrated from OpenAI to Vertex AI Gemini for better integration.
    
    Args:
        user_request: The user's question or request
        context: Additional context for the AI model
        user_id: User identifier for logging
        function_name: Function name (default: ASK_GENERATIVE_AI)
        action_type: Action type (default: CALL_FUNCTION)
        model: AI model to use (default: gemini-2.5-flash)
        
    Returns:
        Dict with AI response and metadata
    """
    logger.info(f"Processing generative AI request for user {user_id}")
    
    try:
        # Prepare AI prompt with context
        system_prompt = _build_system_prompt(context)
        full_prompt = f"{system_prompt}\n\nUsuario: {user_request}"
        
        # Call Vertex AI (placeholder implementation)
        ai_response = await _call_vertex_ai(
            prompt=full_prompt,
            model=model,
            user_id=user_id
        )
        
        if ai_response.get("success"):
            logger.info(f"Generative AI response generated for user {user_id}")
            return {
                "success": True,
                "response": ai_response.get("text"),
                "model_used": model,
                "function_name": function_name,
                "confidence": ai_response.get("confidence", 0.0),
                "tokens_used": ai_response.get("tokens_used"),
                "response_time": ai_response.get("response_time")
            }
        else:
            logger.error(f"Generative AI request failed: {ai_response.get('error')}")
            return {
                "success": False,
                "error": ai_response.get("error", "AI processing failed"),
                "fallback_response": _get_fallback_response(user_request)
            }
            
    except Exception as e:
        logger.error(f"Error in generative AI request: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "fallback_response": _get_fallback_response(user_request)
        }


async def ask_specialized_ai(
    user_request: str,
    specialty: str,
    patient_context: Dict[str, Any],
    user_id: str
) -> Dict[str, Any]:
    """
    Ask specialized AI with medical context.
    
    Enhanced version for medical specialties (diabetes/obesity).
    """
    logger.info(f"Processing specialized AI request ({specialty}) for user {user_id}")
    
    try:
        # Build specialized context
        specialized_context = _build_specialized_context(specialty, patient_context)
        
        # Prepare specialized prompt
        system_prompt = _build_specialized_prompt(specialty, specialized_context)
        full_prompt = f"{system_prompt}\n\nPaciente: {user_request}"
        
        # Use more powerful model for specialized queries
        ai_response = await _call_vertex_ai(
            prompt=full_prompt,
            model="gemini-2.5-pro",  # More powerful model
            user_id=user_id,
            specialty=specialty
        )
        
        return {
            "success": ai_response.get("success", False),
            "response": ai_response.get("text"),
            "specialty": specialty,
            "confidence": ai_response.get("confidence"),
            "medical_disclaimer": _get_medical_disclaimer(),
            "references": ai_response.get("references", []),
            "follow_up_suggestions": ai_response.get("follow_up", [])
        }
        
    except Exception as e:
        logger.error(f"Error in specialized AI request: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "specialty": specialty
        }


async def generate_medical_content(
    content_type: str,
    topic: str,
    audience: str = "patient",
    language: str = "es"
) -> Dict[str, Any]:
    """
    Generate medical educational content.
    """
    logger.info(f"Generating medical content: {content_type} about {topic}")
    
    try:
        prompt = _build_content_generation_prompt(
            content_type, topic, audience, language
        )
        
        ai_response = await _call_vertex_ai(
            prompt=prompt,
            model="gemini-2.5-pro",
            user_id="content_generation"
        )
        
        return {
            "success": ai_response.get("success", False),
            "content": ai_response.get("text"),
            "content_type": content_type,
            "topic": topic,
            "audience": audience,
            "language": language,
            "medical_disclaimer": _get_medical_disclaimer()
        }
        
    except Exception as e:
        logger.error(f"Error generating medical content: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


async def _call_vertex_ai(
    prompt: str,
    model: str,
    user_id: str,
    specialty: str = None
) -> Dict[str, Any]:
    """
    Call Vertex AI Gemini API.
    TODO: Replace with actual Vertex AI implementation.
    """
    import time
    import asyncio
    
    # Simulate API delay
    await asyncio.sleep(0.5)
    
    # Simulate AI response
    response_templates = {
        "diabetes": "Basándome en tu consulta sobre diabetes, puedo ayudarte con información general...",
        "obesity": "Respecto a tu pregunta sobre manejo de peso...",
        "general": "Te puedo ayudar con información general sobre salud..."
    }
    
    template = response_templates.get(specialty, response_templates["general"])
    
    return {
        "success": True,
        "text": f"{template} [Esta es una respuesta simulada del modelo {model}]",
        "confidence": 0.85,
        "tokens_used": 150,
        "response_time": 0.5,
        "model": model
    }


def _build_system_prompt(context: str) -> str:
    """Build system prompt with context"""
    return f"""
    Eres un asistente médico especializado de Dr. Clivi. 
    
    Contexto: {context}
    
    IMPORTANTE:
    - Proporciona información médica precisa pero general
    - Siempre recomienda consultar con un profesional de la salud
    - Mantén un tono empático y profesional
    - Responde en español
    - No hagas diagnósticos específicos
    - Enfócate en educación y orientación general
    """


def _build_specialized_context(specialty: str, patient_context: Dict[str, Any]) -> str:
    """Build specialized medical context"""
    context_parts = [f"Especialidad: {specialty}"]
    
    if patient_context.get("plan"):
        context_parts.append(f"Plan del paciente: {patient_context['plan']}")
    
    if patient_context.get("age"):
        context_parts.append(f"Edad: {patient_context['age']}")
    
    if specialty == "diabetes":
        context_parts.append("Enfoque en: control glucémico, medicamentos, alimentación")
    elif specialty == "obesity":
        context_parts.append("Enfoque en: manejo de peso, ejercicio, nutrición")
    
    return " | ".join(context_parts)


def _build_specialized_prompt(specialty: str, context: str) -> str:
    """Build specialized medical prompt"""
    base_prompt = _build_system_prompt(context)
    
    specialty_additions = {
        "diabetes": """
        Especialización en diabetes:
        - Control de glucosa y hemoglobina glucosilada
        - Medicamentos GLP-1 (Ozempic, Saxenda, Wegovy)
        - Alimentación para diabéticos
        - Monitoreo y complicaciones
        """,
        "obesity": """
        Especialización en obesidad:
        - Manejo integral del peso
        - Planes de ejercicio personalizados
        - Nutrición y cambios de estilo de vida
        - Medicina deportiva y motivación
        """
    }
    
    addition = specialty_additions.get(specialty, "")
    return f"{base_prompt}\n{addition}"


def _build_content_generation_prompt(
    content_type: str,
    topic: str,
    audience: str,
    language: str
) -> str:
    """Build prompt for content generation"""
    return f"""
    Genera contenido médico educativo:
    
    Tipo: {content_type}
    Tema: {topic}
    Audiencia: {audience}
    Idioma: {language}
    
    Requisitos:
    - Información médica precisa y actualizada
    - Lenguaje apropiado para la audiencia
    - Estructura clara y fácil de entender
    - Incluir recomendaciones prácticas
    - Añadir disclaimer médico apropiado
    """


def _get_fallback_response(user_request: str) -> str:
    """Get fallback response when AI fails"""
    return """
    Lo siento, no pude procesar tu consulta en este momento. 
    Por favor intenta de nuevo o contacta directamente con nuestro equipo de soporte.
    
    Para consultas médicas específicas, siempre recomendamos hablar con tu médico tratante.
    """


def _get_medical_disclaimer() -> str:
    """Get standard medical disclaimer"""
    return """
    IMPORTANTE: Esta información es solo para fines educativos y no reemplaza 
    la consulta médica profesional. Siempre consulta con tu médico antes de 
    hacer cambios en tu tratamiento o estilo de vida.
    """


# AI response processing utilities
def extract_action_items(ai_response: str) -> List[str]:
    """Extract actionable items from AI response"""
    # Simple extraction logic - can be enhanced with NLP
    action_keywords = ["debes", "recomiendo", "sugiero", "considera", "intenta"]
    lines = ai_response.split('\n')
    
    actions = []
    for line in lines:
        if any(keyword in line.lower() for keyword in action_keywords):
            actions.append(line.strip())
    
    return actions


def classify_response_urgency(ai_response: str) -> str:
    """Classify response urgency level"""
    urgent_keywords = ["urgente", "inmediato", "emergencia", "contacta", "médico"]
    
    if any(keyword in ai_response.lower() for keyword in urgent_keywords):
        return "high"
    else:
        return "normal"


# Import required modules
from typing import List
