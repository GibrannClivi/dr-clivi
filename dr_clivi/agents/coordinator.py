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
        self.flow_handler = DeterministicFlowHandler(config)
        
        # Specialized agents for complex cases
        self.diabetes_agent = DiabetesAgent(config)
        self.obesity_agent = ObesityAgent(config)
        
        # Import and initialize AI tools
        from ..tools import generative_ai
        self.generative_ai_tool = generative_ai
        
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
            
            elif result.get("action") == "page_transition":
                return await self._handle_page_transition(user_context, result)
            
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
Eres el analizador de consultas médicas de Dr. Clivi. Tu trabajo es clasificar con precisión las consultas de pacientes para rutearlas al especialista correcto.

CONSULTA DEL PACIENTE: "{user_input}"

INFORMACIÓN DEL PACIENTE:
- Plan: {user_context.get('plan', 'UNKNOWN')}
- Historial: {user_context.get('medical_history', 'No disponible')}

ESPECIALIDADES DISPONIBLES:

1. **diabetes** - Para consultas sobre:
   - Glucosa, niveles de azúcar, mg/dL
   - Diabetes tipo 1, tipo 2, gestacional
   - Medicamentos: metformina, insulina, glibenclamida
   - Hipoglucemia, hiperglucemia
   - Complicaciones diabéticas
   - Monitoreo de glucosa
   - Hemoglobina glucosilada (HbA1c)

2. **obesity** - Para consultas sobre:
   - Pérdida de peso, bajar de peso
   - Medicamentos GLP-1: Ozempic, Saxenda, Wegovy
   - Dieta, nutrición, alimentación
   - Ejercicio, actividad física
   - IMC, obesidad
   - Cirugía bariátrica

3. **emergency** - Para emergencias médicas:
   - Dolor de pecho, dificultad respiratoria
   - Hipoglucemia severa (<70 mg/dL)
   - Hiperglucemia extrema (>300 mg/dL)
   - Síntomas de cetoacidosis
   - Reacciones adversas graves
   - "muy fuerte", "intenso", "no puedo respirar"

4. **general** - Para todo lo demás:
   - Citas, facturas, quejas
   - Hipertensión, otras condiciones
   - Preguntas generales de salud
   - Información sobre medicamentos no especializados

NIVELES DE URGENCIA:
- **critical**: Emergencias que requieren atención inmediata
- **high**: Problemas serios que necesitan respuesta rápida
- **medium**: Consultas importantes pero no urgentes
- **low**: Preguntas informativas o de rutina

INSTRUCCIONES:
1. Analiza CUIDADOSAMENTE las palabras clave en la consulta
2. Busca síntomas específicos de diabetes u obesidad
3. Evalúa la urgencia basándote en la severidad
4. Si hay palabras de emergencia, clasifica como "emergency"
5. Responde ÚNICAMENTE con el JSON solicitado

