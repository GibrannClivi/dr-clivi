"""
Optimized Dialogflow Pages Implementation
Modular architecture with separated concerns for better maintainability

This replaces the monolithic dialogflow_pages.py with a clean, modular structure:
- Page definitions separated by functionality
- Rendering logic isolated in PageRenderer
- Routing logic isolated in PageRouter
- Type definitions centralized in page_types
"""

import logging
from typing import Any, Dict, List, Optional

from .page_types import PageType
from .page_renderer import PageRenderer
from .page_router import PageRouter
from .main_menu_pages import (
    get_main_menu_page,
    get_end_session_page,
    get_questions_tags_page,
    get_send_question_page
)
from .appointment_pages import (
    get_appointments_menu_page,
    get_appointments_list_page,
    get_appointments_view_page,
    get_appointment_schedule_page,
    get_appointment_confirm_page,
    get_appointment_reschedule_page,
    get_appointment_cancel_page
)
from .measurement_pages import (
    get_measurements_menu_page,
    get_measurements_reports_page,
    get_log_weight_page,
    get_glucose_fasting_page,
    get_glucose_post_meal_page,
    get_log_hip_page,
    get_log_waist_page,
    get_log_neck_page
)
from .admin_pages import (
    get_invoice_labs_menu_page,
    get_invoice_updated_info_page,
    get_last_file_available_page,
    get_meds_supplies_status_page
)

logger = logging.getLogger(__name__)


class DialogflowPageManager:
    """
    Optimized and modular page manager for Dialogflow CX integration
    
    Features:
    - Modular page definitions by functionality
    - Separated rendering and routing logic
    - Better error handling and validation
    - Easier maintenance and testing
    """
    
    def __init__(self, config=None):
        self.config = config
        self.renderer = PageRenderer()
        self.router = PageRouter()
        self.pages = self._load_all_pages()
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Validate all pages on initialization
        self._validate_all_pages()
    
    def _load_all_pages(self) -> Dict[str, Dict[str, Any]]:
        """
        Load all page definitions from modular functions
        This replaces the massive inline dictionary with clean function calls
        """
        pages = {}
        
        # Main menu pages
        pages["mainMenu"] = get_main_menu_page()
        pages["endSession"] = get_end_session_page()
        pages["questionsTags"] = get_questions_tags_page()
        pages["sendQuestion"] = get_send_question_page()
        
        # Appointment pages
        pages["apptsMenu"] = get_appointments_menu_page()
        pages["appointmentsList"] = get_appointments_list_page()
        pages["appointmentsView"] = get_appointments_view_page()
        pages["appointmentSchedule"] = get_appointment_schedule_page()
        pages["appointmentConfirm"] = get_appointment_confirm_page()
        pages["appointmentReschedule"] = get_appointment_reschedule_page()
        pages["appointmentCancel"] = get_appointment_cancel_page()
        
        # Measurement pages
        pages["measurementsMenu"] = get_measurements_menu_page()
        pages["measurementsReports"] = get_measurements_reports_page()
        pages["logWeight"] = get_log_weight_page()
        pages["glucoseValueLogFasting"] = get_glucose_fasting_page()
        pages["glucoseValueLogPostMeal"] = get_glucose_post_meal_page()
        pages["logHip"] = get_log_hip_page()
        pages["logWaist"] = get_log_waist_page()
        pages["logNeck"] = get_log_neck_page()
        
        # Administrative pages
        pages["invoiceLabsMenu"] = get_invoice_labs_menu_page()
        pages["invoiceUpdatedInfo"] = get_invoice_updated_info_page()
        pages["lastFileAvailable"] = get_last_file_available_page()
        pages["medsSuppliesStatus"] = get_meds_supplies_status_page()
        
        return pages
    
    def _validate_all_pages(self):
        """Validate all page definitions"""
        invalid_pages = []
        
        for page_name, page_def in self.pages.items():
            if not self.router.validate_page_definition(page_name, page_def):
                invalid_pages.append(page_name)
        
        if invalid_pages:
            self.logger.error(f"Invalid page definitions found: {invalid_pages}")
        else:
            self.logger.info(f"All {len(self.pages)} pages validated successfully")
    
    def render_page(self, page_name: str, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Render a page with user context
        Delegates to PageRenderer for clean separation of concerns
        """
        if page_name not in self.pages:
            self.logger.error(f"Page not found: {page_name}")
            return self.renderer._render_fallback_page(user_context)
        
        page_def = self.pages[page_name]
        return self.renderer.render_page(page_name, page_def, user_context)
    
    def handle_page_selection(self, page_name: str, selection_id: str, 
                            user_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle user selection within a page
        Delegates to PageRouter for clean separation of concerns
        """
        if page_name not in self.pages:
            self.logger.error(f"Page not found for selection: {page_name}")
            return {
                "action": "trigger_intelligent_routing",
                "reason": "page_not_found",
                "page": page_name
            }
        
        page_def = self.pages[page_name]
        return self.router.handle_page_selection(page_name, page_def, selection_id, user_context)
    
    def get_page_transitions(self, page_name: str) -> Dict[str, Any]:
        """Get transition routes for a page"""
        if page_name not in self.pages:
            return {}
        
        return self.router.get_page_transitions(self.pages[page_name])
    
    def list_available_pages(self) -> List[str]:
        """Get list of all available page names"""
        return list(self.pages.keys())
    
    def get_page_info(self, page_name: str) -> Optional[Dict[str, Any]]:
        """Get complete information about a page"""
        if page_name not in self.pages:
            return None
        
        page_def = self.pages[page_name]
        return {
            "name": page_name,
            "display_name": page_def.get("display_name"),
            "message_type": page_def.get("entry_fulfillment", {}).get("message_type"),
            "has_transitions": bool(page_def.get("transition_routes")),
            "transition_count": len(page_def.get("transition_routes", {}))
        }


# Backward compatibility - maintain the same interface as the original file
class DialogflowPageImplementor(DialogflowPageManager):
    """
    Backward compatibility class
    Maintains the same interface as the original DialogflowPageImplementor
    """
    
    def __init__(self, config=None):
        super().__init__(config)
        # For backward compatibility, expose pages directly
        self.pages = self.pages


# Create default instance for easy importing
default_page_manager = DialogflowPageManager()

# Convenience functions for backward compatibility
def render_page(page_name: str, user_context: Dict[str, Any]) -> Dict[str, Any]:
    """Convenience function for rendering pages"""
    return default_page_manager.render_page(page_name, user_context)


def handle_page_selection(page_name: str, selection_id: str, 
                        user_context: Dict[str, Any]) -> Dict[str, Any]:
    """Convenience function for handling page selections"""
    return default_page_manager.handle_page_selection(page_name, selection_id, user_context)
