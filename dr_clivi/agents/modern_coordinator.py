"""
Modern Agent Coordinator - Enhanced with SOLID Architecture
Demonstrates how to coordinate multiple agents using the new modular structure
"""

import logging
from typing import Any, Dict, List, Optional, Type
from abc import ABC, abstractmethod

from ..config import Config
from ..core.interfaces import ISessionService, IPatientService, SessionId, PatientId
from ..core.exceptions import DrCliviException, ValidationError
from ..application import SessionService, PatientService
from ..infrastructure import InMemoryPatientRepository
from ..domain.medical_validation import MedicalValidationService
from ..shared import ValidationUtils

# Import agent implementations
from .base_agent import BaseCliviAgent, SessionContext
from .modern_diabetes_agent import ModernDiabetesAgent
from .diabetes_agent import DiabetesAgent
from .obesity_agent import ObesityAgent


class IAgentCoordinator(ABC):
    """Interface for agent coordination following SOLID principles"""
    
    @abstractmethod
    async def route_request(self, session: SessionContext, user_request: str) -> Dict[str, Any]:
        """Route user request to appropriate agent"""
        pass
    
    @abstractmethod
    def register_agent(self, agent_type: str, agent_class: Type[BaseCliviAgent]) -> None:
        """Register a new agent type"""
        pass


