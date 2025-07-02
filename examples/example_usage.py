"""
Example Usage - Modern Dr. Clivi Architecture
Demonstrates how to use the new SOLID architecture in practice
"""

import asyncio
import logging
from typing import Dict, Any

# Import the new modular components
from dr_clivi.config import Config
from dr_clivi.core.interfaces import PatientId, SessionId
from dr_clivi.core.exceptions import DrCliviException, ValidationError
from dr_clivi.agents.modern_coordinator import AgentCoordinatorFactory
from dr_clivi.agents.base_agent import SessionContext, PatientContext


async def example_diabetes_workflow():
    """
    Example workflow showing benefits of new architecture
    """
    print("🏗️ Demostración de la Nueva Arquitectura SOLID Dr. Clivi")
    print("=" * 60)
    
    # Setup
    config = Config()
    coordinator = AgentCoordinatorFactory.create_development_coordinator(config)
    
    # Create sample patient session
    patient = PatientContext(
        name_display="Juan Pérez",
        plan="PRO",
        plan_status="ACTIVE",
        patient_id="patient_123",
        phone_number="521234567890"
    )
    
    session = SessionContext(
        session_id="session_456",
        patient=patient,
        platform="whatsapp",
        language="es"
    )
    
    print(f"👤 Paciente: {patient.name_display} (Plan: {patient.plan})")
    print(f"📱 Sesión: {session.session_id} via {session.platform}")
    print()
    
    # Test scenarios showing architecture benefits
    test_scenarios = [
        {
            "name": "Registro de Glucosa en Ayunas",
            "request": "Mi glucosa en ayunas es 95 mg/dL",
            "benefits": ["Validación médica automática", "Detección de emergencias", "Almacenamiento consistente"]
        },
        {
            "name": "Glucosa Postprandial Alta",
            "request": "Después de comer tengo 210 mg/dL",
            "benefits": ["Alertas inteligentes", "Recomendaciones personalizadas", "Tracking de patrones"]
        },
        {
            "name": "Agendar Cita",
            "request": "Quiero agendar una cita con endocrinólogo",
            "benefits": ["Validación de horarios", "Integración con calendario", "Notificaciones automáticas"]
        },
        {
            "name": "Resumen de Salud",
            "request": "Dame un resumen de mis mediciones",
            "benefits": ["Análisis de tendencias", "Insights médicos", "Reportes personalizados"]
        }
    ]
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"🧪 Escenario {i}: {scenario['name']}")
        print(f"💬 Solicitud: \"{scenario['request']}\"")
        
        try:
            # Route request through new architecture
            response = await coordinator.route_request(session, scenario['request'])
            
            print(f"✅ Tipo de respuesta: {response.get('response_type', 'unknown')}")
            print(f"🤖 Agente usado: {response.get('agent_type', 'unknown')}")
            
            # Show response preview (truncated for readability)
            response_text = response.get('response', '')
            if len(response_text) > 150:
                response_text = response_text[:150] + "..."
            print(f"📝 Respuesta: {response_text}")
            
            print(f"🎯 Beneficios de la nueva arquitectura:")
            for benefit in scenario['benefits']:
                print(f"   • {benefit}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("-" * 50)
        print()
    
    # Show architecture benefits summary
    print("🏛️ BENEFICIOS DE LA ARQUITECTURA SOLID IMPLEMENTADA:")
    print()
    
    benefits = {
        "🔧 Mantenibilidad": [
            "Código organizado por responsabilidades",
            "Fácil localización de bugs",
            "Cambios aislados sin efectos secundarios"
        ],
        "🧪 Testabilidad": [
            "Componentes aislados para unit testing",
            "Mocking fácil de dependencias",
            "Tests de integración claros"
        ],
        "🚀 Escalabilidad": [
            "Nuevas funcionalidades sin romper existentes",
            "Arquitectura preparada para crecimiento",
            "Microservicios ready"
        ],
        "🔄 Reutilización": [
            "Servicios compartidos entre agentes",
            "Utilidades comunes reutilizables",
            "Patrones consistentes"
        ],
        "⚙️ Configurabilidad": [
            "Inyección de dependencias",
            "Implementaciones intercambiables",
            "Configuración por ambiente"
        ]
    }
    
    for category, items in benefits.items():
        print(f"{category}")
        for item in items:
            print(f"   • {item}")
        print()
    
    # Show coordinator statistics
    stats = coordinator.get_coordinator_stats()
    print("📊 ESTADÍSTICAS DEL COORDINADOR:")
    print(f"   • Agentes registrados: {len(stats['registered_agents'])}")
    print(f"   • Instancias activas: {len(stats['active_instances'])}")
    print(f"   • Servicios compartidos: {len(stats['shared_services'])}")
    
    # Health check
    health = await coordinator.health_check()
    print(f"   • Estado de salud: {health['coordinator']}")
    print()
    
    print("✅ ¡Demostración completada! La nueva arquitectura SOLID está lista para producción.")


async def comparison_with_legacy():
    """
    Comparison showing improvements over legacy architecture
    """
    print("📊 COMPARACIÓN: LEGACY vs NUEVA ARQUITECTURA")
    print("=" * 60)
    
    comparisons = [
        {
            "aspect": "📁 Organización del código",
            "legacy": "❌ Archivo monolítico de 2000+ líneas",
            "modern": "✅ Módulos especializados por responsabilidad"
        },
        {
            "aspect": "🧪 Testing",
            "legacy": "❌ Difícil aislar componentes",
            "modern": "✅ Componentes aislados, fácil mocking"
        },
        {
            "aspect": "🔧 Mantenimiento",
            "legacy": "❌ Cambios afectan múltiples funcionalidades",
            "modern": "✅ Cambios aislados por módulo"
        },
        {
            "aspect": "🚀 Nuevas funcionalidades",
            "legacy": "❌ Requiere modificar código existente",
            "modern": "✅ Extensión sin modificación (OCP)"
        },
        {
            "aspect": "🔄 Reutilización",
            "legacy": "❌ Código duplicado entre agentes",
            "modern": "✅ Servicios compartidos reutilizables"
        },
        {
            "aspect": "📖 Legibilidad",
            "legacy": "❌ Navegación compleja",
            "modern": "✅ Estructura predecible e intuitiva"
        },
        {
            "aspect": "🛡️ Manejo de errores",
            "legacy": "❌ Inconsistente entre módulos",
            "modern": "✅ Centralizado y consistente"
        },
        {
            "aspect": "⚙️ Configuración",
            "legacy": "❌ Hardcoded en múltiples lugares",
            "modern": "✅ Inyección de dependencias"
        }
    ]
    
    for comp in comparisons:
        print(f"{comp['aspect']}")
        print(f"   Antes:  {comp['legacy']}")
        print(f"   Ahora:  {comp['modern']}")
        print()
    
    print("🎯 RESULTADO: Mejora dramática en todos los aspectos de calidad de software")


async def development_workflow_example():
    """
    Example of how development workflow improves with new architecture
    """
    print("👨‍💻 FLUJO DE DESARROLLO MEJORADO")
    print("=" * 40)
    
    scenarios = [
        {
            "task": "Agregar nueva validación médica",
            "old_way": "Modificar archivo monolítico, riesgo de romper otras funciones",
            "new_way": "Agregar método en MedicalValidationService, testing aislado"
        },
        {
            "task": "Cambiar backend de datos",
            "old_way": "Modificar código en múltiples lugares",
            "new_way": "Implementar nueva interfaz IPatientRepository"
        },
        {
            "task": "Agregar nuevo tipo de medición",
            "old_way": "Cambios en varias clases y archivos",
            "new_way": "Agregar enum en MeasurementType, automáticamente disponible"
        },
        {
            "task": "Testing de funcionalidad específica",
            "old_way": "Setup complejo, dependencias mezcladas",
            "new_way": "Mock de interfaces específicas, testing aislado"
        }
    ]
    
    for scenario in scenarios:
        print(f"🔧 {scenario['task']}")
        print(f"   ❌ Antes: {scenario['old_way']}")
        print(f"   ✅ Ahora: {scenario['new_way']}")
        print()


async def main():
    """Run all examples"""
    try:
        await example_diabetes_workflow()
        print("\n" + "=" * 80 + "\n")
        
        await comparison_with_legacy()
        print("\n" + "=" * 80 + "\n")
        
        await development_workflow_example()
        
    except Exception as e:
        print(f"❌ Error en demostración: {e}")
        logging.exception("Full error details:")


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run examples
    asyncio.run(main())
