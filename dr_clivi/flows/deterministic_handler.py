"""
Deterministic Flow Handler - Exact implementation of Clivi's original flows
Handles structured WhatsApp menu interactions without AI interpretation.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass
from datetime import datetime

from .dialogflow_pages import DialogflowPageImplementor

logger = logging.getLogger(__name__)


class PlanType(Enum):
    """Plan types from checkPlanStatus analysis"""
    PRO = "PRO"
    PLUS = "PLUS" 
    CLUB = "CLUB"
    BASIC = "BASIC"


class PlanStatus(Enum):
    """Plan statuses from checkPlanStatus analysis"""
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    CANCELED = "CANCELED"


class MenuOption(Enum):
    """Main menu options from mainMenu.json analysis"""
    APPOINTMENTS = "APPOINTMENTS"
    MEASUREMENTS = "MEASUREMENTS"
    MEASUREMENTS_REPORT = "MEASUREMENTS_REPORT"
    INVOICE_LABS = "INVOICE_LABS"
    MEDS_GLP = "MEDS_GLP"
    QUESTION_TYPE = "QUESTION_TYPE"
    NO_NEEDED_QUESTION_PATIENT = "NO_NEEDED_QUESTION_PATIENT"
    PATIENT_COMPLAINT = "PATIENT_COMPLAINT"


@dataclass
class UserContext:
    """User context from session parameters"""
    user_id: str
    patient_name: str
    plan: PlanType
    plan_status: PlanStatus
    phone_number: str
    current_flow: str = "Default Start Flow"
    current_page: str = None
    session_data: Dict[str, Any] = None


class DeterministicFlowHandler:
    """
    Handles the exact deterministic flows from the original Clivi system.
    No AI interpretation - pure button/menu logic.
    """
    
    def __init__(self, config=None):
        self.config = config  # Optional config for future use
        self.page_implementor = DialogflowPageImplementor(config)
        self.menu_options = self._load_menu_structure()
    
    def _load_menu_structure(self) -> Dict[str, Dict[str, Any]]:
        """Load the exact menu structure from mainMenu.json analysis"""
        return {
            "APPOINTMENTS": {
                "title": "Citas",
                "description": "Agenda/Re-agendamiento 🗓️",
                "target_page": "apptsMenu",
                "icon": "🗓️"
            },
            "MEASUREMENTS": {
                "title": "Mediciones", 
                "description": "Enviar mediciones 📏",
                "target_page": "measurementsMenu",
                "icon": "📏"
            },
            "MEASUREMENTS_REPORT": {
                "title": "Reporte mediciones",
                "description": "Reporte de mediciones 📈", 
                "target_page": "measurementsReports",
                "icon": "📈"
            },
            "INVOICE_LABS": {
                "title": "Facturas y estudios",
                "description": "Facturación, estudios y órdenes📂",
                "target_page": "invoiceLabsMenu", 
                "icon": "📂"
            },
            "MEDS_GLP": {
                "title": "Estatus de envíos",
                "description": "Meds/Glucómetro/Tiras📦",
                "target_page": "medsSuppliesStatus",
                "icon": "📦"
            },
            "QUESTION_TYPE": {
                "title": "Enviar pregunta",
                "description": "Enviar pregunta a agente/especialista ❔",
                "target_page": "questionsTags",
                "icon": "❔"
            },
            "NO_NEEDED_QUESTION_PATIENT": {
                "title": "No es necesario", 
                "description": "No requiero apoyo 👍",
                "target_page": "endSession",
                "icon": "👍"
            },
            "PATIENT_COMPLAINT": {
                "title": "Presentar queja",
                "description": "Enviar queja sobre el servicio 📣",
                "target_flow": "presentComplaintTag",
                "icon": "📣"
            }
        }
    
    def check_plan_status(self, user_context: UserContext) -> Dict[str, Any]:
        """
        Exact implementation of checkPlanStatus flow logic.
        Routes based on plan type and status combinations.
        """
        plan = user_context.plan
        status = user_context.plan_status
        
        # CLUB plan with CANCELED status
        if plan == PlanType.CLUB and status == PlanStatus.CANCELED:
            return {
                "flow": "checkPlanStatus",
                "target_page": "clubCanceledPlan",
                "action": "redirect_to_reactivation"
            }
        
        # CLUB plan with ACTIVE/SUSPENDED status  
        if plan == PlanType.CLUB and status in [PlanStatus.ACTIVE, PlanStatus.SUSPENDED]:
            return {
                "flow": "clubPlan",
                "action": "log_session_start",
                "event_type": "STARTED_SESSION_DATE"
            }
        
        # PRO/PLUS/BASIC plans with ACTIVE/SUSPENDED status
        if plan in [PlanType.PRO, PlanType.PLUS, PlanType.BASIC] and status in [PlanStatus.ACTIVE, PlanStatus.SUSPENDED]:
            return {
                "flow": "diabetesPlans", 
                "target_page": "mainMenu",
                "action": "show_main_menu"
            }
        
        # Unknown user context
        return {
            "flow": "checkPlanStatus",
            "target_page": "userProblems", 
            "action": "collect_user_data"
        }
    
    def handle_main_menu_selection(self, user_context: UserContext, 
                                 selected_option: str) -> Dict[str, Any]:
        """
        Handle main menu option selection.
        Returns deterministic routing based on mainMenu.json structure.
        """
        if selected_option not in self.menu_options:
            # This should trigger intelligent routing
            return {
                "action": "trigger_intelligent_routing",
                "reason": "unknown_option",
                "user_input": selected_option
            }
        
        option_config = self.menu_options[selected_option]
        
        # Log button click event (from original flow)
        log_event = {
            "function_name": "ACTIVITY_EVENT_LOG",
            "params": {
                "eventType": "CLICKED_BUTTON_MAIN_MENU"
            }
        }
        
        result = {
            "action": "navigate_to_page",
            "selected_option": selected_option,
            "option_config": option_config,
            "log_event": log_event
        }
        
        # Add target routing
        if "target_page" in option_config:
            result["target_page"] = option_config["target_page"]
        elif "target_flow" in option_config:
            result["target_flow"] = option_config["target_flow"]
        
        return result
    
    def generate_main_menu_whatsapp(self, user_context: UserContext) -> Dict[str, Any]:
        """
        Generate WhatsApp interactive menu usando la implementación exacta de Dialogflow.
        """
        return self.page_implementor.render_page("mainMenu", {
            "patient_name": user_context.patient_name
        })
    
    def handle_page_selection(self, current_page: str, selection_id: str, 
                            user_context: UserContext) -> Dict[str, Any]:
        """
        Maneja selección en una página específica siguiendo las transiciones de Dialogflow
        """
        return self.page_implementor.handle_page_selection(
            current_page, selection_id, {
                "patient_name": user_context.patient_name,
                "user_id": user_context.user_id,
                "plan": user_context.plan.value if user_context.plan else None,
                "plan_status": user_context.plan_status.value if user_context.plan_status else None
            }
        )
    
    def render_page(self, page_name: str, user_context: UserContext) -> Dict[str, Any]:
        """
        Renderiza una página específica
        """
        return self.page_implementor.render_page(page_name, {
            "patient_name": user_context.patient_name,
            "user_id": user_context.user_id,
            "plan": user_context.plan.value if user_context.plan else None,
            "plan_status": user_context.plan_status.value if user_context.plan_status else None
        })
    
    def is_deterministic_input(self, user_input: str, session_context: Dict[str, Any] = None) -> bool:
        """
        Check if user input matches deterministic flow patterns.
        Returns True if it should be handled by flows, False if needs AI routing.
        
        Solo debe considerar determinístico:
        1. Saludos básicos e inicios de conversación
        2. Selecciones exactas de menú (callback IDs)
        3. Palabras clave muy específicas para navegación de menú
        4. Números simples en contexto de medición
        
        Todo lo demás debe ir a routing inteligente.
        """
        # Limpiar input
        user_input = user_input.strip()
        user_upper = user_input.upper()
        user_lower = user_input.lower()
        
        # 1. Callback queries exactos (botones presionados)
        exact_button_ids = [
            "APPOINTMENTS", "MEASUREMENTS", "MEASUREMENTS_REPORT", "INVOICE_LABS",
            "MEDS_GLP", "QUESTION_TYPE", "NO_NEEDED_QUESTION_PATIENT", "PATIENT_COMPLAINT",
            "APPOINTMENTS_LIST_SEND", "APPOINTMENT_RESCHEDULER", "SEND_QUESTION",
            "LOG_WEIGHT", "LOG_GLUCOSE_FASTING", "LOG_GLUCOSE_POST_MEAL",
            "LOG_HIP", "LOG_WAIST", "LOG_NECK",
            "DIABETES_QUESTION", "NUTRITION_QUESTION", "PSYCHOLOGY_QUESTION",
            "SUPPLIES_QUESTION", "HIGH_SPECIALIZATION_QUESTION",
            "INVOICE", "UPLOAD_LABS", "CALL_SUPPORT", "PX_QUESTION_TAG",
            "FULL_REPORT", "GLUCOSE_REPORT",
            # Acciones específicas de citas y mediciones
            "SCHEDULE_NEW_APPOINTMENT", "RESCHEDULE_APPOINTMENT", "CANCEL_APPOINTMENT",
            "BACK_TO_MAIN_MENU", "MAIN_MENU", "HOME", "MENU_PRINCIPAL",
            # Estados de input para mediciones
            "WAITING_FOR_WEIGHT", "WAITING_FOR_GLUCOSE", "WEIGHT_LOGGED", "GLUCOSE_LOGGED",
            # Navegación
            "VOLVER", "REGRESAR", "ATRAS", "MENU", "TERMINAR", "SALIR"
        ]
        
        if user_upper in exact_button_ids:
            return True
        
        # 2. Contexto de medición: números simples cuando el usuario está registrando mediciones
        if session_context:
            current_flow = session_context.get("current_flow", "")
            current_page = session_context.get("current_page", "")
            awaiting_input = session_context.get("awaiting_input", "")
            
            # Si estamos esperando una medición específica, los números son determinísticos
            measurement_contexts = [
                "measurementsMenu", "LOG_WEIGHT", "LOG_GLUCOSE_FASTING", "LOG_GLUCOSE_POST_MEAL",
                "WAITING_FOR_WEIGHT", "WAITING_FOR_GLUCOSE", "weight_input", "glucose_input"
            ]
            
            if (current_page in measurement_contexts or 
                awaiting_input in measurement_contexts or 
                current_flow in measurement_contexts):
                
                # Verificar si es un número válido para medición
                if self._is_valid_measurement_number(user_input):
                    return True
        
        # 3. Frases de navegación comunes
        navigation_phrases = [
            "volver al menu", "menu principal", "regresar", "terminar",
            "atras", "volver", "menu", "salir", "inicio", "home"
        ]
        
        if any(phrase in user_lower for phrase in navigation_phrases):
            return True
        
        # 4. Saludos básicos muy específicos (solo para mostrar menú principal)
        basic_greetings = [
            "hola", "inicio", "menu", "menú", "opciones", 
            "start", "comenzar", "hola doctor", "dr clivi"
        ]
        
        # Debe ser coincidencia exacta o muy cercana para saludos
        if user_lower in basic_greetings:
            return True
            
        # Si contiene saludo pero también contenido médico, va a IA
        medical_keywords = [
            "glucosa", "diabetes", "peso", "dolor", "medicamento", 
            "metformina", "ozempic", "insulina", "presión", "mg/dl",
            "ayuda", "problema", "síntoma", "tratamiento", "plan"
        ]
        
        if any(greeting in user_lower for greeting in basic_greetings):
            if any(medical in user_lower for medical in medical_keywords):
                return False  # Tiene saludo + contenido médico -> IA
        
        # 5. Todo lo demás va a routing inteligente
        # Incluyendo consultas médicas, preguntas específicas, emergencias, etc.
        return False
    
    def _is_valid_measurement_number(self, user_input: str) -> bool:
        """
        Verifica si un input es un número válido para mediciones.
        Rangos típicos:
        - Peso: 30-300 kg
        - Glucosa: 50-400 mg/dL
        - Medidas corporales: 20-200 cm
        """
        try:
            # Limpiar input (remover unidades comunes)
            cleaned = user_input.lower().replace("kg", "").replace("cm", "").replace("mg/dl", "").replace("mg", "").strip()
            
            # Verificar si es un número
            if "." in cleaned:
                number = float(cleaned)
            else:
                number = int(cleaned)
            
            # Rangos razonables para mediciones corporales
            if 10 <= number <= 500:  # Rango amplio para diferentes tipos de medición
                return True
                
        except (ValueError, TypeError):
            pass
            
        return False
    
    def route_deterministic_input(self, user_context: UserContext, 
                                user_input: str, session_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Route deterministic input through the proper flow logic.
        """
        user_lower = user_input.lower().strip()
        user_upper = user_input.upper().strip()
        
        # 1. Manejar entrada de mediciones en contexto PRIMERO (antes de navegación)
        if session_context:
            current_page = session_context.get("current_page", "")
            awaiting_input = session_context.get("awaiting_input", "")
            
            # Si estamos esperando una medición y recibimos un número válido
            if self._is_valid_measurement_number(user_input):
                measurement_contexts = [
                    "measurementsMenu", "LOG_WEIGHT", "LOG_GLUCOSE_FASTING", "LOG_GLUCOSE_POST_MEAL",
                    "WAITING_FOR_WEIGHT", "WAITING_FOR_GLUCOSE", "weight_input", "glucose_input"
                ]
                
                if (current_page in measurement_contexts or 
                    awaiting_input in measurement_contexts):
                    
                    return self._handle_measurement_input(user_context, user_input, session_context)
        
        # 2. Manejar navegación explícita
        navigation_triggers = [
            "volver al menu", "menu principal", "regresar", "terminar",
            "atras", "volver", "menu", "salir", "inicio", "home",
            "BACK_TO_MAIN_MENU", "MAIN_MENU", "HOME", "MENU_PRINCIPAL"
        ]
        
        if any(trigger in user_lower for trigger in navigation_triggers) or user_upper in navigation_triggers:
            # Trigger main menu
            plan_result = self.check_plan_status(user_context)
            
            if plan_result.get("action") == "show_main_menu":
                menu_response = self.generate_main_menu_whatsapp(user_context)
                return {
                    "action": "show_main_menu",
                    "menu_data": menu_response.get("menu_data", {}),
                    "response_type": menu_response.get("response_type", "whatsapp_menu"),
                    "flow": "diabetesPlans",
                    "page": "mainMenu",
                    "routing_type": "deterministic"
                }
        
        # 3. Main menu triggers
        main_menu_triggers = [
            "hola", "menu", "inicio", "clivi", "dr clivi", 
            "opciones", "ayuda", "start", "comenzar"
        ]
        
        if any(trigger in user_lower for trigger in main_menu_triggers):
            # Trigger keyWordMainMenu intent → checkPlanStatus flow
            plan_result = self.check_plan_status(user_context)
            
            if plan_result.get("action") == "show_main_menu":
                menu_response = self.generate_main_menu_whatsapp(user_context)
                return {
                    "action": "show_main_menu",
                    "menu_data": menu_response.get("menu_data", {}),
                    "response_type": menu_response.get("response_type", "whatsapp_menu"),
                    "flow": "diabetesPlans",
                    "page": "mainMenu",
                    "routing_type": "deterministic"
                }
            else:
                return plan_result
        
        # 4. Check for exact button ID matches (callback queries from Telegram)
        button_mappings = {
            # Main menu buttons
            "APPOINTMENTS": ("mainMenu", "APPOINTMENTS"),
            "MEASUREMENTS": ("mainMenu", "MEASUREMENTS"),
            "MEASUREMENTS_REPORT": ("mainMenu", "MEASUREMENTS_REPORT"),
            "INVOICE_LABS": ("mainMenu", "INVOICE_LABS"),
            "MEDS_GLP": ("mainMenu", "MEDS_GLP"),
            "QUESTION_TYPE": ("mainMenu", "QUESTION_TYPE"),
            "NO_NEEDED_QUESTION_PATIENT": ("mainMenu", "NO_NEEDED_QUESTION_PATIENT"),
            "PATIENT_COMPLAINT": ("mainMenu", "PATIENT_COMPLAINT"),
            
            # Appointments menu buttons
            "APPOINTMENTS_LIST_SEND": ("apptsMenu", "APPOINTMENTS_LIST_SEND"),
            "APPOINTMENT_RESCHEDULER": ("apptsMenu", "APPOINTMENT_RESCHEDULER"),
            "SEND_QUESTION": ("apptsMenu", "SEND_QUESTION"),
            
            # Measurements menu buttons
            "LOG_WEIGHT": ("measurementsMenu", "LOG_WEIGHT"),
            "LOG_GLUCOSE_FASTING": ("measurementsMenu", "LOG_GLUCOSE_FASTING"),
            "LOG_GLUCOSE_POST_MEAL": ("measurementsMenu", "LOG_GLUCOSE_POST_MEAL"),
            "LOG_HIP": ("measurementsMenu", "LOG_HIP"),
            "LOG_WAIST": ("measurementsMenu", "LOG_WAIST"),
            "LOG_NECK": ("measurementsMenu", "LOG_NECK"),
            
            # Questions menu buttons
            "DIABETES_QUESTION": ("questionsTags", "DIABETES_QUESTION"),
            "NUTRITION_QUESTION": ("questionsTags", "NUTRITION_QUESTION"),
            "PSYCHOLOGY_QUESTION": ("questionsTags", "PSYCHOLOGY_QUESTION"),
            "SUPPLIES_QUESTION": ("questionsTags", "SUPPLIES_QUESTION"),
            "HIGH_SPECIALIZATION_QUESTION": ("questionsTags", "HIGH_SPECIALIZATION_QUESTION")
        }
        
        if user_upper in button_mappings:
            page_name, selection_id = button_mappings[user_upper]
            result = self.handle_page_selection(page_name, selection_id, user_context)
            
            # Si es una acción de medición, agregar contexto para esperar entrada
            if selection_id.startswith("LOG_"):
                result["awaiting_measurement"] = selection_id
                result["awaiting_input"] = selection_id
                
            return result
        
        # 5. Try to match menu option selection by text content
        for option_id, option_data in self.menu_options.items():
            if (option_data["title"].lower() in user_lower or 
                any(word in user_lower for word in option_data["description"].lower().split())):
                return self.handle_main_menu_selection(user_context, option_id)
        
        # If we get here, it's ambiguous - trigger intelligent routing
        return {
            "action": "trigger_intelligent_routing",
            "reason": "ambiguous_deterministic_input",
            "user_input": user_input
        }
    
    def _handle_measurement_input(self, user_context: UserContext, user_input: str, 
                                session_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Maneja la entrada de mediciones cuando el usuario está en contexto de registro.
        """
        try:
            # Limpiar y validar el número
            cleaned_input = user_input.lower().replace("kg", "").replace("cm", "").replace("mg/dl", "").replace("mg", "").strip()
            
            if "." in cleaned_input:
                value = float(cleaned_input)
            else:
                value = int(cleaned_input)
            
            measurement_type = session_context.get("awaiting_input", "").replace("LOG_", "").lower()
            
            # Determinar el tipo de medición y mensaje de confirmación
            if "weight" in measurement_type:
                unit = "kg"
                message = f"✅ **Peso registrado exitosamente**\n\n📏 **{value} {unit}** ha sido guardado en tu historial.\n\n¿Deseas registrar otra medición o volver al menú principal?"
            elif "glucose" in measurement_type:
                unit = "mg/dL"
                message = f"✅ **Glucosa registrada exitosamente**\n\n🩸 **{value} {unit}** ha sido guardado en tu historial.\n\n¿Deseas registrar otra medición o volver al menú principal?"
            else:
                unit = "cm"
                message = f"✅ **Medición registrada exitosamente**\n\n📏 **{value} {unit}** ha sido guardado en tu historial.\n\n¿Deseas registrar otra medición o volver al menú principal?"
            
            # Crear botones de navegación post-registro
            inline_keyboard = [
                [{"text": "📏 Otra medición", "callback_data": "MEASUREMENTS"}],
                [{"text": "🏠 Menú principal", "callback_data": "BACK_TO_MAIN_MENU"}]
            ]
            
            return {
                "action": "measurement_recorded",
                "response_type": "page_navigation",
                "body_text": message,
                "inline_keyboard": inline_keyboard,
                "measurement_type": measurement_type,
                "value": value,
                "unit": unit,
                "routing_type": "deterministic"
            }
            
        except (ValueError, TypeError) as e:
            return {
                "action": "invalid_measurement",
                "response_type": "general_response",
                "response": f"❌ No pude interpretar la medición '{user_input}'. Por favor ingresa solo el número (ejemplo: 75, 120, 85.5)",
                "routing_type": "deterministic"
            }