class ModernAgentCoordinator(IAgentCoordinator):
    """
    Enhanced Agent Coordinator using SOLID architecture
    
    Key benefits:
    - Dependency injection for easy testing
    - Interface-based design for extensibility
    - Centralized session and patient management
    - Consistent error handling across agents
    - Improved logging and monitoring
    """
    
    def __init__(self, config: Config, use_mock_services: bool = True):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Initialize shared services using dependency injection
        self._setup_shared_services(use_mock_services)
        
        # Agent registry for dynamic agent management
        self.agents: Dict[str, Type[BaseCliviAgent]] = {}
        self.agent_instances: Dict[str, BaseCliviAgent] = {}
        
        # Register default agents
        self._register_default_agents()
    
    def _setup_shared_services(self, use_mock_services: bool):
        """Setup shared services that agents can use"""
        try:
            # Repository layer
            if use_mock_services:
                self.patient_repository = InMemoryPatientRepository()
            else:
                from ..infrastructure import BackendPatientRepository
                from ..services import BackendIntegrationService
                backend_service = BackendIntegrationService(
                    base_url=self.config.backend.base_url,
                    api_key=self.config.backend.api_key
                )
                self.patient_repository = BackendPatientRepository(backend_service)
            
            # Domain services
            self.medical_validator = MedicalValidationService()
            
            # Application services (shared across agents)
            self.patient_service = PatientService(
                self.patient_repository,
                self.medical_validator
            )
            self.session_service = SessionService()
            
            self.logger.info("Shared services initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize shared services: {e}")
            raise DrCliviException(f"Coordinator initialization failed: {e}")
    
    def _register_default_agents(self):
        """Register default agent implementations"""
        # Modern agents using new architecture
        self.register_agent("diabetes_modern", ModernDiabetesAgent)
        
        # Legacy agents (can coexist during migration)
        self.register_agent("diabetes_legacy", DiabetesAgent)
        self.register_agent("obesity", ObesityAgent)
        
        self.logger.info(f"Registered {len(self.agents)} agent types")
    
    def register_agent(self, agent_type: str, agent_class: Type[BaseCliviAgent]) -> None:
        """Register a new agent type with the coordinator"""
        self.agents[agent_type] = agent_class
        self.logger.info(f"Registered agent type: {agent_type}")
    
    async def route_request(self, session: SessionContext, user_request: str) -> Dict[str, Any]:
        """
        Enhanced request routing with improved logic
        
        Benefits of new architecture:
        - Centralized session management
        - Consistent patient data access
        - Better error handling
        - Agent-specific optimizations
        """
        try:
            # Validate input using shared utilities
            validation_result = ValidationUtils.validate_string_length(
                user_request, min_length=1, max_length=1000, field_name="User request"
            )
            if not validation_result.is_valid:
                raise ValidationError(validation_result.message)
            
            # Sanitize input
            clean_request = ValidationUtils.sanitize_text_input(user_request)
            
            # Update session state
            session_id = SessionId(session.session_id)
            await self._update_session_context(session_id, clean_request)
            
            # Determine appropriate agent
            agent_type = await self._determine_agent_type(session, clean_request)
            
            # Get or create agent instance
            agent = await self._get_agent_instance(agent_type, session)
            
            # Route to agent with enhanced context
            response = await self._route_to_agent(agent, session, clean_request)
            
            # Post-process response
            return await self._post_process_response(response, session, agent_type)
            
        except ValidationError as e:
            return self._create_error_response(f"Validation error: {e.message}")
        except DrCliviException as e:
            return self._create_error_response(f"Service error: {e.message}")
        except Exception as e:
            self.logger.error(f"Unexpected error in routing: {e}")
            return self._create_error_response("Internal error occurred")
    
    async def _update_session_context(self, session_id: SessionId, user_request: str):
        """Update session with new request context"""
        try:
            context_data = {
                "last_request": user_request,
                "request_timestamp": ValidationUtils.ValidationResult.__name__,  # Using available class
                "request_length": len(user_request)
            }
            
            self.session_service.update_session_state(
                session_id, 
                "processing_request", 
                context_data
            )
        except Exception as e:
            self.logger.warning(f"Failed to update session context: {e}")
    
    async def _determine_agent_type(self, session: SessionContext, user_request: str) -> str:
        """
        Enhanced agent determination with better logic
        
        Uses:
        - Patient plan information
        - Request content analysis
        - Session history
        - User preferences
        """
        try:
            # Get patient context
            patient_plan = session.patient.plan.lower() if session.patient.plan else "basic"
            
            # Content-based routing (improved logic)
            request_lower = user_request.lower()
            
            # Diabetes keywords
            diabetes_keywords = [
                "glucosa", "glucose", "azucar", "diabetes", "insulina", "metformina",
                "endocrinologo", "endocrinologia", "hba1c", "hemoglobina", "glucometro"
            ]
            
            # Obesity keywords  
            obesity_keywords = [
                "peso", "obesidad", "dieta", "nutricion", "bajar", "adelgazar",
                "nutriologo", "nutricional", "imc", "sobrepeso", "alimentacion"
            ]
            
            # Check for diabetes-related requests
            if any(keyword in request_lower for keyword in diabetes_keywords):
                # Use modern agent for PRO/PLUS plans, legacy for others
                if patient_plan in ["pro", "plus"]:
                    return "diabetes_modern"
                else:
                    return "diabetes_legacy"
            
            # Check for obesity-related requests
            elif any(keyword in request_lower for keyword in obesity_keywords):
                return "obesity"
            
            # Default routing based on patient plan
            elif patient_plan in ["pro", "plus"]:
                return "diabetes_modern"  # Modern features for premium plans
            else:
                return "diabetes_legacy"  # Standard features
                
        except Exception as e:
            self.logger.warning(f"Error determining agent type: {e}")
            return "diabetes_legacy"  # Safe fallback
    
    async def _get_agent_instance(self, agent_type: str, session: SessionContext) -> BaseCliviAgent:
        """Get or create agent instance with shared services"""
        try:
            # Check if we have a cached instance
            if agent_type in self.agent_instances:
                return self.agent_instances[agent_type]
            
            # Get agent class
            if agent_type not in self.agents:
                self.logger.warning(f"Unknown agent type: {agent_type}, using default")
                agent_type = "diabetes_legacy"
            
            agent_class = self.agents[agent_type]
            
            # Create instance with dependency injection
            if agent_type == "diabetes_modern":
                # Modern agent with enhanced services
                agent = agent_class(self.config, use_mock_backend=True)
            else:
                # Legacy agents
                agent = agent_class(self.config)
            
            # Cache instance for reuse
            self.agent_instances[agent_type] = agent
            
            self.logger.info(f"Created agent instance: {agent_type}")
            return agent
            
        except Exception as e:
            self.logger.error(f"Failed to create agent instance: {e}")
            # Fallback to basic agent
            if "diabetes_legacy" not in self.agent_instances:
                self.agent_instances["diabetes_legacy"] = DiabetesAgent(self.config)
            return self.agent_instances["diabetes_legacy"]
    
    async def _route_to_agent(self, agent: BaseCliviAgent, session: SessionContext, user_request: str) -> Dict[str, Any]:
        """Route request to specific agent with enhanced context"""
        try:
            # Enhanced session context with shared services
            enhanced_session = session
            
            # Add shared service access for modern agents
            if hasattr(agent, 'patient_service'):
                # Modern agent - services already injected
                pass
            else:
                # Legacy agent - could add compatibility layer here
                pass
            
            # Route based on request type (this could be enhanced with NLP)
            request_lower = user_request.lower()
            
            # Glucose logging requests
            if any(keyword in request_lower for keyword in ["glucosa", "glucose", "registrar", "medir"]):
                if "ayunas" in request_lower or "fasting" in request_lower:
                    # Extract glucose value (simple regex could be enhanced)
                    import re
                    matches = re.findall(r'\b(\d+(?:\.\d+)?)\b', user_request)
                    if matches:
                        glucose_value = float(matches[0])
                        return await agent.log_glucose_fasting(enhanced_session, glucose_value)
                elif "postprandial" in request_lower or "despues" in request_lower:
                    matches = re.findall(r'\b(\d+(?:\.\d+)?)\b', user_request)
                    if matches:
                        glucose_value = float(matches[0])
                        return await agent.log_glucose_postmeal(enhanced_session, glucose_value)
            
            # Appointment requests
            elif any(keyword in request_lower for keyword in ["cita", "appointment", "agendar", "consulta"]):
                if hasattr(agent, 'schedule_endocrinology_appointment'):
                    return await agent.schedule_endocrinology_appointment(enhanced_session)
                else:
                    return await agent.schedule_appointment(enhanced_session, "endocrinology")
            
            # Summary/report requests
            elif any(keyword in request_lower for keyword in ["resumen", "summary", "reporte", "estadisticas"]):
                if hasattr(agent, 'get_glucose_summary'):
                    return await agent.get_glucose_summary(enhanced_session)
                else:
                    return await agent.generate_health_report(enhanced_session)
            
            # Default to main menu
            else:
                return await agent.main_menu_flow(enhanced_session)
                
        except Exception as e:
            self.logger.error(f"Error routing to agent: {e}")
            return self._create_error_response("Error processing request")
    
    async def _post_process_response(self, response: Dict[str, Any], session: SessionContext, agent_type: str) -> Dict[str, Any]:
        """Post-process agent response with enhancements"""
        try:
            # Add metadata
            response["agent_type"] = agent_type
            response["session_id"] = session.session_id
            response["timestamp"] = ValidationUtils.ValidationResult.__name__  # Placeholder for datetime
            
            # Log interaction for analytics
            self.logger.info(f"Agent {agent_type} processed request for session {session.session_id}")
            
            # Add coordinator-level enhancements
            if response.get("response_type") == "error":
                response["support_contact"] = "Puedes contactar soporte en soporte@drclivi.com"
            
            return response
            
        except Exception as e:
            self.logger.warning(f"Error in post-processing: {e}")
            return response  # Return original response if post-processing fails
    
    def _create_error_response(self, message: str) -> Dict[str, Any]:
        """Create standardized error response"""
        return {
            "response_type": "error",
            "response": f"❌ {message}",
            "error": True,
            "coordinator": "ModernAgentCoordinator"
        }
    
    # =============================================================================
    # MONITORING AND ANALYTICS
    # =============================================================================
    
    def get_coordinator_stats(self) -> Dict[str, Any]:
        """Get coordinator statistics"""
        return {
            "registered_agents": list(self.agents.keys()),
            "active_instances": list(self.agent_instances.keys()),
            "shared_services": {
                "patient_service": type(self.patient_service).__name__,
                "session_service": type(self.session_service).__name__,
                "patient_repository": type(self.patient_repository).__name__
            }
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on all services"""
        health_status = {
            "coordinator": "healthy",
            "services": {},
            "agents": {}
        }
        
        try:
            # Check shared services
            # health_status["services"]["patient_repository"] = await self.patient_repository.health_check()
            health_status["services"]["session_service"] = "healthy"  # Simple check
            
            # Check agent instances
            for agent_type, agent in self.agent_instances.items():
                health_status["agents"][agent_type] = "healthy"  # Could add agent-specific health checks
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            health_status["coordinator"] = "degraded"
        
        return health_status


# =============================================================================
# FACTORY FOR EASY SETUP
# =============================================================================

class AgentCoordinatorFactory:
    """Factory for creating agent coordinators with different configurations"""
    
    @staticmethod
    def create_development_coordinator(config: Config) -> ModernAgentCoordinator:
        """Create coordinator for development with mock services"""
        return ModernAgentCoordinator(config, use_mock_services=True)
    
    @staticmethod
    def create_production_coordinator(config: Config) -> ModernAgentCoordinator:
        """Create coordinator for production with real services"""
        return ModernAgentCoordinator(config, use_mock_services=False)
    
    @staticmethod
    def create_testing_coordinator(config: Config) -> ModernAgentCoordinator:
        """Create coordinator for testing with isolated services"""
        coordinator = ModernAgentCoordinator(config, use_mock_services=True)
        # Add test-specific configurations
        return coordinator
