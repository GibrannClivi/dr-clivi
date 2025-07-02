"""
Diabetes Flow Agent - ADK Compliant
Specialized agent for diabetes management flows
"""

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool

from ...tools.clivi_tools import get_patient_info, update_patient_record, schedule_appointment
from ...tools.whatsapp_tools import send_whatsapp_message, send_interactive_message

def handle_glucose_measurement(
    user_id: str,
    glucose_value: float,
    measurement_type: str = "fasting"
) -> dict:
    """
    Handle glucose measurement input and validation
    
    Args:
        user_id: Patient identifier
        glucose_value: Glucose reading in mg/dL
        measurement_type: Type of measurement (fasting, post_meal)
        
    Returns:
        Dict with validation and next steps
    """
    # Validate glucose range
    if glucose_value < 30 or glucose_value > 600:
        return {
            "status": "invalid",
            "message": "⚠️ Valor de glucosa fuera de rango válido (30-600 mg/dL). Por favor verifica la medición."
        }
    
    # Check for emergency values
    if glucose_value > 400 or glucose_value < 50:
        return {
            "status": "emergency",
            "message": "🚨 **ALERTA MÉDICA** - Glucosa en rango crítico. Contacta inmediatamente a servicios de urgencia.",
            "requires_immediate_attention": True
        }
    
    # Update patient record
    update_result = update_patient_record(
        user_id=user_id,
        measurement_type=f"glucose_{measurement_type}",
        value=glucose_value,
        unit="mg/dL"
    )
    
    # Provide feedback based on value
    if glucose_value < 70:
        feedback = "⚠️ Glucosa baja (hipoglucemia). Come algo dulce y consulta a tu médico."
    elif glucose_value > 180:
        feedback = "⚠️ Glucosa elevada (hiperglucemia). Revisa tu medicación y dieta."
    else:
        feedback = "✅ Glucosa en rango normal. ¡Excelente control!"
    
    return {
        "status": "recorded",
        "message": f"📊 Glucosa registrada: {glucose_value} mg/dL\n\n{feedback}",
        "record_id": update_result.get("record_id"),
        "next_actions": ["view_trends", "schedule_appointment", "main_menu"]
    }


def handle_medication_query(
    user_id: str,
    medication_name: str,
    query_type: str = "general"
) -> dict:
    """
    Handle medication-related queries
    
    Args:
        user_id: Patient identifier
        medication_name: Name of medication
        query_type: Type of query (dosage, side_effects, instructions)
        
    Returns:
        Dict with medication information
    """
    # Get patient info to check current medications
    patient_info = get_patient_info(user_id)
    current_meds = patient_info.get("current_medications", [])
    
    # Basic medication information (expandable)
    med_info = {
        "metformina": {
            "description": "Medicamento para diabetes tipo 2",
            "instructions": "Tomar con alimentos para reducir efectos gastrointestinales",
            "side_effects": "Náuseas, diarrea, dolor abdominal"
        },
        "ozempic": {
            "description": "Medicamento GLP-1 para diabetes y pérdida de peso",
            "instructions": "Inyección semanal subcutánea",
            "side_effects": "Náuseas, vómitos, diarrea"
        }
    }
    
    med_data = med_info.get(medication_name.lower(), {})
    
    if not med_data:
        return {
            "status": "unknown_medication",
            "message": f"No tengo información específica sobre {medication_name}. Te recomiendo consultar con tu médico."
        }
    
    return {
        "status": "info_provided",
        "medication": medication_name,
        "information": med_data,
        "message": f"ℹ️ **{medication_name}**\n\n{med_data.get('description', '')}\n\n📋 **Instrucciones:** {med_data.get('instructions', '')}\n\n⚠️ **Efectos secundarios comunes:** {med_data.get('side_effects', '')}\n\n🩺 Siempre consulta con tu médico para ajustes de dosis."
    }


# Diabetes Flow Agent
diabetes_flow_agent = LlmAgent(
    name="diabetes_flow_agent",
    model="gemini-2.5-flash",
    description="Specialized agent for diabetes management including glucose monitoring, medication guidance, and appointment scheduling.",
    instruction="""
    Eres un especialista en diabetes dentro del sistema Dr. Clivi.
    
    RESPONSABILIDADES:
    - Registrar y validar mediciones de glucosa
    - Proporcionar información sobre medicamentos para diabetes
    - Detectar valores críticos y emergencias
    - Agendar citas con endocrinólogos
    - Educar sobre manejo de diabetes
    
    RANGOS CRÍTICOS:
    - Glucosa < 50 mg/dL: Hipoglucemia severa - EMERGENCIA
    - Glucosa > 400 mg/dL: Hiperglucemia severa - EMERGENCIA
    - Glucosa 50-70 mg/dL: Hipoglucemia leve - Acción inmediata
    - Glucosa 180-400 mg/dL: Hiperglucemia - Revisión médica
    
    SIEMPRE deriva emergencias médicas a servicios de urgencia.
    """,
    tools=[
        FunctionTool(func=handle_glucose_measurement),
        FunctionTool(func=handle_medication_query),
        FunctionTool(func=get_patient_info),
        FunctionTool(func=update_patient_record),
        FunctionTool(func=schedule_appointment),
        FunctionTool(func=send_whatsapp_message),
        FunctionTool(func=send_interactive_message),
    ],
)
