"""
Agente especializado en consultas Ask AI - Ejemplo de cómo los agentes "ask" 
se benefician de la nueva arquitectura SOLID.

Este agente demuestra:
1. Uso de interfaces para flexibilidad y testing
2. Inyección de dependencias para modularidad
3. Servicios compartidos para funcionalidad común
4. Manejo robusto de errores
5. Logging estructurado
6. Validación de dominio
7. Separación de responsabilidades
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from ..core.interfaces import (
    IPatientService, 
    ISessionService,
    IPageRenderer,
    IMedicalValidator,
    IAgent
)
from ..core.exceptions import (
    ValidationError,
    ServiceError,
    PatientNotFoundError
)
from ..domain.entities import Patient, MedicalQuery, QueryResult
from ..shared.validation_utils import validate_query_input
from ..shared.datetime_utils import format_consultation_datetime
from ..tools.generative_ai import ask_generative_ai, ask_specialized_ai


class AskAIAgent(IAgent):
    """
    Agente especializado en consultas Ask AI que aprovecha la nueva arquitectura SOLID.
    
    Beneficios de la nueva arquitectura:
    - Testeable: Todas las dependencias son inyectables
    - Mantenible: Responsabilidades claramente separadas
    - Extensible: Nuevas funcionalidades se agregan fácilmente
    - Robusto: Manejo de errores centralizado y consistente
    """
    
    def __init__(
        self,
        patient_service: IPatientService,
        session_service: ISessionService,
        page_renderer: IPageRenderer,
        medical_validator: IMedicalValidator,
        logger: Optional[logging.Logger] = None
    ):
        """
        Inicializar el agente con dependencias inyectadas.
        
        Args:
            patient_service: Servicio para gestión de pacientes
            session_service: Servicio para gestión de sesiones
            page_renderer: Servicio para renderizado de páginas
            medical_validator: Validador de consultas médicas
            logger: Logger opcional
        """
        self.patient_service = patient_service
        self.session_service = session_service
        self.page_renderer = page_renderer
        self.medical_validator = medical_validator
        self.logger = logger or logging.getLogger(__name__)
        
        # Configuración específica del agente Ask AI
        self.agent_config = {
            "name": "AskAI_Agent",
            "version": "2.0.0",
            "specialties": ["general_consultation", "symptom_analysis", "medication_info"],
            "max_query_length": 500,
            "response_timeout": 30
        }
        
        self.logger.info(f"AskAI Agent initialized with config: {self.agent_config}")

    async def handle_ask_query(
        self, 
        user_id: str, 
        query: str, 
        context: str = "general_consultation"
    ) -> Dict[str, Any]:
        """
        Manejar consulta Ask AI con la nueva arquitectura.
        
        Beneficios demostrados:
        1. Validación robusta usando domain services
        2. Contexto de paciente usando patient service
        3. Sesión persistente usando session service
        4. Renderizado consistente usando page renderer
        5. Manejo de errores estructurado
        """
        try:
            # 1. Validar entrada usando shared utilities
            self._validate_ask_input(query, context)
            
            # 2. Obtener contexto del paciente usando patient service
            patient_context = await self._get_patient_context(user_id)
            
            # 3. Validar consulta médica usando domain validator
            medical_query = await self._validate_medical_query(query, context, patient_context)
            
            # 4. Procesar consulta con IA
            ai_response = await self._process_ai_query(medical_query, user_id)
            
            # 5. Guardar sesión usando session service
            await self._save_query_session(user_id, medical_query, ai_response)
            
            # 6. Renderizar respuesta usando page renderer
            rendered_response = await self._render_ask_response(ai_response, patient_context)
            
            # 7. Retornar resultado estructurado
            return {
                "success": True,
                "response": rendered_response,
                "query_id": medical_query.id,
                "timestamp": format_consultation_datetime(datetime.now()),
                "agent": self.agent_config["name"],
                "context": context,
                "patient_id": patient_context.get("patient_id") if patient_context else None
            }
            
        except ValidationError as e:
            return await self._handle_validation_error(e, user_id)
        except PatientNotFoundError as e:
            return await self._handle_patient_error(e, user_id)
        except ServiceError as e:
            return await self._handle_service_error(e, user_id)
        except Exception as e:
            return await self._handle_unexpected_error(e, user_id, query)

    async def handle_specialized_query(
        self,
        user_id: str,
        query: str,
        specialty: str,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Manejar consulta especializada usando servicios de dominio.
        
        Demuestra cómo la arquitectura permite extensibilidad sin modificar código base.
        """
        try:
            # Validar especialidad
            if specialty not in self.agent_config["specialties"]:
                raise ValidationError(f"Specialty '{specialty}' not supported")
            
            # Obtener contexto completo del paciente
            patient_context = await self._get_enhanced_patient_context(user_id, specialty)
            
            # Combinar contexto adicional
            if additional_context:
                patient_context.update(additional_context)
            
            # Crear consulta médica especializada
            medical_query = MedicalQuery(
                query=query,
                context=specialty,
                patient_id=patient_context.get("patient_id"),
                specialty=specialty,
                timestamp=datetime.now()
            )
            
            # Validar usando domain validator
            await self.medical_validator.validate_specialty_query(medical_query)
            
            # Procesar con IA especializada
            ai_response = await ask_specialized_ai(
                user_request=query,
                specialty=specialty,
                patient_context=patient_context,
                user_id=user_id
            )
            
            # Guardar en sesión con contexto especializado
            await self.session_service.save_specialized_query(
                user_id=user_id,
                query=medical_query,
                response=ai_response,
                specialty=specialty
            )
            
            # Renderizar respuesta especializada
            rendered_response = await self.page_renderer.render_specialized_response(
                response=ai_response,
                specialty=specialty,
                patient_context=patient_context
            )
            
            return {
                "success": True,
                "response": rendered_response,
                "specialty": specialty,
                "query_id": medical_query.id,
                "confidence": ai_response.get("confidence", 0.0),
                "recommendations": ai_response.get("recommendations", [])
            }
            
        except Exception as e:
            self.logger.error(f"Error in specialized query: {str(e)}")
            return await self._handle_specialized_error(e, user_id, specialty)

    async def get_query_history(
        self,
        user_id: str,
        limit: int = 10,
        specialty_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Obtener historial de consultas usando session service.
        
        Demuestra cómo los servicios compartidos proporcionan funcionalidad común.
        """
        try:
            # Usar session service para obtener historial
            history = await self.session_service.get_query_history(
                user_id=user_id,
                limit=limit,
                filter_by_specialty=specialty_filter
            )
            
            # Renderizar historial usando page renderer
            rendered_history = await self.page_renderer.render_query_history(
                history=history,
                user_id=user_id
            )
            
            return {
                "success": True,
                "history": rendered_history,
                "total_queries": len(history),
                "filter_applied": specialty_filter
            }
            
        except Exception as e:
            self.logger.error(f"Error getting query history: {str(e)}")
            return {
                "success": False,
                "error": "No pude obtener el historial de consultas",
                "fallback": "¿Te gustaría hacer una nueva consulta?"
            }

    # Métodos privados que demuestran la separación de responsabilidades

    def _validate_ask_input(self, query: str, context: str) -> None:
        """Validar entrada usando shared utilities."""
        if not validate_query_input(query):
            raise ValidationError("Query input is invalid")
        
        if len(query) > self.agent_config["max_query_length"]:
            raise ValidationError(f"Query too long. Maximum {self.agent_config['max_query_length']} characters")

    async def _get_patient_context(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Obtener contexto del paciente usando patient service."""
        try:
            patient = await self.patient_service.get_patient_by_user_id(user_id)
            if patient:
                return {
                    "patient_id": patient.id,
                    "age": patient.age,
                    "gender": patient.gender,
                    "medical_history": patient.medical_history,
                    "current_medications": patient.current_medications
                }
            return None
        except PatientNotFoundError:
            # Es válido no tener paciente registrado para consultas generales
            return None

    async def _get_enhanced_patient_context(
        self, 
        user_id: str, 
        specialty: str
    ) -> Dict[str, Any]:
        """Obtener contexto mejorado del paciente para especialidades."""
        patient_context = await self._get_patient_context(user_id) or {}
        
        # Agregar contexto específico de la especialidad
        if specialty == "symptom_analysis":
            recent_symptoms = await self.patient_service.get_recent_symptoms(user_id)
            patient_context["recent_symptoms"] = recent_symptoms
        elif specialty == "medication_info":
            current_meds = await self.patient_service.get_current_medications(user_id)
            patient_context["current_medications"] = current_meds
        
        return patient_context

    async def _validate_medical_query(
        self,
        query: str,
        context: str,
        patient_context: Optional[Dict[str, Any]]
    ) -> MedicalQuery:
        """Validar consulta médica usando domain validator."""
        medical_query = MedicalQuery(
            query=query,
            context=context,
            patient_id=patient_context.get("patient_id") if patient_context else None,
            timestamp=datetime.now()
        )
        
        # Usar domain validator
        await self.medical_validator.validate_query(medical_query)
        
        return medical_query

    async def _process_ai_query(
        self,
        medical_query: MedicalQuery,
        user_id: str
    ) -> Dict[str, Any]:
        """Procesar consulta con IA."""
        return await ask_generative_ai(
            user_request=medical_query.query,
            context=medical_query.context,
            user_id=user_id,
            function_name="ASK_AI_AGENT"
        )

    async def _save_query_session(
        self,
        user_id: str,
        medical_query: MedicalQuery,
        ai_response: Dict[str, Any]
    ) -> None:
        """Guardar sesión usando session service."""
        await self.session_service.save_query_session(
            user_id=user_id,
            query=medical_query,
            response=ai_response,
            agent_name=self.agent_config["name"]
        )

    async def _render_ask_response(
        self,
        ai_response: Dict[str, Any],
        patient_context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Renderizar respuesta usando page renderer."""
        return await self.page_renderer.render_ask_response(
            ai_response=ai_response,
            patient_context=patient_context,
            agent_config=self.agent_config
        )

    # Métodos de manejo de errores que demuestran robustez

    async def _handle_validation_error(self, error: ValidationError, user_id: str) -> Dict[str, Any]:
        """Manejar errores de validación."""
        self.logger.warning(f"Validation error for user {user_id}: {str(error)}")
        return {
            "success": False,
            "error_type": "validation",
            "message": "Tu consulta no es válida. Por favor, reformúlala.",
            "suggestion": "Intenta hacer una pregunta más específica sobre tu salud."
        }

    async def _handle_patient_error(self, error: PatientNotFoundError, user_id: str) -> Dict[str, Any]:
        """Manejar errores de paciente no encontrado."""
        self.logger.info(f"Patient not found for user {user_id}: {str(error)}")
        return {
            "success": True,  # No es un error crítico
            "message": "Puedo ayudarte con información general sobre salud.",
            "suggestion": "Si quieres consultas personalizadas, puedes registrarte como paciente."
        }

    async def _handle_service_error(self, error: ServiceError, user_id: str) -> Dict[str, Any]:
        """Manejar errores de servicio."""
        self.logger.error(f"Service error for user {user_id}: {str(error)}")
        return {
            "success": False,
            "error_type": "service",
            "message": "Hay un problema temporal con el servicio.",
            "fallback": "¿Te gustaría intentar con una consulta más simple?"
        }

    async def _handle_unexpected_error(
        self, 
        error: Exception, 
        user_id: str, 
        query: str
    ) -> Dict[str, Any]:
        """Manejar errores inesperados."""
        self.logger.error(f"Unexpected error for user {user_id}, query '{query}': {str(error)}")
        return {
            "success": False,
            "error_type": "unexpected",
            "message": "Ha ocurrido un error inesperado.",
            "fallback": "Por favor, intenta de nuevo o contacta soporte."
        }

    async def _handle_specialized_error(
        self,
        error: Exception,
        user_id: str,
        specialty: str
    ) -> Dict[str, Any]:
        """Manejar errores de consultas especializadas."""
        self.logger.error(f"Specialized error for user {user_id}, specialty '{specialty}': {str(error)}")
        return {
            "success": False,
            "error_type": "specialized",
            "message": f"No pude procesar tu consulta especializada de {specialty}.",
            "fallback": "¿Te gustaría hacer una consulta general en su lugar?"
        }

    # Métodos de IAgent interface

    async def get_agent_info(self) -> Dict[str, Any]:
        """Obtener información del agente."""
        return {
            "name": self.agent_config["name"],
            "version": self.agent_config["version"],
            "specialties": self.agent_config["specialties"],
            "capabilities": [
                "general_queries",
                "specialized_queries", 
                "query_history",
                "patient_context_aware",
                "error_recovery"
            ],
            "architecture": "SOLID_compliant"
        }

    async def health_check(self) -> Dict[str, Any]:
        """Verificar salud del agente."""
        try:
            # Verificar servicios dependientes
            patient_service_ok = await self.patient_service.health_check()
            session_service_ok = await self.session_service.health_check()
            
            return {
                "status": "healthy" if patient_service_ok and session_service_ok else "degraded",
                "dependencies": {
                    "patient_service": patient_service_ok,
                    "session_service": session_service_ok
                },
                "last_check": format_consultation_datetime(datetime.now())
            }
        except Exception as e:
            self.logger.error(f"Health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }
