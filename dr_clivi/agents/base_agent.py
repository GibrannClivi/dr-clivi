"""
Base agent class for Dr. Clivi specialized agents.
Provides common functionality for diabetes and obesity agents.

Note: This is a preliminary implementation that will be adapted to ADK framework.
"""

import logging
import datetime
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
from abc import ABC, abstractmethod

# TODO: Replace with actual ADK imports once available
# from adk import Agent, tool
# from adk.memory import MemoryStore  
# from adk.models import Model

from ..config import Config


def tool(func):
    """Temporary decorator for tool functions until ADK is available"""
    func._is_tool = True
    return func


@dataclass
class PatientContext:
    """Patient context from session parameters based on Conversational Agents analysis"""
    name_display: Optional[str] = None
    plan: Optional[str] = None  # PRO, PLUS, CLUB, BASIC
    plan_status: Optional[str] = None  # ACTIVE, SUSPENDED, CANCELED
    patient_id: Optional[str] = None
    phone_number: Optional[str] = None
    registration_date: Optional[str] = None
    last_activity_date: Optional[str] = None
    
    # Additional context from analysis
    preferred_language: str = "es"
    timezone: str = "America/Mexico_City"
    notification_preferences: Dict[str, bool] = None
    
    def __post_init__(self):
        if self.notification_preferences is None:
            self.notification_preferences = {
                "whatsapp": True,
                "email": False,
                "sms": False
            }


@dataclass 
class SessionContext:
    """Enhanced session context based on Conversational Agents analysis"""
    user_context: Optional[str] = None  # UNKNOWN for new users
    patient: Optional[PatientContext] = None
    current_flow: Optional[str] = None
    current_page: Optional[str] = None
    last_message: Optional[str] = None
    
    # Enhanced session tracking from flows analysis
    session_start_time: Optional[str] = None
    last_activity_time: Optional[str] = None
    flows_visited: List[str] = None
    actions_completed: List[str] = None
    errors_encountered: List[str] = None
    
    # Intent and routing context
    last_intent: Optional[str] = None
    last_intent_confidence: Optional[float] = None
    routing_history: List[Dict[str, Any]] = None
    
    # Activity tracking for analytics
    activity_events: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.flows_visited is None:
            self.flows_visited = []
        if self.actions_completed is None:
            self.actions_completed = []
        if self.errors_encountered is None:
            self.errors_encountered = []
        if self.routing_history is None:
            self.routing_history = []
        if self.activity_events is None:
            self.activity_events = []


