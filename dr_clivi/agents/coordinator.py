"""
Dr. Clivi Coordinator Agent - Routes users to appropriate specialized agents.
Based on plan status and routing logic from exported Conversational Agents flows.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

from .base_agent import BaseCliviAgent, SessionContext, PatientContext, tool
from .diabetes_agent import DiabetesAgent
from .obesity_agent import ObesityAgent
from ..config import Config


class DrCliviCoordinator(BaseCliviAgent):
    """
    Coordinator agent that routes users to appropriate specialized agents.
    
    Implements complex routing logic identified from checkPlanStatus flow:
    - Plan-based routing (PRO/PLUS/CLUB/BASIC)
    - Status-based routing (ACTIVE/SUSPENDED/CANCELED)
    - A2A communication with specialized agents
    - Fallback handling and unknown user management
    """
    
    def __init__(self, config: Config):
        super().__init__(config)
        
        # Initialize specialized agents
        self.diabetes_agent = DiabetesAgent(config)
        self.obesity_agent = ObesityAgent(config)
        
        # Routing statistics
        self._routing_stats = {
            "diabetes_routes": 0,
            "obesity_routes": 0,
            "unknown_users": 0,
            "club_routes": 0
        }
    
    def get_agent_name(self) -> str:
        return self.config.coordinator_agent.name
    
    def get_system_instructions(self) -> str:
        return f"""
        Eres el coordinador principal de Dr. Clivi, responsable de dirigir a los usuarios 
        al especialista correcto según su plan y necesidades.

        Tu función es:
        - Identificar el tipo de plan del usuario (PRO/PLUS/CLUB/BASIC)
        - Verificar el estado del plan (ACTIVE/SUSPENDED/CANCELED)
        - Enrutar a agentes especializados (Diabetes/Obesidad)
        - Manejar usuarios desconocidos o sin plan
        - Proporcionar soporte general cuando sea necesario

        Configuración:
        - Idioma: {self.config.base_agent.default_language}
        - Zona horaria: {self.config.base_agent.timezone}
        - Modelo coordinador: {self.config.coordinator_agent.model}

        Mantén un tono profesional, empático y eficiente. Tu objetivo es conectar 
        rápidamente al usuario con el especialista adecuado.
        """
    
    def get_tools(self) -> List[str]:
        """Get coordinator-specific tools"""
        base_tools = super().get_tools()
        coordinator_tools = [
            "route_to_specialist",
            "identify_user_needs",
            "handle_unknown_user",
            "manage_plan_status",
            "coordinate_agents",
            "collect_user_context"
        ]
        return base_tools + coordinator_tools
    
    @tool
    async def main_menu_flow(self, user_id: str) -> Dict[str, Any]:
        """
        Coordinator main menu - routes to appropriate specialist menu.
        """
        context = self.get_session_context(user_id)
        
        # If user context is not established, collect it first
        if not context.patient or context.user_context == "UNKNOWN":
            return await self.handle_unknown_user(user_id)
        
        # Route to appropriate specialist based on plan and preferences
        routing_result = await self.route_to_specialist(user_id)
        return routing_result
    
    @tool
    async def route_to_specialist(self, user_id: str, force_agent: str = None) -> Dict[str, Any]:
        """
        Route user to appropriate specialist agent.
        
        Implements the complex routing logic from checkPlanStatus flow analysis.
        """
        context = self.get_session_context(user_id)
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
