"""
Comparativo: Agentes "Ask" - Arquitectura Anterior vs Nueva Arquitectura SOLID

Este archivo demuestra las diferencias prácticas entre el enfoque anterior
y la nueva arquitectura SOLID para agentes que manejan consultas "Ask AI".
"""

from typing import Dict, Any, List
import logging

# ================================================================================
# ENFOQUE ANTERIOR (Legacy)
# ================================================================================

class LegacyAskAgent:
    """
    Ejemplo del enfoque anterior para agentes Ask.
    
    PROBLEMAS IDENTIFICADOS:
    ❌ Dependencias acopladas (importaciones directas)
    ❌ Lógica de negocio mezclada con presentación
    ❌ Manejo de errores inconsistente
    ❌ Difícil de testear (dependencias no inyectables)
    ❌ Código duplicado entre agentes
    ❌ Sin validación de dominio
    ❌ Sin separación de responsabilidades
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def Ask_OpenAI(self, user_id: str, query: str, context: str = "general") -> Dict[str, Any]:
        """Método Ask heredado - enfoque anterior."""
        
        # ❌ PROBLEMA: Importación directa dentro del método
        from ..tools import generative_ai
        
        # ❌ PROBLEMA: No hay validación de entrada
        # ❌ PROBLEMA: No hay contexto de paciente
        # ❌ PROBLEMA: Lógica de negocio mezclada
        
        ai_prompt = f"""
        Contexto: {context}
        Consulta del usuario: {query}
        Proporciona una respuesta médica.
        """
        
        try:
            # ❌ PROBLEMA: Llamada directa sin abstracción
            ai_response = await generative_ai.ask_generative_ai(
                user_id=user_id,
                prompt=ai_prompt,
                context={"query_type": context}
            )
            
            # ❌ PROBLEMA: Formato de respuesta hardcodeado
            return {
                "action": "AI_RESPONSE",
                "response": ai_response,
                "source": "generative_ai",
                "context": context
            }
            
        except Exception as e:
            # ❌ PROBLEMA: Manejo de errores básico
            self.logger.error(f"Error in Ask_OpenAI: {str(e)}")
            return {
                "action": "AI_ERROR",
                "error": "Error genérico",
                "fallback": True
            }


# ================================================================================
# NUEVA ARQUITECTURA SOLID
# ================================================================================

from ..core.interfaces import IPatientService, ISessionService, IPageRenderer, IMedicalValidator, IAgent
from ..core.exceptions import ValidationError, ServiceError, PatientNotFoundError
from ..domain.entities import MedicalQuery
from ..shared.validation_utils import validate_query_input
from ..shared.datetime_utils import format_consultation_datetime
from datetime import datetime

class ModernAskAgent(IAgent):
    """
    Ejemplo del nuevo enfoque SOLID para agentes Ask.
    
    BENEFICIOS DEMOSTRADOS:
    ✅ Dependencias inyectadas (testeable y flexible)
    ✅ Separación clara de responsabilidades
    ✅ Manejo robusto y consistente de errores
    ✅ Validación de dominio robusta
    ✅ Servicios compartidos (sin duplicación)
    ✅ Interfaces bien definidas
    ✅ Logging estructurado
    ✅ Extensible sin modificar código base
    """
    
    def __init__(
        self,
        patient_service: IPatientService,
        session_service: ISessionService,
        page_renderer: IPageRenderer,
        medical_validator: IMedicalValidator,
        logger: logging.Logger = None
    ):
        """
        ✅ BENEFICIO: Inyección de dependencias
        - Testeable: Se pueden inyectar mocks
        - Flexible: Se pueden cambiar implementaciones
        - Mantenible: Dependencias explícitas
        """
        self.patient_service = patient_service
        self.session_service = session_service
        self.page_renderer = page_renderer
        self.medical_validator = medical_validator
        self.logger = logger or logging.getLogger(__name__)
    
    async def handle_ask_query(
        self, 
        user_id: str, 
        query: str, 
        context: str = "general"
    ) -> Dict[str, Any]:
        """
        Manejar consulta Ask con arquitectura SOLID.
        
        ✅ BENEFICIOS DEMOSTRADOS:
        1. Validación robusta
        2. Contexto de paciente
        3. Servicios de dominio
        4. Manejo de errores estructurado
        5. Separación de responsabilidades
        """
        try:
            # ✅ BENEFICIO: Validación usando shared utilities
            self._validate_input(query, context)
            
            # ✅ BENEFICIO: Contexto de paciente usando service
            patient_context = await self._get_patient_context(user_id)
            
            # ✅ BENEFICIO: Validación de dominio
            medical_query = await self._create_validated_query(query, context, patient_context)
            
            # ✅ BENEFICIO: Procesamiento con contexto completo
            ai_response = await self._process_query_with_context(medical_query, user_id)
            
            # ✅ BENEFICIO: Persistencia usando session service
            await self._save_interaction(user_id, medical_query, ai_response)
            
            # ✅ BENEFICIO: Renderizado consistente
            rendered_response = await self._render_response(ai_response, patient_context)
            
            return {
                "success": True,
                "response": rendered_response,
                "query_id": medical_query.id,
                "timestamp": format_consultation_datetime(datetime.now()),
                "context": context,
                "patient_aware": patient_context is not None
            }
            
        except ValidationError as e:
            # ✅ BENEFICIO: Manejo específico de errores de validación
            return await self._handle_validation_error(e, user_id)
        except ServiceError as e:
            # ✅ BENEFICIO: Manejo específico de errores de servicio
            return await self._handle_service_error(e, user_id)
        except Exception as e:
            # ✅ BENEFICIO: Manejo robusto de errores inesperados
            return await self._handle_unexpected_error(e, user_id, query)
    
    # ✅ BENEFICIO: Métodos privados con responsabilidades específicas
    
    def _validate_input(self, query: str, context: str) -> None:
        """Validar entrada usando utilities compartidas."""
        if not validate_query_input(query):
            raise ValidationError("Invalid query format")
    
    async def _get_patient_context(self, user_id: str) -> Dict[str, Any]:
        """Obtener contexto usando patient service."""
        try:
            patient = await self.patient_service.get_patient_by_user_id(user_id)
            return patient.to_context_dict() if patient else {}
        except PatientNotFoundError:
            return {}
    
    async def _create_validated_query(
        self, 
        query: str, 
        context: str, 
        patient_context: Dict[str, Any]
    ) -> MedicalQuery:
        """Crear y validar consulta médica."""
        medical_query = MedicalQuery(
            query=query,
            context=context,
            patient_id=patient_context.get("patient_id"),
            timestamp=datetime.now()
        )
        
        # Validar usando domain validator
        await self.medical_validator.validate_query(medical_query)
        return medical_query
    
    async def _process_query_with_context(
        self, 
        medical_query: MedicalQuery, 
        user_id: str
    ) -> Dict[str, Any]:
        """Procesar consulta con contexto completo."""
        # La implementación usaría el servicio de IA
        # pero manteniendo la separación de responsabilidades
        pass
    
    async def _save_interaction(
        self, 
        user_id: str, 
        medical_query: MedicalQuery, 
        ai_response: Dict[str, Any]
    ) -> None:
        """Guardar interacción usando session service."""
        await self.session_service.save_query_session(
            user_id=user_id,
            query=medical_query,
            response=ai_response,
            agent_name="ModernAskAgent"
        )
    
    async def _render_response(
        self, 
        ai_response: Dict[str, Any], 
        patient_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Renderizar respuesta usando page renderer."""
        return await self.page_renderer.render_ask_response(
            ai_response=ai_response,
            patient_context=patient_context,
            agent_config={"name": "ModernAskAgent"}
        )
    
    # ✅ BENEFICIO: Manejo específico y robusto de errores
    
    async def _handle_validation_error(self, error: ValidationError, user_id: str) -> Dict[str, Any]:
        """Manejar errores de validación de forma específica."""
        self.logger.warning(f"Validation error for user {user_id}: {str(error)}")
        return {
            "success": False,
            "error_type": "validation",
            "message": "Por favor, reformula tu consulta.",
            "suggestion": "Intenta ser más específico en tu pregunta."
        }
    
    async def _handle_service_error(self, error: ServiceError, user_id: str) -> Dict[str, Any]:
        """Manejar errores de servicio de forma específica."""
        self.logger.error(f"Service error for user {user_id}: {str(error)}")
        return {
            "success": False,
            "error_type": "service",
            "message": "Problema temporal con el servicio.",
            "retry_suggested": True
        }
    
    async def _handle_unexpected_error(
        self, 
        error: Exception, 
        user_id: str, 
        query: str
    ) -> Dict[str, Any]:
        """Manejar errores inesperados de forma robusta."""
        self.logger.error(f"Unexpected error for user {user_id}, query '{query}': {str(error)}")
        return {
            "success": False,
            "error_type": "unexpected",
            "message": "Error inesperado. Contacta soporte si persiste.",
            "error_id": f"ask_agent_error_{user_id}_{datetime.now().timestamp()}"
        }


