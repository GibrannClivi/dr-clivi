"""
Diabetes Agent - Specialized agent for diabetes care workflows.
Based on analysis of exported Conversational Agents diabetes flow.
"""

import logging
from typing import Any, Dict, List, Optional

from .base_agent import BaseCliviAgent, SessionContext, PatientContext, tool
from ..config import Config


class DiabetesAgent(BaseCliviAgent):
    """
    Specialized agent for diabetes care based on exported flows analysis.
    
    Implements diabetes-specific flows:
    - diabetesPlans main menu
    - Glucose logging (fasting/post-meal) 
    - Medication tutorials (GLP-1)
    - Supplies management (glucometer, strips)
    - Endocrinology appointments
    """
    
    def __init__(self, config: Config):
        super().__init__(config)
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def get_agent_name(self) -> str:
        return self.config.diabetes_agent.name
    
    def get_system_instructions(self) -> str:
        return f"""
        Eres Dr. Clivi, un asistente médico especializado en diabetes tipo 2 para la plataforma Dr. Clivi.

        OBJETIVO PRINCIPAL:
        Identificar con precisión las solicitudes del usuario usando el parámetro `userRequest` y enrutarlas según las 
        instrucciones proporcionadas. Siempre terminar la sesión después de responder al usuario en español.

        FUNCIONES PRINCIPALES:
        1. GESTIÓN DE CITAS:
           - Agendar, reprogramar y cancelar citas con endocrinólogo
           - Confirmar citas programadas
           - Aclarar que las citas son virtuales (en línea)
           - Enviar enlaces de videollamada 30 minutos antes

        2. MEDICIONES DE GLUCOSA:
           - Registrar glucosa en ayunas (70-130 mg/dL normal)
           - Registrar glucosa postprandial (menos de 180 mg/dL normal)
           - Asesorar sobre horarios de medición
           - Generar reportes de tendencias

        3. MEDICIONES CORPORALES:
           - Peso corporal
           - Circunferencia de cintura
           - Circunferencia de cadera
           - Circunferencia de cuello

        4. GESTIÓN DE MEDICAMENTOS:
           - Tutoriales de inyección para GLP-1 (Ozempic, Saxenda, Wegovy)
           - Recordatorios de medicación
           - Efectos secundarios comunes
           - Almacenamiento correcto

        5. SUMINISTROS MÉDICOS:
           - Estado de envíos de glucómetro
           - Tiras reactivas
           - Lancetas
           - Agujas para plumas de insulina

        6. EJERCICIO ESPECIALIZADO (según EXERCISE_AI_AGENT):
           - Planes de ejercicio para diabéticos tipo 2
           - Ejercicio aeróbico y entrenamiento de fuerza
           - Rutinas seguras para controlar glucosa
           - Verificar limitaciones físicas y cardiovasculares antes de recomendar

        PROTOCOLOS DE SEGURIDAD:
        - Para ejercicio: preguntar sobre limitaciones físicas y problemas cardiovasculares
        - Para síntomas graves: derivar a emergencias
        - Para consultas médicas complejas: escalar a especialista humano

        RESPUESTAS ESTÁNDAR:
        - "Soy Dr. Clivi, parece que quieres [acción]. Puedo ayudarte."
        - "Hola, me parece que necesitas [servicio]. Déjame asistirte."
        - Para quejas: "Lamento mucho tu mala experiencia. Estoy escalando tu caso con un agente de soporte."

        CONFIGURACIÓN TÉCNICA:
        - Idioma: {self.config.base_agent.default_language}
        - Zona horaria: {self.config.base_agent.timezone}
        - Modelo: {self.config.diabetes_agent.model}
        - Siempre responder en español
        - Terminar sesión después de cada respuesta

        EJEMPLOS DE MANEJO:
        - "¿Cuándo debo medirme la glucosa?" → Explicar horarios de ayunas y postprandial
        - "Mi glucosa está en 200" → Recomendar contactar médico, registrar medición
        - "¿Cómo me inyecto Ozempic?" → Activar tutorial de medicamento
        - "Quiero hacer ejercicio" → Verificar limitaciones antes de recomendar rutinas
        """
    
    def get_tools(self) -> List[str]:
        """Get diabetes-specific tools"""
        base_tools = super().get_tools()
        diabetes_tools = [
            "glucose_logging_flow",
            "medication_tutorial_flow", 
            "supplies_management_flow",
            "endocrinology_appointment_flow",
            "glucose_report_flow"
        ]
        return base_tools + diabetes_tools

    async def process_diabetes_query(self, user_request: str, user_id: str, 
                                    session_context: SessionContext, 
                                    patient_context: PatientContext) -> Dict[str, Any]:
        """
        Process diabetes-related queries with full scenario coverage from original Dialogflow CX flows.
        Implements all scenarios from MASTER_AGENT and EXERCISE_AI_AGENT instructions.
        """
        self.logger.info(f"Processing diabetes query for user {user_id}: {user_request}")
        
        # Set session context
        context = self.get_session_context(user_id)
        if session_context:
            # Update with provided session context data
            context.current_flow = session_context.current_flow or "diabetes_specialist"
            context.current_page = session_context.current_page or "diabetes_consultation"
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
            "cita", "agendar", "consulta", "appointment", "médico", "endocrinólogo"
        ]):
            return {
                "response": "Soy Dr. Clivi. Parece que quieres agendar una cita. Es correcto?",
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
        
        # GLUCOSE MEASUREMENTS (NUMBERS ONLY)
        if query_lower.replace(".", "").isdigit() or any(char.isdigit() for char in query_lower):
            return {
                "response": "Soy tu Dr. Clivi, creo que quieres enviar una medida. Déjame ayudarte con eso.",
                "action": "SEND_MESSAGE",
                "template_name": "px_sends_numbers_ai_no_context",
                "should_end_session": True
            }
        
        # BODY MEASUREMENTS - SPECIFIC QUERIES
        if any(keyword in query_lower for keyword in [
            "medición", "medir", "glucosa", "peso", "cintura", "cadera", "measurement"
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
        
        # EXERCISE QUERIES - WITH SAFETY PROTOCOL
        if any(keyword in query_lower for keyword in [
            "ejercicio", "exercise", "actividad física", "rutina", "entrenamiento"
        ]):
            return {
                "response": "Por tu propia seguridad, antes de responderte necesitamos asegurarnos con un par de preguntas. Gracias.",
                "action": "EXERCISE_SAFETY_CHECK",
                "questions": [
                    "¿Tienes alguna limitación física como problemas articulares?",
                    "¿Has tenido problemas cardiovasculares como dolor en el pecho, falta de aire o mareos durante o después de actividad física?"
                ],
                "context": "You are an AI exercise specialist focused on managing type 2 diabetes. Provide personalized exercise plans and evidence-based advice to help control blood sugar levels.",
                "should_end_session": False
            }
        
        # COMPLAINTS ABOUT SERVICE
        if any(keyword in query_lower for keyword in [
            "queja", "mal servicio", "problema", "complaint", "insatisfecho"
        ]):
            return {
                "response": "Lamento mucho tu mala experiencia. Estoy escalando tu caso con un agente de soporte. Dame unos momentos. Por favor.",
                "action": "CALL_FUNCTION", 
                "function_name": "QUESTION_SET_LAST_MESSAGE",
                "parameters": {
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
            "envío", "shipment", "glucómetro", "tiras", "medicamento", "supplies"
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
            "diabetes", "glucosa alta", "insulina", "hemoglobina", "a1c", "complications"
        ]):
            return {
                "response": "Lo lamento, no entendí tu petición voy a escalar tu caso con un especialista. Gracias por tu paciencia.",
                "action": "CALL_FUNCTION", 
                "function_name": "QUESTION_SET_LAST_MESSAGE",
                "parameters": {
                    "category": "DIABETES",
                    "sendToHelpdesk": True,
                    "isKnownQuestion": True
                },
                "should_end_session": True
            }
        
        # SINGLE WORD RESPONSES
        if len(query_lower.split()) == 1 and query_lower.isalpha():
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
