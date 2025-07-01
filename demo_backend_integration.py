"""
Demo: Backend Integration for Dr. Clivi
Demonstrates the integration capabilities with mock backend
"""

import asyncio
import sys
import os
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dr_clivi.agents.diabetes_agent_with_backend import DiabetesAgentWithBackend
from dr_clivi.agents.base_agent import SessionContext, PatientContext
from dr_clivi.config import Config


def print_section(title: str):
    """Print formatted section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


async def main():
    """Main demo function"""
    
    print_section("🤖 DR. CLIVI - DEMO DE INTEGRACIÓN CON BACKEND")
    
    # Configure mock backend
    config = Config()
    
    # Add mock backend configuration
    config.backend = type('BackendConfig', (), {
        'use_mock': True,
        'base_url': 'https://api.drclivi.com',
        'api_key': 'demo_api_key_12345',
        'timeout': 30
    })()
    
    # Initialize enhanced agent
    agent = DiabetesAgentWithBackend(config)
    
    # Create demo session
    patient_context = PatientContext(
        patient_id="patient_123",
        name_display="Juan Pérez García",
        preferred_language="es",
        plan="PRO",
        plan_status="ACTIVE"
    )
    
    session = SessionContext(
        user_context="PATIENT",
        patient=patient_context,
        current_flow="diabetes_care",
        current_page="main_menu",
        session_start_time=datetime.now().isoformat()
    )
    
    print(f"👤 **Paciente:** {session.patient.name_display}")
    print(f"🆔 **ID:** {session.patient.patient_id}")
    print(f"💬 **Flujo:** {session.current_flow}")
    
    try:
        # Demo 1: Check appointments
        print_section("📅 ESCENARIO 1: CONSULTAR CITAS EXISTENTES")
        result = await agent.APPOINTMENT_CONFIRM(session)
        print("🤖 **Respuesta del Bot:**")
        print(result)
        
        # Demo 2: Schedule new appointment  
        print_section("📝 ESCENARIO 2: AGENDAR NUEVA CITA")
        result = await agent.SCHEDULE_NEW_APPOINTMENT(session, specialty="endocrinólogo")
        print("🤖 **Respuesta del Bot:**")
        print(result)
        
        # Demo 3: Save glucose measurement
        print_section("📊 ESCENARIO 3: REGISTRAR GLUCOSA")
        result = await agent.SAVE_MEASUREMENT(session, "glucosa_ayunas", "95")
        print("🤖 **Respuesta del Bot:**")
        print(result)
        
        # Demo 4: Generate report
        print_section(" ESCENARIO 4: GENERAR REPORTE")
        result = await agent.GENERATE_GLUCOSE_REPORT(session, days=30)
        print("🤖 **Respuesta del Bot:**")
        print(result)
        
    except Exception as e:
        print(f"❌ Error en demo específico: {e}")
    
    # ==================== BACKEND COMPARISON ====================
    
    print_section("📊 COMPARACIÓN: ANTES vs DESPUÉS DE BACKEND")
    
    print("🔴 **ANTES (Sin Backend):**")
    print("   ❌ Datos en memoria, se pierden al reiniciar")
    print("   ❌ Mensajes estáticos predefinidos")
    print("   ❌ No hay validación médica")
    print("   ❌ No hay persistencia de citas")
    print("   ❌ Reportes simulados")
    print("   ❌ No hay integración con sistemas médicos")
    
    print("\n🟢 **DESPUÉS (Con Backend):**")
    print("   ✅ Datos persistentes en base de datos")
    print("   ✅ Información dinámica y personalizada")
    print("   ✅ Validación médica automática")
    print("   ✅ Sistema de citas integrado")
    print("   ✅ Reportes basados en datos reales")
    print("   ✅ Integración con sistemas hospitalarios")
    
    print_section("🎯 BENEFICIOS DE LA INTEGRACIÓN")
    
    benefits = [
        "**Experiencia de Usuario Mejorada**: Respuestas personalizadas basadas en datos reales",
        "**Seguridad Médica**: Validación automática de valores y alertas de emergencia", 
        "**Continuidad de Atención**: Historial médico persistente y accesible",
        "**Eficiencia Operativa**: Automatización de procesos administrativos",
        "**Análisis Predictivo**: Tendencias y recomendaciones basadas en IA",
        "**Integración Hospitalaria**: Conexión con sistemas existentes",
        "**Escalabilidad**: Soporte para múltiples canales (Telegram, WhatsApp, Web)",
        "**Cumplimiento Regulatorio**: HIPAA, GDPR y normativas locales"
    ]
    
    for i, benefit in enumerate(benefits, 1):
        print(f"{i}. {benefit}")
    
    print_section("🚀 PRÓXIMOS PASOS RECOMENDADOS")
    
    next_steps = [
        "**Análisis del Backend Real**: Revisar endpoints y estructura de datos disponibles",
        "**Prototipo de Integración**: Implementar una funcionalidad como prueba de concepto",
        "**Testing Exhaustivo**: Validar que no se rompen funcionalidades existentes",
        "**Migración Gradual**: Actualizar herramientas una por una",
        "**Monitoreo y Optimización**: Implementar logging y métricas de rendimiento",
        "**Documentación**: Crear guías de integración y mantenimiento",
        "**Capacitación del Equipo**: Entrenar al personal en las nuevas funcionalidades",
        "**Despliegue en Producción**: Lanzamiento controlado con rollback preparado"
    ]
    
    for i, step in enumerate(next_steps, 1):
        print(f"{i}. {step}")
    
    print_section("✅ DEMO COMPLETADO")
    print("🎉 **La integración con backend es altamente factible y beneficiosa.**")
    print("📧 **Para continuar, necesitamos acceso al repositorio del backend.**")
    print("🔗 **Una vez disponible, podemos proceder con la implementación real.**")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⏹️  Demo interrumpido por el usuario.")
    except Exception as e:
        print(f"\n\n❌ Error en demo: {e}")