class BaseCliviAgent(ABC):
    """
    Base agent for Dr. Clivi platform.
    
    Implements common functionality identified from Conversational Agents export:
    - Plan-based routing logic
    - Session management 
    - Common flows (help desk, complaints, end session)
    - Common tools (messaging, appointments, measurements)
    
    This will be adapted to inherit from ADK Agent class once available.
    """
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Session management
        self._session_contexts: Dict[str, SessionContext] = {}
        
        # Initialize agent settings
        self.name = self.get_agent_name()
        self.model = config.base_agent.model
        self.instructions = self.get_system_instructions()
    
    @abstractmethod
    def get_agent_name(self) -> str:
        """Get the agent name from config"""
        pass
    
    @abstractmethod
    def get_system_instructions(self) -> str:
        """Get agent-specific system instructions"""
        pass
    
    def get_tools(self) -> List[str]:
        """Get common tool names for all Clivi agents based on analysis"""
        return [
            # Messaging tools (from SEND_MESSAGE analysis)
            "send_template_message",
            "send_interactive_message",
            
            # Image processing tools (from photoScalePhoto analysis)
            "process_scale_image", 
            "analyze_medical_image",
            
            # Appointment management (from manageAppointment analysis)
            "manage_appointment",
            "schedule_appointment",
            "reschedule_appointment",
            "cancel_appointment",
            
            # Measurement tracking (from logMeasurement analysis)
            "log_measurement",
            "get_measurement_history",
            "generate_measurement_report",
            
            # Generative AI tools (from askGenerativeAI analysis)
            "ask_generative_ai",
            "get_ai_recommendation",
            
            # Flow control (from flows analysis)
            "start_flow",
            "check_plan_status",
            "route_to_specialist",
            
            # Help and support (from helpDeskSubMenu analysis)
            "help_desk_submenu",
            "technical_support",
            "billing_support",
            
            # Complaint handling (from presentComplaintTag analysis)
            "present_complaint",
            "submit_complaint",
            
            # Session management
            "end_session",
            "extend_session",
            
            # Activity tracking
            "log_activity_event",
            "track_user_interaction"
        ]
    
    def get_session_context(self, user_id: str) -> SessionContext:
        """Get or create session context for user"""
        if user_id not in self._session_contexts:
            self._session_contexts[user_id] = SessionContext()
        return self._session_contexts[user_id]
    
    def update_session_context(self, user_id: str, **kwargs):
        """Update session context with new data"""
        context = self.get_session_context(user_id)
        for key, value in kwargs.items():
            if hasattr(context, key):
                setattr(context, key, value)
            elif hasattr(context, 'patient') and hasattr(context.patient, key):
                setattr(context.patient, key, value)
    
    @tool
    async def start_flow(self, user_id: str, intent: str = "keyWordMainMenu") -> Dict[str, Any]:
        """
        Default Start Flow implementation.
        Routes to checkPlanStatus based on intent.
        
        Based on: Default Start Flow → checkPlanStatus routing
        """
        self.logger.info(f"Starting flow for user {user_id} with intent {intent}")
        
        context = self.get_session_context(user_id)
        context.current_flow = "start_flow"
        
        # Route based on intent (from analysis)
        if intent in ["keyWordMainMenu", "END_SESSION_TEMPLATE"]:
            return await self.check_plan_status(user_id)
        
        # Default fallback to plan status check
        return await self.check_plan_status(user_id)
    
    @tool
    async def check_plan_status(self, user_id: str) -> Dict[str, Any]:
        """
        Enhanced plan status check with complex routing logic from exported flows.
        
        Implements the detailed conditional logic from checkPlanStatus flow:
        - Handles all plan types: PRO, PLUS, BASIC, CLUB
        - Manages all status types: ACTIVE, SUSPENDED, CANCELED  
        - Routes to appropriate flows based on plan/status combination
        - Handles special cases like offline payments and club cancellations
        """
        self.logger.info(f"Checking plan status for user {user_id}")
        
        context = self.get_session_context(user_id)
        context.current_flow = "checkPlanStatus"
        
        # Track this activity event
        await self._log_activity_event(user_id, "PLAN_STATUS_CHECK_STARTED")
        
        # Handle unknown user context - redirect to user problems flow
        if context.user_context == "UNKNOWN" or not context.patient:
            await self._log_activity_event(user_id, "UNKNOWN_USER_DETECTED")
            return {
                "action": "redirect",
                "target": "user_problems_flow",
                "message": "Bienvenido a Dr. Clivi. Para ofrecerte el mejor servicio, necesitamos conocer tu información.",
                "next_steps": [
                    "Proporcionar número de teléfono",
                    "Verificar identidad",
                    "Configurar perfil"
                ]
            }
        
        patient = context.patient
        plan = patient.plan
        plan_status = patient.plan_status
        
        self.logger.info(f"User {user_id} has plan: {plan}, status: {plan_status}")
        
        # Plan-based routing logic from checkPlanStatus conditions analysis
        
        # Handle PRO, PLUS, BASIC plans with ACTIVE/SUSPENDED status
        if plan in ["PRO", "PLUS", "BASIC"] and plan_status in ["ACTIVE", "SUSPENDED"]:
            # Check for offline payments intent (specific condition from analysis)
            if await self._check_offline_payment_intent(user_id):
                await self._log_activity_event(user_id, "OFFLINE_PAYMENT_FLOW_STARTED")
                return await self.handle_offline_payments(user_id)
            
            # Standard routing to specialized agent menu
            await self._log_activity_event(user_id, "MAIN_MENU_FLOW_STARTED", {"plan": plan, "status": plan_status})
            return await self.main_menu_flow(user_id)
            
        # Handle CLUB plan with ACTIVE/SUSPENDED status
        elif plan == "CLUB" and plan_status in ["ACTIVE", "SUSPENDED"]:
            await self._log_activity_event(user_id, "CLUB_PLAN_FLOW_STARTED", {"status": plan_status})
            return await self.club_plan_flow(user_id)
            
        # Handle CLUB plan with CANCELED status - specific redirect
        elif plan == "CLUB" and plan_status == "CANCELED":
            await self._log_activity_event(user_id, "CLUB_CANCELED_PLAN_ACCESSED")
            return {
                "action": "redirect", 
                "target": "club_canceled_plan",
                "message": "Tu plan Club ha sido cancelado. ¿Te gustaría reactivarlo?",
                "options": [
                    {"id": "REACTIVATE_CLUB", "title": "Reactivar Plan Club"},
                    {"id": "VIEW_OTHER_PLANS", "title": "Ver otros planes"},
                    {"id": "CONTACT_SUPPORT", "title": "Contactar soporte"}
                ]
            }
        
        # Handle any plan with CANCELED status (non-CLUB)
        elif plan_status == "CANCELED":
            await self._log_activity_event(user_id, "CANCELED_PLAN_ACCESSED", {"plan": plan})
            return {
                "action": "redirect",
                "target": "plan_reactivation_flow",
                "message": f"Tu plan {plan} ha sido cancelado. Te ayudamos a reactivarlo.",
                "plan_type": plan
            }
        
        # Handle unrecognized plan types
        elif plan not in ["PRO", "PLUS", "BASIC", "CLUB"]:
            await self._log_activity_event(user_id, "UNRECOGNIZED_PLAN_TYPE", {"plan": plan})
            return {
                "action": "error",
                "message": "Tu tipo de plan no es reconocido. Por favor contacta soporte técnico.",
                "error_code": "INVALID_PLAN_TYPE",
                "support_contact": True
            }
        
        # Default fallback for any unhandled cases
        await self._log_activity_event(user_id, "PLAN_STATUS_CHECK_FALLBACK", {"plan": plan, "status": plan_status})
        return {
            "action": "error",
            "message": "No pudimos determinar tu tipo de plan o estado. Por favor contacta soporte.",
            "error_code": "PLAN_STATUS_UNDETERMINED",
            "plan": plan,
            "status": plan_status,
            "support_contact": True
        }
    
    @abstractmethod
    async def main_menu_flow(self, user_id: str) -> Dict[str, Any]:
        """Main menu flow - implemented by specialized agents"""
        pass
    
    @tool
    async def club_plan_flow(self, user_id: str) -> Dict[str, Any]:
        """
        Club plan specific flow.
        Common for both diabetes and obesity agents.
        """
        context = self.get_session_context(user_id)
        context.current_flow = "clubPlan"
        
        # Log activity event (from flows analysis)
        await self._log_activity_event(user_id, "STARTED_SESSION_DATE")
        
        return {
            "action": "menu",
            "type": "club_plan",
            "message": f"Hola {context.patient.name_display}, bienvenido al Plan Club.",
            "options": [
                {"id": "CLUB_BENEFITS", "title": "Beneficios del Club"},
                {"id": "CLUB_ACTIVITIES", "title": "Actividades disponibles"},
                {"id": "CLUB_SUPPORT", "title": "Soporte especializado"},
                {"id": "MAIN_MENU", "title": "Menú principal"}
            ]
        }
    
    @tool
    async def help_desk_submenu(self, user_id: str) -> Dict[str, Any]:
        """
        Help desk submenu - common functionality.
        From helpDeskSubMenu flow analysis.
        """
        context = self.get_session_context(user_id)
        context.current_flow = "helpDeskSubMenu"
        
        return {
            "action": "menu",
            "type": "help_desk",
            "message": "¿En qué podemos ayudarte?",
            "options": [
                {"id": "TECHNICAL_SUPPORT", "title": "Soporte técnico 🔧"},
                {"id": "BILLING_SUPPORT", "title": "Soporte de facturación 💳"},
                {"id": "APPOINTMENT_SUPPORT", "title": "Soporte de citas 📅"},
                {"id": "GENERAL_QUESTIONS", "title": "Preguntas generales ❓"},
                {"id": "BACK_TO_MENU", "title": "Volver al menú principal"}
            ]
        }
    
    @tool
    async def present_complaint(self, user_id: str, complaint_text: str = None) -> Dict[str, Any]:
        """
        Present complaint flow.
        From presentComplaintTag flow analysis.
        """
        context = self.get_session_context(user_id)
        context.current_flow = "presentComplaintTag"
        
        if not complaint_text:
            return {
                "action": "request_input",
                "message": "Por favor describe tu queja o sugerencia. Nuestro equipo la revisará y te contactará pronto.",
                "input_type": "text",
                "max_length": 500
            }
        
        # Process complaint (integrate with Clivi API)
        complaint_id = await self._submit_complaint(user_id, complaint_text)
        
        return {
            "action": "confirmation",
            "message": f"Tu queja ha sido registrada con el ID: {complaint_id}. Te contactaremos en las próximas 24 horas.",
            "complaint_id": complaint_id,
            "next_action": "main_menu"
        }
    
    @tool
    async def end_session(self, user_id: str, reason: str = "user_request") -> Dict[str, Any]:
        """
        End session flow.
        From END_SESSION flow analysis.
        """
        context = self.get_session_context(user_id)
        context.current_flow = "END_SESSION"
        
        # Log session end event
        await self._log_activity_event(user_id, "SESSION_ENDED", {"reason": reason})
        
        return {
            "action": "end_session",
            "message": "Gracias por usar Dr. Clivi. ¡Que tengas un excelente día! 🌟",
            "session_summary": {
                "duration": self._calculate_session_duration(user_id),
                "flows_visited": self._get_flows_visited(user_id),
                "actions_completed": self._get_actions_completed(user_id)
            }
        }
    
    async def handle_offline_payments(self, user_id: str) -> Dict[str, Any]:
        """
        Handle offline payments flow from checkPlanStatus conditions.
        Identified as a specific routing condition in the analysis.
        """
        context = self.get_session_context(user_id)
        context.current_flow = "offline_payments"
        
        await self._log_activity_event(user_id, "OFFLINE_PAYMENTS_ACCESSED")
        
        return {
            "action": "menu",
            "target": "offline_payments_flow",
            "message": "Te ayudamos con tu pago en efectivo. Selecciona tu opción preferida:",
            "options": [
                {
                    "id": "OXXO_PAYMENT",
                    "title": "Pago en OXXO 🏪",
                    "description": "Genera código para pagar en OXXO"
                },
                {
                    "id": "BANK_TRANSFER", 
                    "title": "Transferencia bancaria 🏦",
                    "description": "Obtén datos para transferencia"
                },
                {
                    "id": "CASH_DEPOSIT",
                    "title": "Depósito en efectivo 💵", 
                    "description": "Deposita en sucursal bancaria"
                },
                {
                    "id": "PAYMENT_HISTORY",
                    "title": "Historial de pagos 📋",
                    "description": "Ver pagos anteriores"
                }
            ]
        }

    async def _check_offline_payment_intent(self, user_id: str) -> bool:
        """
        Check if user has offline payment intent.
        Based on specific condition identified in checkPlanStatus flow.
        """
        # TODO: Implement logic to detect offline payment intent
        # This could be based on previous interactions, payment history, etc.
        return False
    
    async def _log_activity_event(self, user_id: str, event_type: str, params: Dict = None):
        """
        Enhanced activity event logging based on flows analysis.
        Tracks user interactions for analytics and session management.
        """
        if params is None:
            params = {}
            
        # Add timestamp and session context
        import datetime
        event_data = {
            "user_id": user_id,
            "event_type": event_type,
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "session_id": self._get_session_id(user_id),
            **params
        }
        
        # Add to session context for tracking
        context = self.get_session_context(user_id)
        context.activity_events.append(event_data)
        
        self.logger.info(f"Activity event: {event_type} for user {user_id}")
        
        # Send to analytics endpoint if configured
        if self.config.integrations.activity_logging_enabled:
            await self._send_activity_to_webhook(event_data)
    
    async def _send_activity_to_webhook(self, event_data: Dict[str, Any]):
        """Send activity event to n8n webhook for analytics"""
        try:
            # TODO: Implement actual webhook call
            # This would send to self.config.integrations.activity_webhook
            pass
        except Exception as e:
            self.logger.error(f"Failed to send activity event: {e}")
    
    def _get_session_id(self, user_id: str) -> str:
        """Generate or retrieve session ID for user"""
        # TODO: Implement proper session ID management
        return f"session_{user_id}_{hash(user_id) % 10000:04d}"
    
    async def _submit_complaint(self, user_id: str, complaint_text: str) -> str:
        """Submit complaint to Clivi system"""
        # Integrate with Clivi API
        return f"COMP-{user_id[-4:]}-{hash(complaint_text) % 10000:04d}"
    
    def _calculate_session_duration(self, user_id: str) -> int:
        """Calculate session duration in minutes"""
        context = self.get_session_context(user_id)
        if context.session_start_time:
            import datetime
            start_time = datetime.datetime.fromisoformat(context.session_start_time)
            current_time = datetime.datetime.utcnow()
            duration = (current_time - start_time).total_seconds() / 60
            return int(duration)
        return 0
    
    def _get_flows_visited(self, user_id: str) -> List[str]:
        """Get list of flows visited in session"""
        context = self.get_session_context(user_id)
        return list(set(context.flows_visited))  # Return unique flows
    
    def _get_actions_completed(self, user_id: str) -> List[str]:
        """Get list of actions completed in session"""
        context = self.get_session_context(user_id)
        return context.actions_completed
    
    async def handle_no_match_fallback(self, user_id: str, user_input: str) -> Dict[str, Any]:
        """
        Enhanced no-match default event handling.
        Routes to MASTER_AGENT (generative AI) from flows analysis.
        """
        self.logger.info(f"No match fallback for user {user_id}: {user_input}")
        
        context = self.get_session_context(user_id)
        context.errors_encountered.append({
            "type": "no_match",
            "user_input": user_input,
            "timestamp": datetime.datetime.utcnow().isoformat()
        })
        
        await self._log_activity_event(user_id, "NO_MATCH_FALLBACK", {
            "user_input": user_input,
            "current_flow": context.current_flow
        })
        
        # Use generative AI for intelligent fallback response
        try:
            ai_response = await self._get_generative_fallback_response(user_id, user_input)
            return {
                "action": "fallback_response",
                "message": ai_response.get("response", "No entendí completamente tu solicitud."),
                "user_input": user_input,
                "confidence": ai_response.get("confidence", 0.0),
                "suggested_actions": ai_response.get("suggested_actions", [
                    "Ir al menú principal", 
                    "Contactar soporte", 
                    "Intentar de nuevo"
                ]),
                "fallback_type": "generative_ai"
            }
        except Exception as e:
            self.logger.error(f"Generative AI fallback failed: {e}")
            return {
                "action": "fallback",
                "message": "No entendí completamente tu solicitud. ¿Podrías ser más específico?",
                "user_input": user_input,
                "suggested_actions": ["Ir al menú principal", "Contactar soporte", "Intentar de nuevo"],
                "fallback_type": "default"
            }
    
    async def handle_no_input_timeout(self, user_id: str) -> Dict[str, Any]:
        """
        Enhanced no-input default event handling.
        Routes to End Session from flows analysis with improved session management.
        """
        await self._log_activity_event(user_id, "NO_INPUT_TIMEOUT", {
            "timeout_duration": self.config.flows.no_input_timeout_seconds
        })
        
        return await self.end_session(user_id, reason="no_input_timeout")
    
    async def _get_generative_fallback_response(self, user_id: str, user_input: str) -> Dict[str, Any]:
        """
        Get intelligent fallback response using generative AI.
        Implementation of MASTER_AGENT routing from no-match analysis.
        """
        context = self.get_session_context(user_id)
        
        # TODO: Implement actual generative AI call
        # This would use the askGenerativeAI tool or similar
        
        # Placeholder response based on context
        if "cita" in user_input.lower() or "appointment" in user_input.lower():
            return {
                "response": "Parece que quieres agendar una cita. Te dirijo al menú de citas.",
                "suggested_actions": ["Agendar cita", "Ver citas existentes", "Menú principal"],
                "confidence": 0.8
            }
        elif "medicamento" in user_input.lower() or "medicina" in user_input.lower():
            return {
                "response": "¿Necesitas información sobre medicamentos? Te ayudo con eso.",
                "suggested_actions": ["Ver medicamentos", "Tutorial de medicamentos", "Contactar especialista"],
                "confidence": 0.7
            }
        else:
            return {
                "response": "No estoy seguro de entender tu solicitud. ¿Podrías ser más específico?",
                "suggested_actions": ["Menú principal", "Contactar soporte", "Intentar de nuevo"],
                "confidence": 0.3
            }