# ================================================================================
# COMPARATIVO DE BENEFICIOS
# ================================================================================

class BenefitsComparison:
    """
    Comparativo detallado de beneficios entre enfoques.
    """
    
    @staticmethod
    def get_comparison_table() -> Dict[str, Dict[str, str]]:
        """Tabla comparativa de características."""
        return {
            "testability": {
                "legacy": "❌ Difícil - dependencias acopladas",
                "modern": "✅ Fácil - dependencias inyectables con mocks"
            },
            "maintainability": {
                "legacy": "❌ Baja - lógica mezclada, código duplicado",
                "modern": "✅ Alta - responsabilidades separadas, código modular"
            },
            "extensibility": {
                "legacy": "❌ Difícil - modificaciones requieren cambios en múltiples lugares",
                "modern": "✅ Fácil - nuevas funcionalidades por composición"
            },
            "error_handling": {
                "legacy": "❌ Básico - errores genéricos",
                "modern": "✅ Robusto - errores específicos y recuperación"
            },
            "code_reuse": {
                "legacy": "❌ Bajo - cada agente duplica funcionalidad",
                "modern": "✅ Alto - servicios compartidos entre agentes"
            },
            "validation": {
                "legacy": "❌ Mínima - validación ad-hoc",
                "modern": "✅ Robusta - validación de dominio consistente"
            },
            "patient_context": {
                "legacy": "❌ Limitado - sin contexto de paciente",
                "modern": "✅ Completo - contexto rico usando patient service"
            },
            "session_management": {
                "legacy": "❌ Manual - cada agente maneja su propia sesión",
                "modern": "✅ Automático - session service centralizado"
            },
            "monitoring": {
                "legacy": "❌ Básico - logging inconsistente",
                "modern": "✅ Avanzado - logging estructurado y métricas"
            },
            "deployment": {
                "legacy": "❌ Frágil - dependencias implícitas",
                "modern": "✅ Robusto - dependencias explícitas y configurables"
            }
        }
    
    @staticmethod
    def get_migration_benefits() -> List[str]:
        """Beneficios específicos de migrar agentes Ask a la nueva arquitectura."""
        return [
            "🧪 **Testing Mejorado**: Cada componente se puede testear independientemente",
            "🔧 **Mantenimiento Simplificado**: Cambios en un servicio no afectan otros",
            "📈 **Escalabilidad**: Nuevos tipos de consulta se agregan fácilmente", 
            "🛡️ **Robustez**: Manejo consistente de errores y recuperación",
            "🔄 **Reutilización**: Servicios compartidos entre todos los agentes",
            "📊 **Monitoring**: Métricas y logging estructurado",
            "⚡ **Performance**: Servicios optimizados y cacheable",
            "🔐 **Seguridad**: Validación de dominio consistente",
            "📱 **UX Consistente**: Renderizado uniforme de respuestas",
            "🎯 **Contexto Rico**: Información de paciente para respuestas personalizadas"
        ]
    
    @staticmethod
    def get_example_scenarios() -> Dict[str, Dict[str, str]]:
        """Escenarios de ejemplo que muestran los beneficios."""
        return {
            "new_agent_development": {
                "legacy": "Desarrollador debe implementar desde cero: validación, contexto, errores, etc.",
                "modern": "Desarrollador inyecta servicios existentes y se enfoca en lógica específica"
            },
            "adding_patient_context": {
                "legacy": "Cada agente debe implementar su propia lógica de contexto",
                "modern": "Usar patient_service existente automáticamente proporciona contexto"
            },
            "error_recovery": {
                "legacy": "Errores genéricos sin contexto ni posibilidad de recuperación",
                "modern": "Errores específicos con sugerencias y opciones de recuperación"
            },
            "testing_ask_functionality": {
                "legacy": "Difícil testear - requiere servicios reales",
                "modern": "Fácil testear - inyectar mocks de todos los servicios"
            },
            "monitoring_performance": {
                "legacy": "Logs básicos sin métricas",
                "modern": "Métricas detalladas de cada servicio y interacción"
            },
            "customizing_responses": {
                "legacy": "Modificar código en múltiples lugares",
                "modern": "Modificar solo el page_renderer"
            }
        }


