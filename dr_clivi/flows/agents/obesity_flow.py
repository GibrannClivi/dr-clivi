"""
Obesity Flow Agent - ADK Compliant
Specialized agent for obesity management flows
"""

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool

from ...tools.clivi_tools import get_patient_info, update_patient_record, schedule_appointment
from ...tools.whatsapp_tools import send_whatsapp_message, send_interactive_message

def handle_weight_measurement(
    user_id: str,
    weight_value: float,
    unit: str = "kg"
) -> dict:
    """
    Handle weight measurement input and validation
    
    Args:
        user_id: Patient identifier
        weight_value: Weight reading
        unit: Unit of measurement (kg, lbs)
        
    Returns:
        Dict with validation and progress analysis
    """
    # Validate weight range
    if weight_value < 30 or weight_value > 300:
        return {
            "status": "invalid",
            "message": "⚠️ Valor de peso fuera de rango válido (30-300 kg). Por favor verifica la medición."
        }
    
    # Convert to kg if needed
    if unit.lower() == "lbs":
        weight_kg = weight_value * 0.453592
    else:
        weight_kg = weight_value
    
    # Update patient record
    update_result = update_patient_record(
        user_id=user_id,
        measurement_type="weight",
        value=weight_kg,
        unit="kg"
    )
    
    # Get patient info to calculate progress
    patient_info = get_patient_info(user_id)
    last_weight = patient_info.get("last_weight_reading", 0)
    
    # Calculate progress
    if last_weight > 0:
        weight_change = weight_kg - last_weight
        if weight_change > 0:
            progress_msg = f"📈 Aumento de {weight_change:.1f} kg desde la última medición"
        elif weight_change < 0:
            progress_msg = f"📉 Pérdida de {abs(weight_change):.1f} kg desde la última medición ¡Excelente!"
        else:
            progress_msg = "➡️ Peso estable desde la última medición"
    else:
        progress_msg = "📊 Primera medición registrada"
    
    return {
        "status": "recorded",
        "message": f"⚖️ Peso registrado: {weight_kg:.1f} kg\n\n{progress_msg}",
        "record_id": update_result.get("record_id"),
        "weight_kg": weight_kg,
        "progress": progress_msg,
        "next_actions": ["view_trends", "nutrition_plan", "exercise_plan", "main_menu"]
    }


def create_exercise_plan(
    user_id: str,
    fitness_level: str,
    preferences: list = None,
    time_available: int = 30
) -> dict:
    """
    Create personalized exercise plan
    
    Args:
        user_id: Patient identifier
        fitness_level: Current fitness level (beginner, intermediate, advanced)
        preferences: List of preferred exercise types
        time_available: Available time per session in minutes
        
    Returns:
        Dict with personalized exercise plan
    """
    preferences = preferences or []
    
    # Exercise plans by fitness level
    plans = {
        "beginner": {
            "cardio": "Caminar 20-30 min, 3-4 veces por semana",
            "strength": "Ejercicios con peso corporal 2 veces por semana",
            "flexibility": "Estiramientos diarios 10 minutos"
        },
        "intermediate": {
            "cardio": "Trotar/caminar rápido 30-45 min, 4-5 veces por semana",
            "strength": "Pesas ligeras/ejercicios funcionales 3 veces por semana",
            "flexibility": "Yoga o pilates 2 veces por semana"
        },
        "advanced": {
            "cardio": "Running/ciclismo intenso 45-60 min, 5-6 veces por semana",
            "strength": "Entrenamiento de fuerza intensivo 4 veces por semana",
            "flexibility": "Yoga avanzado o movilidad deportiva"
        }
    }
    
    plan = plans.get(fitness_level, plans["beginner"])
    
    # Customize based on time available
    if time_available < 20:
        plan["note"] = "Plan adaptado para sesiones cortas de alta intensidad"
    elif time_available > 60:
        plan["note"] = "Plan extendido con mayor volumen de entrenamiento"
    
    return {
        "status": "plan_created",
        "user_id": user_id,
        "fitness_level": fitness_level,
        "time_available": time_available,
        "plan": plan,
        "message": f"💪 **Plan de Ejercicio - Nivel {fitness_level.title()}**\n\n🏃 **Cardio:** {plan['cardio']}\n\n🏋️ **Fuerza:** {plan['strength']}\n\n🧘 **Flexibilidad:** {plan['flexibility']}\n\n⏰ Adaptado para {time_available} min por sesión",
        "next_actions": ["start_workout", "modify_plan", "nutrition_plan", "main_menu"]
    }


