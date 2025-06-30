"""
Dr. Clivi Intelligent Coordinator - Routes complex queries using Gemini 2.5 Flash.
Handles cases that escape deterministic flows and need AI interpretation.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

from .base_agent import BaseCliviAgent, SessionContext, PatientContext, tool
from .diabetes_agent import DiabetesAgent
from .obesity_agent import ObesityAgent
from ..config import Config
from ..flows.deterministic_handler import (
    DeterministicFlowHandler, 
    UserContext, 
    PlanType, 
    PlanStatus
)

logger = logging.getLogger(__name__)


class IntelligentCoordinator(BaseCliviAgent):
    """
    Intelligent coordinator that uses Gemini 2.5 Flash to route complex queries.
    
    Architecture:
    1. First checks if input should follow deterministic flows
    2. If not, uses AI to analyze intent and route to appropriate specialist
    3. Maintains context and handles escalations
    4. Falls back to MASTER_AGENT for unresolvable cases
    """
    
    def __init__(self, config: Config):
        super().__init__(config)
        
        # Deterministic flow handler for structured interactions
        self.flow_handler = DeterministicFlowHandler()
        
        # Specialized agents for complex cases
        self.diabetes_agent = DiabetesAgent(config)
        self.obesity_agent = ObesityAgent(config)
        
        # Routing statistics
        self._routing_stats = {
            "deterministic_routes": 0,
            "ai_routes": 0,
            "diabetes_escalations": 0,
            "obesity_escalations": 0,
            "master_agent_fallbacks": 0
        }
    
    def get_agent_name(self) -> str:
        return "dr-clivi-intelligent-coordinator"
    
    def get_system_instructions(self) -> str:
        return f"""
        Eres el Coordinador Inteligente de Dr. Clivi, especialista en ruteo de consultas médicas complejas.

        Tu función principal:
        1. Analizar consultas médicas que escapan de los flujos determinísticos
        2. Identificar la especialidad médica apropiada (diabetes, obesidad, general)
        3. Rutear inteligentemente al agente especializado correcto
        4. Manejar emergencias médicas con prioridad máxima

        Especialidades disponibles:
        - **Diabetes**: Glucosa, insulina, medicamentos diabéticos, hipoglucemia, hiperglucemia
        - **Obesidad**: Peso, dieta, medicamentos GLP-1 (Ozempic, Saxenda), ejercicio
        - **General**: Citas, facturas, quejas, soporte técnico

        Casos de emergencia (ALTA PRIORIDAD):
        - Hipoglucemia severa (<70 mg/dL)
        - Hiperglucemia extrema (>300 mg/dL)
        - Síntomas de cetoacidosis
        - Reacciones adversas a medicamentos
        - Dolor de pecho, dificultad respiratoria

        Configuración:
        - Modelo: Gemini 2.5 Flash (para análisis rápido y preciso)
        - Idioma: {self.config.base_agent.default_language}
        - Zona horaria: {self.config.base_agent.timezone}

        Responde SIEMPRE en español, sé empático y directo.
        """
    
    def get_tools(self) -> List[str]:
        """Get coordinator-specific tools"""
        base_tools = super().get_tools()
        coordinator_tools = [
            "analyze_medical_query",
            "route_to_specialist", 
            "handle_emergency",
            "escalate_to_master_agent",
            "check_deterministic_flow"
        ]
        return base_tools + coordinator_tools
    
    @tool
    async def process_user_input(self, user_id: str, user_input: str, 
                               phone_number: str = None) -> Dict[str, Any]:
        """
        Main entry point - decides between deterministic flows vs AI routing.
        """
        # Get or create user context
        user_context = await self._get_user_context(user_id, phone_number)
        
        # First check: Is this a deterministic flow interaction?
        if self.flow_handler.is_deterministic_input(user_input):
            self._routing_stats["deterministic_routes"] += 1
            return await self._handle_deterministic_flow(user_context, user_input)
        
        # Second check: Does this need intelligent routing?
        self._routing_stats["ai_routes"] += 1
        return await self._handle_intelligent_routing(user_context, user_input)
    
    async def _handle_deterministic_flow(self, user_context: UserContext, 
                                       user_input: str) -> Dict[str, Any]:
        """Handle structured menu interactions without AI"""
        try:
            result = self.flow_handler.route_deterministic_input(user_context, user_input)
            
            if result.get("action") == "show_main_menu":
                return {
                    "response_type": "whatsapp_menu",
                    "menu_data": result["menu_data"],
                    "flow": result["flow"],
                    "page": result["page"],
                    "routing_type": "deterministic"
                }
            
            elif result.get("action") == "navigate_to_page":
                return await self._handle_page_navigation(user_context, result)
            
            elif result.get("action") == "trigger_intelligent_routing":
                # Deterministic handler couldn't resolve - escalate to AI
                return await self._handle_intelligent_routing(user_context, user_input)
            
            else:
                return result
                
        except Exception as e:
            logger.error(f"Error in deterministic flow handling: {e}")
            return await self._escalate_to_master_agent(user_context, user_input, str(e))
    
    @tool 
    async def analyze_medical_query(self, user_input: str, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use Gemini 2.5 Flash to analyze medical query and determine routing.
        """
        analysis_prompt = f"""
        Analiza esta consulta médica y determina la especialidad y urgencia:

        Consulta del paciente: "{user_input}"
        
        Plan del paciente: {user_context.get('plan', 'UNKNOWN')}
        Historial: {user_context.get('medical_history', 'No disponible')}

        Responde en formato JSON:
        {{
            "specialty": "diabetes|obesity|general|emergency",
            "urgency": "low|medium|high|critical",
            "confidence": 0.0-1.0,
            "reasoning": "explicación breve",
            "suggested_action": "acción recomendada",
            "keywords_detected": ["palabra1", "palabra2"]
        }}
        """
        
        try:
            # This would call Gemini 2.5 Flash via the generative AI tool
            response = await self.generative_ai_tool.generate_response(
                prompt=analysis_prompt,
                model="gemini-2.5-flash",
                response_format="json"
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error in medical query analysis: {e}")
            return {
                "specialty": "general",
                "urgency": "medium", 
                "confidence": 0.5,
                "reasoning": f"Error en análisis: {e}",
                "suggested_action": "escalate_to_master_agent"
            }
    
    @tool
    async def route_to_specialist(self, analysis: Dict[str, Any], user_context: UserContext, 
                                user_input: str) -> Dict[str, Any]:
        """
        Route to appropriate specialist based on AI analysis.
        """
        specialty = analysis.get("specialty", "general")
        urgency = analysis.get("urgency", "medium")
        
        # Handle emergencies first
        if urgency == "critical" or specialty == "emergency":
            return await self.handle_emergency(user_context, user_input, analysis)
        
        # Route to specialized agents
        if specialty == "diabetes":
            self._routing_stats["diabetes_escalations"] += 1
            return await self._route_to_diabetes_agent(user_context, user_input, analysis)
            
        elif specialty == "obesity":
            self._routing_stats["obesity_escalations"] += 1  
            return await self._route_to_obesity_agent(user_context, user_input, analysis)
            
        elif specialty == "general":
            return await self._handle_general_query(user_context, user_input, analysis)
            
        else:
            # Fallback to master agent
            return await self._escalate_to_master_agent(user_context, user_input, 
                                                      f"Unknown specialty: {specialty}")
    
    async def _handle_intelligent_routing(self, user_context: UserContext, 
                                        user_input: str) -> Dict[str, Any]:
        """
        Handle complex queries using AI analysis and routing.
        """
        try:
            # Analyze the medical query
            analysis = await self.analyze_medical_query(
                user_input, 
                user_context.__dict__
            )
            
            # Route based on analysis
            return await self.route_to_specialist(analysis, user_context, user_input)
            
        except Exception as e:
            logger.error(f"Error in intelligent routing: {e}")
            return await self._escalate_to_master_agent(user_context, user_input, str(e))
    
    async def _route_to_diabetes_agent(self, user_context: UserContext, user_input: str,
                                     analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Route to diabetes specialist agent"""
        try:
            # Create session context for diabetes agent
            session_context = SessionContext(
                user_id=user_context.user_id,
                conversation_id=f"diabetes_{user_context.user_id}",
                patient=PatientContext(
                    user_id=user_context.user_id,
                    name=user_context.patient_name,
                    plan=user_context.plan.value,
                    plan_status=user_context.plan_status.value
                )
            )
            
            # Hand off to diabetes agent
            diabetes_response = await self.diabetes_agent.process_diabetes_query(
                session_context, user_input
            )
            
            return {
                "response_type": "specialist_response",
                "specialist": "diabetes",
                "analysis": analysis,
                "response": diabetes_response,
                "routing_type": "intelligent"
            }
            
        except Exception as e:
            logger.error(f"Error routing to diabetes agent: {e}")
            return await self._escalate_to_master_agent(user_context, user_input, str(e))
    
    async def _route_to_obesity_agent(self, user_context: UserContext, user_input: str,
                                    analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Route to obesity specialist agent"""
        try:
            # Create session context for obesity agent  
            session_context = SessionContext(
                user_id=user_context.user_id,
                conversation_id=f"obesity_{user_context.user_id}",
                patient=PatientContext(
                    user_id=user_context.user_id,
                    name=user_context.patient_name,
                    plan=user_context.plan.value,
                    plan_status=user_context.plan_status.value
                )
            )
            
            # Hand off to obesity agent
            obesity_response = await self.obesity_agent.process_obesity_query(
                session_context, user_input
            )
            
            return {
                "response_type": "specialist_response", 
                "specialist": "obesity",
                "analysis": analysis,
                "response": obesity_response,
                "routing_type": "intelligent"
            }
            
        except Exception as e:
            logger.error(f"Error routing to obesity agent: {e}")
            return await self._escalate_to_master_agent(user_context, user_input, str(e))
    
    @tool
    async def handle_emergency(self, user_context: UserContext, user_input: str,
                             analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle medical emergencies with highest priority.
        """
        emergency_response = {
            "response_type": "emergency",
            "urgency": "critical",
            "analysis": analysis,
            "immediate_actions": []
        }
        
        # Detect specific emergency types
        emergency_keywords = {
            "hypoglycemia": ["hipoglucemia", "azúcar bajo", "mareo", "sudor frío", "temblor"],
            "hyperglycemia": ["hiperglucemia", "azúcar alto", "sed excesiva", "orinar mucho"],
            "cardiac": ["dolor pecho", "dificultad respirar", "palpitaciones"],
            "medication_reaction": ["reacción", "alergia", "medicamento", "efecto adverso"]
        }
        
        detected_emergency = None
        for emergency_type, keywords in emergency_keywords.items():
            if any(keyword in user_input.lower() for keyword in keywords):
                detected_emergency = emergency_type
                break
        
        if detected_emergency == "hypoglycemia":
            emergency_response["immediate_actions"] = [
                "🚨 HIPOGLUCEMIA DETECTADA",
                "1. Consume inmediatamente 15g de azúcar (3 sobres o 1 refresco)",
                "2. Espera 15 minutos y mide tu glucosa",
                "3. Si sigue baja, repite el paso 1",
                "4. Si no mejoras, llama al 911 INMEDIATAMENTE"
            ]
        elif detected_emergency == "hyperglycemia":
            emergency_response["immediate_actions"] = [
                "⚠️ HIPERGLUCEMIA DETECTADA", 
                "1. Mide tu glucosa inmediatamente",
                "2. Si >300 mg/dL, busca atención médica URGENTE",
                "3. Bebe agua, NO bebidas azucaradas",
                "4. Si tienes cetosis, llama al 911"
            ]
        elif detected_emergency in ["cardiac", "medication_reaction"]:
            emergency_response["immediate_actions"] = [
                "🚨 EMERGENCIA MÉDICA DETECTADA",
                "1. LLAMA AL 911 INMEDIATAMENTE",
                "2. No tomes más medicamentos",
                "3. Si es posible, contacta a tu médico",
                "4. Ve al hospital más cercano"
            ]
        else:
            emergency_response["immediate_actions"] = [
                "⚠️ Situación de urgencia detectada",
                "1. Si sientes que es una emergencia, llama al 911",
                "2. Contacta a tu médico inmediatamente", 
                "3. Ve al hospital si los síntomas empeoran",
                "4. Mantén la calma y busca ayuda"
            ]
        
        # Log emergency for follow-up
        logger.critical(f"Emergency detected for user {user_context.user_id}: {detected_emergency}")
        
        return emergency_response
    
    async def _get_user_context(self, user_id: str, phone_number: str = None) -> UserContext:
        """Get or create user context with plan information"""
        # In a real implementation, this would query the user database
        # For now, we'll create a mock context
        return UserContext(
            user_id=user_id,
            patient_name="Paciente",  # Would be fetched from DB
            plan=PlanType.PRO,        # Would be fetched from DB  
            plan_status=PlanStatus.ACTIVE,  # Would be fetched from DB
            phone_number=phone_number or f"+52{user_id}",
            session_data={}
        )
    
    async def _escalate_to_master_agent(self, user_context: UserContext, user_input: str,
                                      error_reason: str) -> Dict[str, Any]:
        """Escalate to MASTER_AGENT playbook (fallback from original flows)"""
        self._routing_stats["master_agent_fallbacks"] += 1
        
        return {
            "response_type": "master_agent_escalation",
            "reason": error_reason,
            "user_input": user_input,
            "fallback_message": "Disculpa, necesito transferirte con un especialista humano. En un momento te contactaremos.",
            "routing_type": "fallback"
        }
    
    async def _handle_general_query(self, user_context: UserContext, user_input: str,
                                  analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Handle general queries that don't need specialized agents"""
        return {
            "response_type": "general_response",
            "analysis": analysis,
            "response": "Entiendo tu consulta. ¿Te gustaría que te muestre el menú principal para ayudarte mejor?",
            "suggested_action": "show_main_menu",
            "routing_type": "general"
        }
    
    async def _handle_page_navigation(self, user_context: UserContext, 
                                    result: Dict[str, Any]) -> Dict[str, Any]:
        """Handle navigation to specific pages from menu selections"""
        # This would implement the specific page logic from the original flows
        return {
            "response_type": "page_navigation",
            "target_page": result.get("target_page"),
            "target_flow": result.get("target_flow"),  
            "selected_option": result.get("selected_option"),
            "routing_type": "deterministic"
        }
        patient = context.patient
        
        if not patient:
            return await self.handle_unknown_user(user_id)
        
        self.logger.info(f"Routing user {user_id} - Plan: {patient.plan}, Status: {patient.plan_status}")
        
        # Handle forced routing (for testing or specific requests)
        if force_agent:
            return await self._route_to_specific_agent(user_id, force_agent)
        
        # Implement plan-based routing logic from flows analysis
        plan = patient.plan
        plan_status = patient.plan_status
        
        # Route based on plan and status (from checkPlanStatus conditions)
        if plan in ["PRO", "PLUS", "BASIC"] and plan_status in ["ACTIVE", "SUSPENDED"]:
            # Determine specialization based on user history or intent
            specialist = await self._determine_specialization(user_id, context)
            
            if specialist == "diabetes":
                self._routing_stats["diabetes_routes"] += 1
                return await self.diabetes_agent.main_menu_flow(user_id)
            elif specialist == "obesity":
                self._routing_stats["obesity_routes"] += 1
                return await self.obesity_agent.main_menu_flow(user_id)
            else:
                # Present choice to user
                return await self._present_specialization_choice(user_id)
        
        elif plan == "CLUB" and plan_status in ["ACTIVE", "SUSPENDED"]:
            self._routing_stats["club_routes"] += 1
            # Club plan has its own specific flow
            return await self.club_plan_flow(user_id)
        
        elif plan == "CLUB" and plan_status == "CANCELED":
            return await self._handle_canceled_club_plan(user_id)
        
        # Handle offline payments for eligible plans
        elif plan in ["PRO", "PLUS"]:
            return await self.handle_offline_payments(user_id)
        
        # Default fallback
        return await self._handle_routing_fallback(user_id)
    
    @tool
    async def identify_user_needs(self, user_id: str, user_input: str) -> Dict[str, Any]:
        """
        Analyze user input to identify their needs and route accordingly.
        """
        user_input_lower = user_input.lower()
        
        # Diabetes-related keywords
        diabetes_keywords = [
            "glucosa", "azucar", "diabetes", "insulina", "glp", "ozempic", 
            "saxenda", "wegovy", "endocrinologo", "hemoglobina", "hba1c",
            "glucometro", "tiras", "puncion"
        ]
        
        # Obesity-related keywords  
        obesity_keywords = [
            "peso", "bajar", "adelgazar", "dieta", "ejercicio", "obesidad",
            "grasa", "imc", "cintura", "cadera", "entrenamiento", "cardio",
            "nutricion", "medicina deportiva"
        ]
        
        # Count keyword matches
        diabetes_matches = sum(1 for keyword in diabetes_keywords if keyword in user_input_lower)
        obesity_matches = sum(1 for keyword in obesity_keywords if keyword in user_input_lower)
        
        # Determine intent
        if diabetes_matches > obesity_matches:
            intent = "diabetes"
            confidence = diabetes_matches / len(diabetes_keywords)
        elif obesity_matches > diabetes_matches:
            intent = "obesity"  
            confidence = obesity_matches / len(obesity_keywords)
        else:
            intent = "general"
            confidence = 0.0
        
        return {
            "intent": intent,
            "confidence": confidence,
            "diabetes_score": diabetes_matches,
            "obesity_score": obesity_matches,
            "recommendation": await self._get_routing_recommendation(intent, confidence)
        }
    
    @tool
    async def handle_unknown_user(self, user_id: str) -> Dict[str, Any]:
        """
        Handle unknown users - collect basic information and establish context.
        From userProblems flow in checkPlanStatus.
        """
        context = self.get_session_context(user_id)
        context.user_context = "UNKNOWN"
        context.current_flow = "user_onboarding"
        
        self._routing_stats["unknown_users"] += 1
        
        return {
            "action": "onboarding",
            "message": "¡Bienvenido a Dr. Clivi! 👋 Para ofrecerte el mejor servicio personalizado, necesitamos conocerte un poco.",
            "steps": [
                {
                    "step": 1,
                    "question": "¿Cuál es tu nombre?",
                    "input_type": "text",
                    "field": "name_display"
                },
                {
                    "step": 2,
                    "question": "¿Cuál es tu principal objetivo de salud?",
                    "input_type": "selection",
                    "options": [
                        {"id": "DIABETES_CARE", "title": "Control de diabetes"},
                        {"id": "WEIGHT_MANAGEMENT", "title": "Manejo de peso"},
                        {"id": "GENERAL_WELLNESS", "title": "Bienestar general"},
                        {"id": "SPECIFIC_CONDITION", "title": "Condición específica"}
                    ]
                },
                {
                    "step": 3,
                    "question": "¿Tienes algún plan activo con nosotros?",
                    "input_type": "selection",
                    "options": [
                        {"id": "YES_EXISTING", "title": "Sí, ya soy paciente"},
                        {"id": "NO_NEW", "title": "No, soy nuevo"},
                        {"id": "NOT_SURE", "title": "No estoy seguro"}
                    ]
                }
            ],
            "completion_action": "establish_user_context"
        }
    
    @tool
    async def manage_plan_status(self, user_id: str, plan: str, status: str) -> Dict[str, Any]:
        """
        Manage user plan status and update routing accordingly.
        """
        context = self.get_session_context(user_id)
        
        if not context.patient:
            context.patient = PatientContext()
        
        context.patient.plan = plan
        context.patient.plan_status = status
        
        self.logger.info(f"Updated plan status for user {user_id}: {plan} - {status}")
        
        # Log activity event (from flows analysis)
        await self._log_activity_event(user_id, "PLAN_STATUS_UPDATED", {
            "plan": plan,
            "status": status
        })
        
        return {
            "action": "plan_updated",
            "message": f"Plan actualizado: {plan} ({status})",
            "next_step": "routing_update",
            "routing_available": status in ["ACTIVE", "SUSPENDED"]
        }
    
    @tool
    async def coordinate_agents(self, user_id: str, source_agent: str, 
                              target_agent: str, context_data: Dict) -> Dict[str, Any]:
        """
        Coordinate communication between specialized agents (A2A).
        """
        self.logger.info(f"A2A coordination: {source_agent} → {target_agent} for user {user_id}")
        
        # Transfer context between agents
        session_context = self.get_session_context(user_id)
        session_context.current_flow = f"a2a_transfer_{target_agent}"
        
        # Route to target agent with transferred context
        if target_agent == "diabetes":
            return await self.diabetes_agent.main_menu_flow(user_id)
        elif target_agent == "obesity":
            return await self.obesity_agent.main_menu_flow(user_id)
        else:
            return {
                "action": "coordination_error",
                "message": "No se pudo transferir a la especialidad solicitada"
            }
    
    @tool
    async def collect_user_context(self, user_id: str, context_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Collect and process user context from onboarding or interactions.
        """
        context = self.get_session_context(user_id)
        
        # Create or update patient context
        if not context.patient:
            context.patient = PatientContext()
        
        # Process collected data
        for key, value in context_data.items():
            if hasattr(context.patient, key):
                setattr(context.patient, key, value)
        
        # Update user context status
        if context.user_context == "UNKNOWN":
            context.user_context = "IDENTIFIED"
        
        return {
            "action": "context_updated",
            "message": "Información actualizada correctamente",
            "context": context_data,
            "next_step": "proceed_to_routing"
        }
    
    # Helper methods
    async def _determine_specialization(self, user_id: str, context: SessionContext) -> str:
        """Determine user specialization based on history and context"""
        # TODO: Implement ML-based specialization detection
        # For now, return None to present choice
        return None
    
    async def _present_specialization_choice(self, user_id: str) -> Dict[str, Any]:
        """Present specialization choice to user"""
        return {
            "action": "specialization_choice",
            "message": "¿En qué área te gustaría recibir atención especializada?",
            "options": [
                {
                    "id": "DIABETES_SPECIALIST",
                    "title": "Diabetes y control glucémico",
                    "description": "Endocrinología, medicamentos, monitoreo 🩺",
                    "agent": "diabetes"
                },
                {
                    "id": "OBESITY_SPECIALIST", 
                    "title": "Manejo de peso y obesidad",
                    "description": "Nutrición, ejercicio, medicina deportiva ⚖️",
                    "agent": "obesity"
                },
                {
                    "id": "GENERAL_SUPPORT",
                    "title": "Soporte general",
                    "description": "Información general y orientación 💬",
                    "agent": "coordinator"
                }
            ]
        }
    
    async def _route_to_specific_agent(self, user_id: str, agent: str) -> Dict[str, Any]:
        """Route to specific agent (forced routing)"""
        if agent == "diabetes":
            return await self.diabetes_agent.main_menu_flow(user_id)
        elif agent == "obesity":
            return await self.obesity_agent.main_menu_flow(user_id)
        else:
            return await self.main_menu_flow(user_id)
    
    async def _handle_canceled_club_plan(self, user_id: str) -> Dict[str, Any]:
        """Handle canceled club plan users"""
        return {
            "action": "club_reactivation",
            "message": "Tu plan Club ha sido cancelado. ¿Te gustaría reactivarlo o cambiar a otro plan?",
            "options": [
                {"id": "REACTIVATE_CLUB", "title": "Reactivar Plan Club"},
                {"id": "UPGRADE_PLAN", "title": "Cambiar a otro plan"},
                {"id": "CONTACT_SUPPORT", "title": "Hablar con soporte"},
                {"id": "BROWSE_OPTIONS", "title": "Ver opciones disponibles"}
            ]
        }
    
    async def _handle_routing_fallback(self, user_id: str) -> Dict[str, Any]:
        """Handle routing fallback cases"""
        return {
            "action": "routing_fallback",
            "message": "No pudimos determinar tu plan actual. Por favor contacta a soporte para asistencia personalizada.",
            "options": [
                {"id": "CONTACT_SUPPORT", "title": "Contactar soporte"},
                {"id": "UPDATE_PLAN", "title": "Actualizar información de plan"},
                {"id": "GENERAL_INFO", "title": "Información general"}
            ]
        }
    
    async def _get_routing_recommendation(self, intent: str, confidence: float) -> Dict[str, Any]:
        """Get routing recommendation based on intent analysis"""
        if confidence > 0.3:
            return {
                "action": "direct_route",
                "target": intent,
                "confidence": confidence
            }
        else:
            return {
                "action": "present_choice",
                "reason": "unclear_intent",
                "confidence": confidence
            }
    
    def get_routing_stats(self) -> Dict[str, Any]:
        """Get routing statistics for analytics"""
        return {
            **self._routing_stats,
            "total_routes": sum(self._routing_stats.values()),
            "diabetes_percentage": self._routing_stats["diabetes_routes"] / max(sum(self._routing_stats.values()), 1) * 100,
            "obesity_percentage": self._routing_stats["obesity_routes"] / max(sum(self._routing_stats.values()), 1) * 100
        }