FORMATO DE RESPUESTA (JSON válido):
{{
    "specialty": "diabetes|obesity|general|emergency",
    "urgency": "low|medium|high|critical",
    "confidence": 0.0-1.0,
    "reasoning": "explicación breve de por qué elegiste esta especialidad",
    "suggested_action": "acción recomendada",
    "keywords_detected": ["palabra1", "palabra2", "palabra3"]
}}
        """
        
        try:
            # Call Gemini 2.5 Flash via the generative AI tool
            response = await self.generative_ai_tool.ask_generative_ai(
                user_request=analysis_prompt,
                context=f"Medical routing analysis for Dr. Clivi - Plan: {user_context.get('plan', 'UNKNOWN')}",
                user_id=user_context.get('user_id', 'unknown'),
                model="gemini-2.5-flash"
            )
            
            # Try to parse JSON response
            if isinstance(response, dict) and 'response' in response:
                try:
                    import json
                    response_text = response['response'].strip()
                    
                    # Try to extract JSON from response if it has extra text
                    if response_text.startswith('{') and response_text.endswith('}'):
                        parsed_response = json.loads(response_text)
                    else:
                        # Look for JSON block in response
                        import re
                        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                        if json_match:
                            parsed_response = json.loads(json_match.group())
                        else:
                            raise json.JSONDecodeError("No JSON found", response_text, 0)
                    
                    # Validate required fields
                    required_fields = ['specialty', 'urgency', 'confidence']
                    if all(field in parsed_response for field in required_fields):
                        return parsed_response
                    else:
                        raise ValueError("Missing required fields in JSON response")
                        
                except (json.JSONDecodeError, ValueError) as e:
                    logger.warning(f"Failed to parse JSON response: {e}. Raw response: {response_text}")
                    # Fallback: analyze keywords manually
                    return self._fallback_keyword_analysis(user_input, response_text)
            
            return response
            
        except Exception as e:
            logger.error(f"Error in medical query analysis: {e}")
            return self._fallback_keyword_analysis(user_input, str(e))
    
    def _fallback_keyword_analysis(self, user_input: str, ai_response: str = "") -> Dict[str, Any]:
        """
        Fallback keyword-based analysis when JSON parsing fails.
        """
        user_lower = user_input.lower()
        
        # Emergency keywords
        emergency_keywords = [
            "dolor pecho", "no puedo respirar", "dificultad respirar", "muy fuerte",
            "severo", "grave", "urgente", "emergencia", "auxilio"
        ]
        
        # Diabetes keywords  
        diabetes_keywords = [
            "glucosa", "diabetes", "diabético", "azúcar", "mg/dl", "mg/dL",
            "metformina", "insulina", "hipoglucemia", "hiperglucemia",
            "glucómetro", "hemoglobina", "hba1c"
        ]
        
        # Obesity keywords
        obesity_keywords = [
            "peso", "bajar", "adelgazar", "obesidad", "ozempic", "saxenda",
            "dieta", "ejercicio", "imc", "gordura", "grasa"
        ]
        
        # Check for emergency first
        if any(keyword in user_lower for keyword in emergency_keywords):
            return {
                "specialty": "emergency",
                "urgency": "critical",
                "confidence": 0.9,
                "reasoning": "Detected emergency keywords",
                "suggested_action": "immediate_attention",
                "keywords_detected": [kw for kw in emergency_keywords if kw in user_lower]
            }
        
        # Check for diabetes
        if any(keyword in user_lower for keyword in diabetes_keywords):
            return {
                "specialty": "diabetes", 
                "urgency": "medium",
                "confidence": 0.8,
                "reasoning": "Detected diabetes-related keywords",
                "suggested_action": "route_to_diabetes_specialist",
                "keywords_detected": [kw for kw in diabetes_keywords if kw in user_lower]
            }
        
        # Check for obesity
        if any(keyword in user_lower for keyword in obesity_keywords):
            return {
                "specialty": "obesity",
                "urgency": "medium", 
                "confidence": 0.8,
                "reasoning": "Detected obesity/weight management keywords",
                "suggested_action": "route_to_obesity_specialist",
                "keywords_detected": [kw for kw in obesity_keywords if kw in user_lower]
            }
        
        # Default to general
        return {
            "specialty": "general",
            "urgency": "medium",
            "confidence": 0.6,
            "reasoning": f"No specific specialty keywords detected. AI response: {ai_response[:100]}...",
            "suggested_action": "route_to_general",
            "keywords_detected": []
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
                patient=PatientContext(
                    patient_id=user_context.user_id,
                    name_display=user_context.patient_name,
                    plan=user_context.plan.value,
                    plan_status=user_context.plan_status.value,
                    phone_number=user_context.phone_number
                ),
                current_flow="diabetes_specialist",
                current_page="diabetes_consultation"
            )
            
            # Hand off to diabetes agent with correct parameters
            diabetes_response = await self.diabetes_agent.process_diabetes_query(
                user_input, user_context.user_id, session_context, session_context.patient
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
                patient=PatientContext(
                    patient_id=user_context.user_id,
                    name_display=user_context.patient_name,
                    plan=user_context.plan.value,
                    plan_status=user_context.plan_status.value,
                    phone_number=user_context.phone_number
                ),
                current_flow="obesity_specialist",
                current_page="obesity_consultation"
            )
            
            # Hand off to obesity agent with correct parameters
            obesity_response = await self.obesity_agent.process_obesity_query(
                user_context.user_id, user_input, {"session_context": session_context, "patient_context": session_context.patient}
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
        target_page = result.get("target_page")
        
        if target_page:
            # Renderizar la página específica usando el implementador de Dialogflow
            page_response = self.flow_handler.render_page(target_page, user_context)
            
            # Agregar información de navegación
            page_response["navigation_info"] = {
                "source_action": result.get("action"),
                "selected_option": result.get("selected_option"),
                "target_page": target_page
            }
            
            # Log del evento si está definido
            if "event_log" in result:
                logger.info(f"Logging event: {result['event_log']}")
            
            return page_response
        
        # Fallback si no hay página target
        return {
            "response_type": "general_response",
            "response": "Navegación no disponible. Regresando al menú principal.",
            "suggested_action": "show_main_menu",
            "routing_type": "navigation_error"
        }
    
    async def _handle_page_transition(self, user_context: UserContext, 
                                    result: Dict[str, Any]) -> Dict[str, Any]:
        """Maneja transiciones específicas entre páginas según Dialogflow"""
        action = result.get("action")
        
        if action == "navigate_to_page":
            target_page = result.get("target_page")
            if target_page == "End Session":
                return {
                    "response_type": "general_response",
                    "response": "Sesión finalizada. ¡Que tengas un buen día!",
                    "routing_type": "session_end"
                }
            else:
                return await self._handle_page_navigation(user_context, result)
        
        elif action == "navigate_to_flow":
            target_flow = result.get("target_flow")
            return {
                "response_type": "general_response",
                "response": f"Redirigiendo a {target_flow}. Esta funcionalidad se implementará próximamente.",
                "target_flow": target_flow,
                "routing_type": "flow_redirect"
            }
        
        elif action == "execute_function":
            function_name = result.get("function_call")
            function_params = result.get("function_params", {})
            
            # Simular llamada a función (implementar según necesidades)
            logger.info(f"Ejecutando función: {function_name} con parámetros: {function_params}")
            
            return {
                "response_type": "general_response",
                "response": f"Función {function_name} ejecutada. Por favor espera...",
                "function_call": function_name,
                "function_params": function_params,
                "routing_type": "function_execution"
            }
        
        else:
            return {
                "response_type": "general_response",
                "response": "Acción no reconocida. Regresando al menú principal.",
                "routing_type": "unknown_action"
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
    
    @tool
    async def main_menu_flow(self, user_id: str) -> Dict[str, Any]:
        """
        Main menu flow implementation for coordinator.
        Routes through the hybrid architecture.
        """
        try:
            # Get user context
            user_context = await self._get_user_context(user_id)
            
            # Check plan status and route accordingly
            plan_result = self.flow_handler.check_plan_status(user_context)
            
            if plan_result.get("action") == "show_main_menu":
                return {
                    "response_type": "whatsapp_menu",
                    "menu_data": self.flow_handler.generate_main_menu_whatsapp(user_context),
                    "flow": "diabetesPlans",
                    "page": "mainMenu",
                    "routing_type": "deterministic"
                }
            else:
                return plan_result
                
        except Exception as e:
            logger.error(f"Error in main_menu_flow: {e}")
            return await self._escalate_to_master_agent(
                await self._get_user_context(user_id), 
                "main_menu_request", 
                str(e)
            )

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