def provide_nutrition_guidance(
    user_id: str,
    query_type: str = "general",
    specific_food: str = None
) -> dict:
    """
    Provide nutrition guidance for weight management
    
    Args:
        user_id: Patient identifier
        query_type: Type of guidance (general, specific_food, meal_planning)
        specific_food: Specific food item if querying about it
        
    Returns:
        Dict with nutrition guidance
    """
    # Get patient info
    patient_info = get_patient_info(user_id)
    conditions = patient_info.get("medical_conditions", [])
    
    guidance = {
        "general": {
            "title": "🥗 Guía General de Nutrición",
            "content": """
**Principios básicos para pérdida de peso:**

🍽️ **Porciones controladas:**
- Usa platos más pequeños
- Come despacio y mastica bien
- Para cuando te sientas 80% lleno

🥬 **Alimentos recomendados:**
- Verduras sin almidón (espinacas, brócoli, pepino)
- Proteínas magras (pollo, pescado, legumbres)
- Grasas saludables (aguacate, nueces, aceite de oliva)
- Granos integrales con moderación

❌ **Limitar:**
- Azúcares añadidos y bebidas azucaradas
- Alimentos procesados y fritos
- Porciones grandes de carbohidratos refinados

💧 **Hidratación:** 8-10 vasos de agua al día
            """
        },
        "meal_planning": {
            "title": "📅 Planificación de Comidas",
            "content": """
**Estructura de comidas ideal:**

🌅 **Desayuno:** Proteína + fibra + grasa saludable
🥗 **Almuerzo:** Verduras + proteína + carbohidrato complejo
🍽️ **Cena:** Proteína + muchas verduras + grasa saludable
🥜 **Snacks:** Frutas, nueces, yogurt griego

**Timing:**
- Come cada 3-4 horas
- Cena 3 horas antes de dormir
- No saltes comidas
            """
        }
    }
    
    # Adjust for diabetes if present
    if "diabetes" in " ".join(conditions).lower():
        guidance["general"]["content"] += "\n\n🩸 **Especial para diabetes:** Controla carbohidratos y prefiere índice glucémico bajo"
    
    selected_guidance = guidance.get(query_type, guidance["general"])
    
    return {
        "status": "guidance_provided",
        "user_id": user_id,
        "query_type": query_type,
        "message": f"{selected_guidance['title']}\n\n{selected_guidance['content']}",
        "next_actions": ["nutrition_consultation", "meal_plan", "exercise_plan", "main_menu"]
    }


# Obesity Flow Agent
obesity_flow_agent = LlmAgent(
    name="obesity_flow_agent",
    model="gemini-2.5-flash",
    description="Specialized agent for obesity and weight management including weight tracking, exercise planning, and nutrition guidance.",
    instruction="""
    Eres un especialista en obesidad y manejo de peso dentro del sistema Dr. Clivi.
    
    RESPONSABILIDADES:
    - Registrar y analizar mediciones de peso
    - Crear planes de ejercicio personalizados
    - Proporcionar guía nutricional
    - Agendar citas con nutricionistas y medicina deportiva
    - Motivar y educar sobre estilo de vida saludable
    
    PRINCIPIOS:
    - Enfoque holístico: dieta + ejercicio + cambios de comportamiento
    - Metas realistas y sostenibles
    - Progreso gradual y constante
    - Apoyo emocional y motivacional
    
    RANGOS DE PESO:
    - Pérdida > 1kg/semana: Revisar estrategia
    - Pérdida 0.5-1kg/semana: Ideal
    - Sin cambios por 4+ semanas: Ajustar plan
    
    SIEMPRE celebra los logros y mantén motivación positiva.
    """,
    tools=[
        FunctionTool(func=handle_weight_measurement),
        FunctionTool(func=create_exercise_plan),
        FunctionTool(func=provide_nutrition_guidance),
        FunctionTool(func=get_patient_info),
        FunctionTool(func=update_patient_record),
        FunctionTool(func=schedule_appointment),
        FunctionTool(func=send_whatsapp_message),
        FunctionTool(func=send_interactive_message),
    ],
)