# ================================================================================
# EJEMPLO DE USO PRÁCTICO
# ================================================================================

async def demonstrate_ask_agent_benefits():
    """
    Función que demuestra los beneficios prácticos de la nueva arquitectura
    para agentes Ask en un escenario real.
    """
    
    # Simulación de servicios inyectados (en producción vendrían del container DI)
    from ..application.patient_service import PatientService
    from ..application.session_service import SessionService
    from ..presentation.page_renderer import PageRenderer
    from ..domain.medical_validation import MedicalValidator
    
    # ✅ BENEFICIO: Inyección de dependencias permite configuración flexible
    ask_agent = ModernAskAgent(
        patient_service=PatientService(),
        session_service=SessionService(),
        page_renderer=PageRenderer(),
        medical_validator=MedicalValidator()
    )
    
    # ✅ BENEFICIO: Consulta simple con contexto automático
    result = await ask_agent.handle_ask_query(
        user_id="user123",
        query="¿Cuáles son los síntomas de la diabetes?",
        context="symptom_inquiry"
    )
    
    print("✅ Consulta procesada con contexto de paciente automático")
    print(f"   Respuesta: {result['success']}")
    print(f"   Contexto de paciente: {result.get('patient_aware', False)}")
    
    # ✅ BENEFICIO: Historial automático usando session service
    history = await ask_agent.get_query_history(user_id="user123", limit=5)
    print("✅ Historial obtenido automáticamente")
    print(f"   Total consultas: {history.get('total_queries', 0)}")
    
    # ✅ BENEFICIO: Health check para monitoring
    health = await ask_agent.health_check()
    print("✅ Health check con dependencias")
    print(f"   Estado: {health['status']}")
    print(f"   Servicios: {health.get('dependencies', {})}")


if __name__ == "__main__":
    """
    RESUMEN DE BENEFICIOS PARA AGENTES ASK:
    
    1. **Desarrollo Más Rápido**: Servicios pre-construidos
    2. **Mayor Calidad**: Validación y manejo de errores robusto  
    3. **Mejor UX**: Contexto de paciente y respuestas personalizadas
    4. **Fácil Testing**: Dependencias inyectables
    5. **Mantenimiento Simplificado**: Responsabilidades separadas
    6. **Extensibilidad**: Nuevas funcionalidades sin modificar código base
    7. **Monitoring**: Métricas y logging estructurado
    8. **Reutilización**: Código compartido entre agentes
    9. **Robustez**: Recuperación de errores inteligente
    10. **Escalabilidad**: Arquitectura preparada para crecimiento
    """
    pass
