"""
Deterministic Flow Handler - Exact implementation of Clivi's original flows
Handles structured WhatsApp menu interactions without AI interpretation.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass
from datetime import datetime

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
    
    def __init__(self):
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
        Generate WhatsApp interactive menu based on mainMenu.json structure.
        Returns exact format for WhatsApp Business API.
        """
        sections = [{
            "title": "Menú:",
            "rows": []
        }]
        
        for option_id, option_data in self.menu_options.items():
            sections[0]["rows"].append({
                "id": option_id,
                "title": option_data["title"],
                "description": option_data["description"]
            })
        
        return {
            "type": "interactive",
            "interactive": {
                "type": "list", 
                "header": {
                    "type": "text",
                    "text": "Dr. Clivi"
                },
                "body": {
                    "text": f"Hola {user_context.patient_name}, por favor utiliza el menú de opciones."
                },
                "action": {
                    "button": "Seleccionar opción",
                    "sections": sections
                }
            }
        }
    
    def is_deterministic_input(self, user_input: str) -> bool:
        """
        Check if user input matches deterministic flow patterns.
        Returns True if it should be handled by flows, False if needs AI routing.
        """
        # Check for main menu trigger keywords (from keyWordMainMenu intent)
        main_menu_triggers = [
            "hola", "menu", "inicio", "clivi", "dr clivi", 
            "opciones", "ayuda", "start", "comenzar"
        ]
        
        # Check for menu option selections
        menu_option_patterns = list(self.menu_options.keys())
        
        # Check for button/menu selection patterns
        user_lower = user_input.lower().strip()
        
        if any(trigger in user_lower for trigger in main_menu_triggers):
            return True
            
        if any(option.lower() in user_lower for option in menu_option_patterns):
            return True
            
        # Check for specific deterministic patterns
        deterministic_patterns = [
            "citas", "mediciones", "reporte", "facturas", "envios", 
            "pregunta", "queja", "no necesario", "estudios"
        ]
        
        if any(pattern in user_lower for pattern in deterministic_patterns):
            return True
            
        return False
    
    def route_deterministic_input(self, user_context: UserContext, 
                                user_input: str) -> Dict[str, Any]:
        """
        Route deterministic input through the proper flow logic.
        """
        user_lower = user_input.lower().strip()
        
        # Main menu triggers
        main_menu_triggers = [
            "hola", "menu", "inicio", "clivi", "dr clivi", 
            "opciones", "ayuda", "start", "comenzar"
        ]
        
        if any(trigger in user_lower for trigger in main_menu_triggers):
            # Trigger keyWordMainMenu intent → checkPlanStatus flow
            plan_result = self.check_plan_status(user_context)
            
            if plan_result.get("action") == "show_main_menu":
                return {
                    "action": "show_main_menu",
                    "menu_data": self.generate_main_menu_whatsapp(user_context),
                    "flow": "diabetesPlans",
                    "page": "mainMenu"
                }
            else:
                return plan_result
        
        # Try to match menu option selection
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
