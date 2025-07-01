#!/usr/bin/env python3
"""
Prueba específica de flujos determinísticos de Dialogflow CX
Verifica que cada paso siga exactamente la implementación original
"""

import asyncio
import json
import logging
import sys
import os
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dr_clivi.config import Config
from dr_clivi.flows.deterministic_handler import DeterministicFlowHandler, UserContext, PlanType, PlanStatus
from dr_clivi.flows.dialogflow_pages import DialogflowPageImplementor

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DialogflowFlowTester:
    """Tester específico para verificar flujos de Dialogflow CX"""
    
    def __init__(self):
        self.config = Config()
        self.flow_handler = DeterministicFlowHandler(self.config)
        self.page_implementor = DialogflowPageImplementor(self.config)
        
        # Usuario de prueba con plan PRO ACTIVE (debe mostrar mainMenu)
        self.test_user = UserContext(
            user_id="test_user_123",
            patient_name="Juan Pérez",
            plan=PlanType.PRO,
            plan_status=PlanStatus.ACTIVE,
            phone_number="+52123456789",
            current_flow="Default Start Flow"
        )
    
    def test_plan_status_check(self):
        """Test 1: Verificar checkPlanStatus flow"""
        print("\n🧪 Test 1: checkPlanStatus Flow")
        print("=" * 40)
        
        result = self.flow_handler.check_plan_status(self.test_user)
        
        print(f"Plan: {self.test_user.plan.value}")
        print(f"Status: {self.test_user.plan_status.value}")
        print(f"Resultado: {result}")
        
        # Verificar que PRO + ACTIVE → diabetesPlans + mainMenu
        assert result["flow"] == "diabetesPlans"
        assert result["action"] == "show_main_menu"
        print("✅ checkPlanStatus correcto: PRO+ACTIVE → diabetesPlans+mainMenu")
    
    def test_main_menu_generation(self):
        """Test 2: Verificar generación del menú principal"""
        print("\n🧪 Test 2: Generación del Menú Principal")
        print("=" * 45)
        
        menu_response = self.flow_handler.generate_main_menu_whatsapp(self.test_user)
        
        print("Estructura del menú:")
        print(f"Response type: {menu_response.get('response_type')}")
        
        menu_data = menu_response.get("menu_data", {})
        interactive = menu_data.get("interactive", {})
        
        # Verificar estructura
        assert interactive.get("type") == "list"
        assert "Dr. Clivi" in interactive.get("header", {}).get("text", "")
        assert self.test_user.patient_name in interactive.get("body", {}).get("text", "")
        
        # Verificar opciones del menú
        sections = interactive.get("action", {}).get("sections", [])
        assert len(sections) == 1
        
        rows = sections[0].get("rows", [])
        expected_options = [
            "APPOINTMENTS", "MEASUREMENTS", "MEASUREMENTS_REPORT",
            "INVOICE_LABS", "MEDS_GLP", "QUESTION_TYPE",
            "NO_NEEDED_QUESTION_PATIENT", "PATIENT_COMPLAINT"
        ]
        
        actual_options = [row["id"] for row in rows]
        print(f"Opciones encontradas: {actual_options}")
        
        for expected in expected_options:
            assert expected in actual_options, f"Opción faltante: {expected}"
        
        print("✅ Menú principal generado correctamente con todas las opciones")
    
    def test_main_menu_selections(self):
        """Test 3: Verificar selecciones del menú principal"""
        print("\n🧪 Test 3: Selecciones del Menú Principal")
        print("=" * 43)
        
        # Test cada opción del menú principal
        test_selections = [
            ("APPOINTMENTS", "apptsMenu"),
            ("MEASUREMENTS", "measurementsMenu"),
            ("MEASUREMENTS_REPORT", "measurementsReports"),
            ("INVOICE_LABS", "invoiceLabsMenu"),
            ("MEDS_GLP", "medsSuppliesStatus"),
            ("QUESTION_TYPE", "questionsTags"),
            ("NO_NEEDED_QUESTION_PATIENT", "endSession"),
            ("PATIENT_COMPLAINT", None)  # Este va a presentComplaintTag flow
        ]
        
        for selection_id, expected_target in test_selections:
            print(f"\n  Probando selección: {selection_id}")
            
            result = self.flow_handler.handle_page_selection("mainMenu", selection_id, self.test_user)
            
            print(f"    Resultado: {result.get('action')}")
            
            if expected_target:
                assert result.get("target_page") == expected_target, f"Target incorrecto para {selection_id}"
                print(f"    ✅ Navega correctamente a: {expected_target}")
            else:
                # PATIENT_COMPLAINT debe ir a flow
                assert "target_flow" in result, f"Debería tener target_flow para {selection_id}"
                print(f"    ✅ Redirige a flow: {result.get('target_flow')}")
        
        print("\n✅ Todas las selecciones del menú principal funcionan correctamente")
    
    def test_appointments_page(self):
        """Test 4: Verificar página de citas (apptsMenu)"""
        print("\n🧪 Test 4: Página de Citas (apptsMenu)")
        print("=" * 38)
        
        # Renderizar página de citas
        page_response = self.page_implementor.render_page("apptsMenu", {
            "patient_name": self.test_user.patient_name
        })
        
        print(f"Response type: {page_response.get('response_type')}")
        
        # Verificar que es page_navigation con botones
        assert page_response.get("response_type") == "page_navigation"
        
        inline_keyboard = page_response.get("inline_keyboard", [])
        print(f"Botones encontrados: {len(inline_keyboard)} filas")
        
        # Verificar botones esperados
        expected_buttons = ["APPOINTMENTS_LIST_SEND", "APPOINTMENT_RESCHEDULER", "SEND_QUESTION"]
        
        all_buttons = []
        for row in inline_keyboard:
            for button in row:
                all_buttons.append(button["callback_data"])
        
        print(f"IDs de botones: {all_buttons}")
        
        for expected in expected_buttons:
            assert expected in all_buttons, f"Botón faltante: {expected}"
        
        print("✅ Página de citas renderizada correctamente")
    
    def test_measurements_page(self):
        """Test 5: Verificar página de mediciones (measurementsMenu)"""
        print("\n🧪 Test 5: Página de Mediciones (measurementsMenu)")
        print("=" * 48)
        
        page_response = self.page_implementor.render_page("measurementsMenu", {
            "patient_name": self.test_user.patient_name
        })
        
        # Verificar estructura
        assert page_response.get("response_type") == "page_navigation"
        
        inline_keyboard = page_response.get("inline_keyboard", [])
        
        # Verificar botones de mediciones
        expected_measurements = [
            "LOG_WEIGHT", "LOG_GLUCOSE_FASTING", "LOG_GLUCOSE_POST_MEAL",
            "LOG_HIP", "LOG_WAIST", "LOG_NECK"
        ]
        
        all_buttons = []
        for row in inline_keyboard:
            for button in row:
                all_buttons.append(button["callback_data"])
        
        print(f"Opciones de medición: {all_buttons}")
        
        for expected in expected_measurements:
            assert expected in all_buttons, f"Medición faltante: {expected}"
        
        print("✅ Página de mediciones renderizada correctamente")
    
    def test_questions_page(self):
        """Test 6: Verificar página de preguntas (questionsTags)"""
        print("\n🧪 Test 6: Página de Preguntas (questionsTags)")
        print("=" * 44)
        
        page_response = self.page_implementor.render_page("questionsTags", {
            "patient_name": self.test_user.patient_name
        })
        
        # Verificar estructura
        assert page_response.get("response_type") == "page_navigation"
        
        inline_keyboard = page_response.get("inline_keyboard", [])
        
        # Verificar categorías de preguntas
        expected_categories = [
            "DIABETES_QUESTION", "NUTRITION_QUESTION", "PSYCHOLOGY_QUESTION",
            "SUPPLIES_QUESTION", "HIGH_SPECIALIZATION_QUESTION"
        ]
        
        all_buttons = []
        for row in inline_keyboard:
            for button in row:
                all_buttons.append(button["callback_data"])
        
        print(f"Categorías de preguntas: {all_buttons}")
        
        for expected in expected_categories:
            assert expected in all_buttons, f"Categoría faltante: {expected}"
        
        print("✅ Página de preguntas renderizada correctamente")
    
    def test_callback_query_routing(self):
        """Test 7: Verificar routing de callback queries (botones presionados)"""
        print("\n🧪 Test 7: Routing de Callback Queries")
        print("=" * 39)
        
        # Test casos de callback queries como si vinieran de Telegram
        test_callbacks = [
            ("APPOINTMENTS", True, "mainMenu → apptsMenu"),
            ("LOG_GLUCOSE_FASTING", True, "measurementsMenu → glucoseValueLogFasting"),
            ("DIABETES_QUESTION", True, "questionsTags → sendQuestion"),
            ("UNKNOWN_BUTTON", False, "Debe activar intelligent routing")
        ]
        
        for callback_data, should_be_deterministic, description in test_callbacks:
            print(f"\n  Probando callback: {callback_data}")
            
            is_deterministic = self.flow_handler.is_deterministic_input(callback_data)
            
            print(f"    Es determinístico: {is_deterministic}")
            print(f"    Esperado: {should_be_deterministic}")
            print(f"    Descripción: {description}")
            
            assert is_deterministic == should_be_deterministic, f"Routing incorrecto para {callback_data}"
            
            if should_be_deterministic:
                result = self.flow_handler.route_deterministic_input(self.test_user, callback_data)
                print(f"    Resultado: {result.get('action')}")
                print(f"    ✅ Ruteado correctamente")
            else:
                print(f"    ✅ Correctamente marcado para intelligent routing")
        
        print("\n✅ Routing de callback queries funciona correctamente")
    
    def test_full_flow_simulation(self):
        """Test 8: Simulación de flujo completo"""
        print("\n🧪 Test 8: Simulación de Flujo Completo")
        print("=" * 41)
        
        print("Simulando: Usuario dice 'Hola' → Menú → Citas → Ver citas")
        
        # Paso 1: Usuario dice "Hola"
        print("\n  Paso 1: Usuario dice 'Hola'")
        result1 = self.flow_handler.route_deterministic_input(self.test_user, "Hola")
        
        assert result1.get("action") == "show_main_menu"
        assert result1.get("response_type") == "whatsapp_menu"
        print("    ✅ Muestra menú principal")
        
        # Paso 2: Usuario selecciona "APPOINTMENTS"
        print("\n  Paso 2: Usuario selecciona 'APPOINTMENTS'")
        result2 = self.flow_handler.route_deterministic_input(self.test_user, "APPOINTMENTS")
        
        print(f"    Resultado real: {result2}")
        assert result2.get("action") == "navigate_to_page"
        assert result2.get("target_page") == "apptsMenu"
        print("    ✅ Navega a página de citas")
        
        # Paso 3: Usuario selecciona "APPOINTMENTS_LIST_SEND" 
        print("\n  Paso 3: Usuario selecciona 'APPOINTMENTS_LIST_SEND'")
        result3 = self.flow_handler.route_deterministic_input(self.test_user, "APPOINTMENTS_LIST_SEND")
        
        print(f"    Resultado real: {result3}")
        assert result3.get("action") == "navigate_to_page"
        assert result3.get("target_page") == "End Session"
        print("    ✅ Ejecuta función y termina sesión")
        
        print("\n✅ Flujo completo simulado correctamente")
    
    def run_all_tests(self):
        """Ejecutar todos los tests de verificación"""
        print("🔬 VERIFICACIÓN DE FLUJOS DETERMINÍSTICOS DE DIALOGFLOW CX")
        print("=" * 65)
        
        tests = [
            self.test_plan_status_check,
            self.test_main_menu_generation,
            self.test_main_menu_selections,
            self.test_appointments_page,
            self.test_measurements_page,
            self.test_questions_page,
            self.test_callback_query_routing,
            self.test_full_flow_simulation
        ]
        
        passed = 0
        total = len(tests)
        
        for test_func in tests:
            try:
                test_func()
                passed += 1
            except Exception as e:
                print(f"\n❌ Test {test_func.__name__} FALLÓ: {e}")
                import traceback
                traceback.print_exc()
        
        print(f"\n📊 RESULTADOS FINALES")
        print("=" * 22)
        print(f"✅ Tests pasados: {passed}/{total}")
        
        if passed == total:
            print("🎉 TODOS LOS FLUJOS DETERMINÍSTICOS FUNCIONAN CORRECTAMENTE")
            print("   Los flujos siguen fielmente la implementación de Dialogflow CX")
            print("   ✓ checkPlanStatus flow")
            print("   ✓ diabetesPlans flow")
            print("   ✓ mainMenu page")
            print("   ✓ apptsMenu page")
            print("   ✓ measurementsMenu page")
            print("   ✓ questionsTags page")
            print("   ✓ Callback query routing")
            print("   ✓ Navegación entre páginas")
        else:
            print("⚠️  ALGUNOS TESTS FALLARON")
            print("   Revisar la implementación antes de continuar")
        
        return passed == total


if __name__ == "__main__":
    print("🧪 Dr. Clivi - Verificación de Flujos Determinísticos")
    print("Comparando implementación actual vs Dialogflow CX original")
    print("=" * 70)
    
    tester = DialogflowFlowTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🚀 LISTO PARA PRUEBAS CON TELEGRAM EN VIVO")
        print("   Los flujos determinísticos están correctos")
        print("   Proceder con configuración de webhook")
    else:
        print("\n🔧 REQUIERE AJUSTES ANTES DE CONTINUAR")
        print("   Corregir flujos determinísticos primero")
    
    sys.exit(0 if success else 1)
