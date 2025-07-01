#!/usr/bin/env python3
"""
Debug script para probar el ruteo inteligente del coordinador.
Verifica paso a paso qué está fallando en el análisis de consultas médicas.
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Agregar el directorio padre al path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from dr_clivi.config import Config
from dr_clivi.agents.coordinator import IntelligentCoordinator
from dr_clivi.flows.deterministic_handler import UserContext, PlanType, PlanStatus

# Configurar logging para debug
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_intelligent_routing():
    """Probar el ruteo inteligente paso a paso"""
    print("🔍 DEBUG - RUTEO INTELIGENTE DEL COORDINADOR")
    print("=" * 60)
    
    # Cargar configuración
    config = Config()
    coordinator = IntelligentCoordinator(config)
    
    # Casos de prueba que deberían ir a ruteo inteligente
    test_cases = [
        {
            "input": "Tengo diabetes y mi glucosa está en 180 mg/dl",
            "expected_specialty": "diabetes",
            "expected_urgency": "medium"
        },
        {
            "input": "¿Cuándo debo tomar la metformina?",
            "expected_specialty": "diabetes",
            "expected_urgency": "low"
        },
        {
            "input": "Necesito ayuda para bajar de peso",
            "expected_specialty": "obesity", 
            "expected_urgency": "low"
        },
        {
            "input": "Tengo dolor en el pecho muy fuerte",
            "expected_specialty": "emergency",
            "expected_urgency": "critical"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 TEST {i}: {test_case['input']}")
        print("-" * 50)
        
        # Crear contexto de usuario de prueba
        user_context = UserContext(
            user_id="debug_user_123",
            patient_name="Paciente Debug",
            phone_number="+1234567890",
            plan=PlanType.PRO,
            plan_status=PlanStatus.ACTIVE
        )
        
        try:
            # 1. Verificar que NO sea determinístico
            is_deterministic = coordinator.flow_handler.is_deterministic_input(test_case["input"])
            print(f"✅ is_deterministic_input: {is_deterministic} (esperado: False)")
            
            if is_deterministic:
                print("⚠️  ERROR: Esta consulta se clasificó como determinística cuando debería ir a IA")
                continue
            
            # 2. Probar análisis médico con Gemini
            print("🧠 Probando análisis médico con Gemini...")
            analysis = await coordinator.analyze_medical_query(
                test_case["input"], 
                user_context.__dict__
            )
            
            print(f"📋 Análisis resultado:")
            print(f"   - Especialidad: {analysis.get('specialty', 'N/A')}")
            print(f"   - Urgencia: {analysis.get('urgency', 'N/A')}")  
            print(f"   - Confianza: {analysis.get('confidence', 'N/A')}")
            print(f"   - Razonamiento: {analysis.get('reasoning', 'N/A')}")
            print(f"   - Acción sugerida: {analysis.get('suggested_action', 'N/A')}")
            
            # 3. Verificar ruteo basado en análisis
            print("🎯 Probando ruteo a especialista...")
            routing_result = await coordinator.route_to_specialist(
                analysis, user_context, test_case["input"]
            )
            
            print(f"📊 Resultado de ruteo:")
            print(f"   - Tipo de respuesta: {routing_result.get('response_type', 'N/A')}")
            print(f"   - Especialista: {routing_result.get('specialist', 'N/A')}")
            print(f"   - Tipo de ruteo: {routing_result.get('routing_type', 'N/A')}")
            
            # 4. Verificar si coincide con lo esperado
            expected_specialty = test_case["expected_specialty"]
            actual_specialty = analysis.get("specialty")
            
            if actual_specialty == expected_specialty:
                print(f"✅ Especialidad correcta: {actual_specialty}")
            else:
                print(f"❌ Especialidad incorrecta: esperado {expected_specialty}, obtuvo {actual_specialty}")
            
            # 5. Probar el proceso completo
            print("🔄 Probando proceso completo...")
            full_result = await coordinator.process_user_input(
                user_id="debug_user_123",
                user_input=test_case["input"]
            )
            
            print(f"🎊 Resultado final completo:")
            print(f"   - Tipo de respuesta: {full_result.get('response_type', 'N/A')}")
            print(f"   - Tipo de ruteo: {full_result.get('routing_type', 'N/A')}")
            print(f"   - Respuesta texto: {full_result.get('response', {}).get('response', 'N/A')[:100]}...")
            
        except Exception as e:
            print(f"❌ ERROR en el test: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n📈 Estadísticas de ruteo:")
    print(f"   - Rutas determinísticas: {coordinator._routing_stats['deterministic_routes']}")
    print(f"   - Rutas de IA: {coordinator._routing_stats['ai_routes']}")
    print(f"   - Escalaciones diabetes: {coordinator._routing_stats['diabetes_escalations']}")
    print(f"   - Escalaciones obesidad: {coordinator._routing_stats['obesity_escalations']}")
    print(f"   - Fallbacks agente maestro: {coordinator._routing_stats['master_agent_fallbacks']}")

if __name__ == "__main__":
    asyncio.run(test_intelligent_routing())
