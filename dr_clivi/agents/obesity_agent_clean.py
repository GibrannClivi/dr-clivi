"""
Obesity Agent - Specialized agent for obesity care workflows.
Based on analysis of exported Conversational Agents obesity flow.
"""

import logging
from typing import Any, Dict, List, Optional

from .base_agent import BaseCliviAgent, SessionContext, PatientContext, tool
from ..config import Config


class ObesityAgent(BaseCliviAgent):
    """
    Specialized agent for obesity care based on exported flows analysis.
    
    Implements obesity-specific flows:
    - obesityPlan main menu
    - Weight logging and body measurements
    - Workout signup categories
    - Nutrition hotline
    - Sports medicine appointments
    """
    
    def __init__(self, config: Config):
        super().__init__(config)
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def get_agent_name(self) -> str:
        return self.config.obesity_agent.name
    
    def get_system_instructions(self) -> str:
        return f"""
        Eres Dr. Clivi, un asistente médico especializado en manejo de obesidad para la plataforma Dr. Clivi.

        OBJETIVO PRINCIPAL:
        Identificar con precisión las solicitudes del usuario y enrutarlas correctamente. Tu meta principal es 
        identificar con precisión la solicitud del usuario y enrutarla correctamente. Siempre responder al usuario 
        en español y luego terminar la sesión.

        FUNCIONES PRINCIPALES:
        1. GESTIÓN DE CITAS:
           - Agendar, reprogramar y cancelar citas con especialistas en obesidad
           - Medicina deportiva y endocrinología 
           - Confirmar citas programadas
           - Aclarar que las citas son virtuales (en línea)

        2. MEDICIONES CORPORALES:
           - Peso corporal y seguimiento de tendencias
           - Circunferencia de cintura, cadera y cuello
           - IMC y análisis de progreso
           - Reportes de mediciones y gráficas de tendencias

        3. NUTRICIÓN ESPECIALIZADA (según NUTRITION_AI_AGENT):
           - Planes de comidas personalizados para obesidad
           - Verificar alergias alimentarias antes de recomendar
           - Conocimiento extenso en manejo de obesidad a través de nutrición personalizada
           - Respuestas directas basadas en evidencia, específicas para obesidad
           - Evitar sugerir consultar con nutricionista (dar respuestas directas)

        4. EJERCICIO ESPECIALIZADO (según EXERCISE_AI_AGENT):
           - Planes de ejercicio enfocados en manejo de obesidad
           - Planes personalizados y consejos adaptados a las necesidades del usuario
           - Orientación directa basada en evidencia sobre ejercicio relacionado con obesidad
           - Verificar limitaciones físicas y problemas cardiovasculares antes de recomendar
           - Evitar sugerir consultar con especialistas (dar orientación directa)

        5. SUMINISTROS Y MEDICAMENTOS:
           - Estado de envíos de medicamentos para obesidad
           - Tutoriales de inyección (GLP-1, otros)
           - Seguimiento de tratamientos

        PROTOCOLOS DE SEGURIDAD:
        - Para nutrición: preguntar sobre alergias alimentarias
        - Para ejercicio: verificar limitaciones físicas y problemas cardiovasculares 
        - Para síntomas graves: derivar a emergencias
        - Para consultas médicas complejas: escalar a especialista humano

        RESPUESTAS ESTÁNDAR:
        - "Soy Dr. Clivi. Parece que quieres [acción]. Déjame ayudarte con eso."
        - "Hola, me parece que necesitas [servicio]. Permíteme asistirte."
        - Para quejas: "Lamentamos tu experiencia. Estamos escalando tu caso con alta prioridad."

        EJEMPLOS DE MANEJO ESPECÍFICO:
        - Nutrición: "Por tu propia seguridad, antes de responderte necesitamos asegurarnos con una pregunta. ¿Eres alérgico a algún alimento?"
        - Ejercicio: "Por tu propia seguridad, antes de responderte necesitamos asegurarnos con un par de preguntas. ¿Tienes alguna limitación física? ¿Has tenido problemas cardiovasculares?"
        - Si responden negativamente a preguntas de seguridad: proceder con IA especializada
        - Si responden afirmativamente: "Por favor, escribe la palabra Clivi para ir al menú principal"

        CONFIGURACIÓN TÉCNICA:
        - Idioma: {self.config.base_agent.default_language}
        - Zona horaria: {self.config.base_agent.timezone}
        - Modelo: {self.config.obesity_agent.model}
        - Siempre responder en español
        - Terminar sesión después de cada respuesta

        EJEMPLOS REALES DE CASOS:
        - "¿Qué puedo comer para bajar de peso?" → Verificar alergias → Plan nutricional personalizado
        - "¿Qué ejercicios puedo hacer?" → Verificar limitaciones → Rutina personalizada para obesidad
        - "Mi peso está estancado" → Analizar tendencias → Recomendaciones de ajuste
        - "¿Cómo me inyecto el medicamento?" → Tutorial específico de medicamento
        """
    
    def get_tools(self) -> List[str]:
        """Get obesity-specific tools"""
        base_tools = super().get_tools()
        obesity_tools = [
            "weight_logging_flow",
            "workout_signup_flow",
            "nutrition_hotline_flow", 
            "sports_medicine_appointment_flow",
            "obesity_report_flow"
        ]
        return base_tools + obesity_tools

    async def process_obesity_query(self, user_request: str, user_id: str, 
                                   session_context: SessionContext, 
                                   patient_context: PatientContext) -> Dict[str, Any]:
        """
        Process obesity-related queries with full scenario coverage from original Dialogflow CX flows.
        Implements all scenarios from obesity MASTER_AGENT, NUTRITION_AI_AGENT, and EXERCISE_AI_AGENT.
        """
        self.logger.info(f"Processing obesity query for user {user_id}: {user_request}")
        
        # Set session context
        context = self.get_session_context(user_id)
        if session_context:
            # Update with provided session context data
            context.current_flow = session_context.current_flow or "obesity_specialist"
            context.current_page = session_context.current_page or "obesity_consultation"
            context.patient = patient_context or session_context.patient
        elif patient_context:
            context.patient = patient_context
        
        # Normalize query for pattern matching
        query_lower = user_request.lower().strip()
        
        # ONBOARDING PROCESS
        if any(keyword in query_lower for keyword in [
            "onboarding", "iniciar tratamiento", "validar datos", "comenzar", "empezar"
        ]):
            return {
                "response": "Soy Dr. Clivi. Parece que quieres iniciar con tu tratamiento. Déjame ayudarte con eso.",
                "action": "CALL_FUNCTION",
                "function_name": "ONBOARDING_SEND_LINK",
                "should_end_session": True
            }
        
        # APPOINTMENT BOOKING
        if any(keyword in query_lower for keyword in [
            "cita", "agendar", "consulta", "appointment", "médico", "endocrinólogo", "nutriólogo"
        ]):
            return {
                "response": "Soy Dr. Clivi. Parece que quieres agendar una cita. Déjame ayudarte con eso.",
                "action": "SEND_MESSAGE", 
                "template_name": "booking_catcher_ai_menu",
                "should_end_session": True,
                "followup_expected": "booking_confirmation"
            }
        
        # APPOINTMENT TYPE CLARIFICATION
        if any(keyword in query_lower for keyword in [
            "en línea", "presencial", "hospital", "virtual", "online", "videollamada"
        ]):
            return {
                "response": "Tu cita es en línea. Te enviaremos la liga 30 minutos antes.",
                "action": "SEND_MESSAGE",
                "template_name": "px_appt_list", 
                "should_end_session": True
            }
        
        # APPOINTMENT RESCHEDULING
        if any(keyword in query_lower for keyword in [
            "reprogramar", "reagendar", "cambiar cita", "mover cita", "reschedule"
        ]):
            return {
                "response": "Soy Dr. Clivi, parece que quieres reprogramar una cita. Puedo ayudarte.",
                "action": "SEND_MESSAGE",
                "template_name": "reschedule_appt_ai_menu",
                "should_end_session": True
            }
        
        # APPOINTMENT CANCELLATION
        if any(keyword in query_lower for keyword in [
            "cancelar cita", "cancel", "anular cita"
        ]):
            return {
                "response": "Soy Dr. Clivi, parece que quieres cancelar una cita. Puedo ayudarte.",
                "action": "SEND_MESSAGE", 
                "template_name": "cancel_appt_catcher_ai",
                "should_end_session": True
            }
        
        # APPOINTMENT CONFIRMATION
        if any(keyword in query_lower for keyword in [
            "confirmar cita", "confirmación", "confirm"
        ]):
            return {
                "response": "Soy Dr. Clivi, parece que quieres confirmar tu cita. Puedo ayudarte.",
                "action": "CALL_FUNCTION",
                "function_name": "APPOINTMENT_CONFIRM",
                "should_end_session": True
            }
        
        # NUTRITION QUERIES - WITH SAFETY PROTOCOL (según NUTRITION_AI_AGENT)
        if any(keyword in query_lower for keyword in [
            "nutrición", "dieta", "alimentación", "comida", "calorías", "plan alimenticio", 
            "menú", "qué comer", "nutrition", "meal plan"
        ]):
            return {
                "response": "Por tu propia seguridad, antes de responderte necesitamos asegurarnos con una pregunta. Gracias",
                "action": "NUTRITION_SAFETY_CHECK",
                "question": "¿Eres alérgico a algún alimento?",
                "context": "You are an AI nutritionist specializing in obesity, with extensive knowledge in managing and treating obesity through personalized nutrition plans. You will only respond in Spanish to the specific questions or prompts that are sent to you, providing direct, evidence-based, and specific answers tailored to the user's needs. Focus solely on obesity-related nutrition topics. Avoid suggesting to consult with a nutritionist or any specialist.",
                "should_end_session": False
            }
        
        # EXERCISE QUERIES - WITH SAFETY PROTOCOL (según EXERCISE_AI_AGENT)
        if any(keyword in query_lower for keyword in [
            "ejercicio", "exercise", "actividad física", "rutina", "entrenamiento", "gimnasio", "deporte"
        ]):
            return {
                "response": "Por tu propia seguridad, antes de responderte necesitamos asegurarnos con un par de preguntas. Gracias.",
                "action": "EXERCISE_SAFETY_CHECK",
                "questions": [
                    "¿Tienes alguna limitación física?",
                    "¿Has tenido problemas cardiovasculares en el pasado?"
                ],
                "context": "You are an AI exercise specialist focusing on obesity management, providing personalized exercise plans and advice tailored to the user's needs. You will only respond in Spanish to the specific questions or prompts sent to you, offering direct and evidence-based guidance on obesity-related exercise. Avoid suggesting to consult with a nutritionist or any specialist.",
                "should_end_session": False
            }
        
        # WEIGHT MEASUREMENTS (NUMBERS ONLY)
        if query_lower.replace(".", "").isdigit() or any(char.isdigit() for char in query_lower):
            return {
                "response": "Soy tu Dr. Clivi, creo que quieres enviar una medida. Déjame ayudarte con eso.",
                "action": "SEND_MESSAGE",
                "template_name": "px_sends_numbers_ai_no_context",
                "should_end_session": True
            }
        
        # BODY MEASUREMENTS - SPECIFIC QUERIES
        if any(keyword in query_lower for keyword in [
            "medición", "medir", "peso", "cintura", "cadera", "cuello", "measurement", "imc"
        ]):
            return {
                "response": "Soy Dr. Clivi, parece que quieres enviarnos una medición. Puedo ayudarte.",
                "action": "SEND_MESSAGE",
                "template_name": "px_sends_numbers_ai_no_context", 
                "should_end_session": True
            }
        
        # HOW TO TAKE MEASUREMENTS
        if any(keyword in query_lower for keyword in [
            "cómo medir", "how to", "tutorial medición", "instrucciones"
        ]):
            return {
                "response": "Soy Dr. Clivi, parece que quieres instrucciones para mediciones. Puedo ayudarte.",
                "action": "SEND_MESSAGE",
                "template_name": "px_sends_numbers_ai_no_context",
                "should_end_session": True
            }
        
        # LAB RESULTS / MEDICAL FILES
        if any(keyword in query_lower for keyword in [
            "resultados", "laboratorio", "recetas", "prescription", "archivos", "estudios"
        ]):
            return {
                "response": "Soy Dr. Clivi, parece que quieres ver los archivos disponibles. Puedo ayudarte.",
                "action": "SEND_MESSAGE",
                "template_name": "last_ai_file_available",
                "should_end_session": True
            }
        
        # VIDEO CALL PLATFORM QUESTIONS
        if any(keyword in query_lower for keyword in [
            "aplicación", "app", "videollamada", "plataforma", "software"
        ]):
            return {
                "response": "Soy Dr. Clivi, parece que quieres actualizar tu aplicación. Puedo ayudarte.",
                "action": "SEND_MESSAGE",
                "template_name": "update_videocall",
                "should_end_session": True
            }
        
        # COMPLAINTS ABOUT SERVICE
        if any(keyword in query_lower for keyword in [
            "queja", "mal servicio", "problema", "complaint", "insatisfecho"
        ]):
            return {
                "response": "Lamentamos tu experiencia. Estamos escalando tu caso con alta prioridad. Un agente de soporte te contactará.",
                "action": "CALL_FUNCTION", 
                "function_name": "QUESTION_SET_LAST_MESSAGE",
                "parameters": {
                    "category": "PAGOS",
                    "sendToHelpdesk": True,
                    "isKnownQuestion": True
                },
                "should_end_session": True
            }
        
        # GENERAL QUESTIONS
        if any(keyword in query_lower for keyword in [
            "pregunta", "duda", "consulta", "question", "ayuda"
        ]):
            return {
                "response": "Hola, con gusto te puedo ayudar con el envío de una pregunta a nuestro equipo",
                "action": "SEND_MESSAGE",
                "template_name": "master_general_question_ai",
                "should_end_session": True
            }
        
        # INVOICING QUERIES
        if any(keyword in query_lower for keyword in [
            "factura", "facturación", "invoice", "billing", "pago"
        ]):
            return {
                "response": "Soy Dr. Clivi, me parece que quieres apoyo con tus facturas. Yo te puedo ayudar.",
                "action": "SEND_MESSAGE",
                "template_name": "invoicing_ai_catcher",
                "should_end_session": True
            }
        
        # PAYMENT QUERIES
        if any(keyword in query_lower for keyword in [
            "pago", "payment", "cobro", "tarjeta"
        ]):
            return {
                "response": "Hola, me parece que quieres apoyo con tus pagos. Yo te puedo ayudar.",
                "action": "SEND_MESSAGE",
                "template_name": "payment_ai_catcher", 
                "should_end_session": True
            }
        
        # SHIPMENT STATUS
        if any(keyword in query_lower for keyword in [
            "envío", "shipment", "medicamento", "supplies", "medicación"
        ]):
            return {
                "response": "Me parece que quieres apoyo con tus envíos. Yo te puedo ayudar",
                "action": "SEND_MESSAGE",
                "template_name": "supplies_ai_catcher",
                "should_end_session": True
            }
        
        # PHYSICAL SYMPTOMS - EMERGENCY PROTOCOL
        if any(keyword in query_lower for keyword in [
            "me siento mal", "síntomas", "dolor", "mareo", "nausea", "emergency"
        ]):
            return {
                "response": "Comprendo tu preocupación. Te voy a conectar con nuestro servicio de especialistas.",
                "action": "SEND_MESSAGE",
                "template_name": "call_specialists_ai",
                "should_end_session": True
            }
        
        # MENTAL HEALTH CONCERNS
        if any(keyword in query_lower for keyword in [
            "depresión", "ansiedad", "mental", "psychological", "psicológico"
        ]):
            return {
                "response": "Tu bienestar mental es importante. Te conectaré con nuestro servicio de apoyo psicológico.",
                "action": "SEND_MESSAGE", 
                "template_name": "psycho_emergency_call_ai_requested",
                "should_end_session": True
            }
        
        # GRATITUDE EXPRESSIONS
        if any(keyword in query_lower for keyword in [
            "gracias", "thank", "thanks", "agradezco"
        ]):
            return {
                "response": "Gracias a ti",
                "action": "END_SESSION",
                "should_end_session": True
            }
        
        # REFERRALS
        if any(keyword in query_lower for keyword in [
            "referir", "recomendar", "referral", "amigo"
        ]):
            return {
                "response": "Soy Dr. Clivi, parece que quieres referir. Es muy sencillo compártenos su contacto por este WhatsApp.",
                "action": "END_SESSION",
                "should_end_session": True
            }
        
        # EMOJIS IN MESSAGE
        import re
        emoji_pattern = re.compile(
            "[\U0001F600-\U0001F64F]|[\U0001F300-\U0001F5FF]|[\U0001F680-\U0001F6FF]|[\U0001F1E0-\U0001F1FF]"
        )
        if emoji_pattern.search(user_request):
            return {
                "response": "Soy Dr. Clivi, solo para estar seguro. Por favor, utiliza el siguiente menú. Gracias",
                "action": "SEND_MESSAGE",
                "template_name": "master_general_question_ai",
                "should_end_session": True
            }
        
        # SUBSCRIPTION CANCELLATION
        if any(keyword in query_lower for keyword in [
            "cancelar suscripción", "cancel subscription", "dar de baja", "discontinuar"
        ]):
            return {
                "response": "Lamentamos tu experiencia. Estamos escalando tu caso con alta prioridad. Un agente de soporte te contactará.",
                "action": "CALL_FUNCTION",
                "function_name": "QUESTION_SET_LAST_MESSAGE",
                "parameters": {
                    "category": "PAGOS",
                    "sendToHelpdesk": True,
                    "isKnownQuestion": True
                },
                "should_end_session": True
            }
        
        # SPECIFIC MEDICAL QUESTIONS - ROUTE TO SPECIALIST  
        if any(keyword in query_lower for keyword in [
            "obesidad", "peso ideal", "imc", "grasa corporal", "metabolism", "metabolismo"
        ]):
            return {
                "response": "Lo lamento, no entendí tu petición voy a escalar tu caso con un especialista. Gracias por tu paciencia.",
                "action": "CALL_FUNCTION", 
                "function_name": "QUESTION_SET_LAST_MESSAGE",
                "parameters": {
                    "category": "OBESITY",
                    "sendToHelpdesk": True,
                    "isKnownQuestion": True
                },
                "should_end_session": True
            }
        
        # SINGLE WORD RESPONSES (específico para obesity agent)
        if len(query_lower.split()) == 1 and query_lower.isalpha():
            if query_lower in ["ahora", "now"]:
                return {
                    "response": "Por favor utiliza el siguiente menú para mejor asistencia.",
                    "action": "FLOW_REDIRECT",
                    "flow_name": "helpDeskSubMenu",
                    "should_end_session": True
                }
        
        # DEFAULT CASE - ROUTE TO HELP DESK
        return {
            "response": "Por favor, utiliza el siguiente menú para mejor asistencia.",
            "action": "FLOW_REDIRECT",
            "flow_name": "helpDeskSubMenu", 
            "should_end_session": True
        }
