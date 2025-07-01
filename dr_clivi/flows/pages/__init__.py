"""
Dialogflow Pages Module - Initialization
Centralizes access to all page definitions following modular architecture
"""

from .page_types import PageType, MessageType, ResponseType, RoutingType
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

__all__ = [
    # Types
    "PageType",
    "MessageType", 
    "ResponseType",
    "RoutingType",
    
    # Main Menu Pages
    "get_main_menu_page",
    "get_end_session_page",
    "get_questions_tags_page",
    "get_send_question_page",
    
    # Appointment Pages
    "get_appointments_menu_page",
    "get_appointments_list_page",
    "get_appointments_view_page",
    "get_appointment_schedule_page",
    "get_appointment_confirm_page",
    "get_appointment_reschedule_page",
    "get_appointment_cancel_page",
    
    # Measurement Pages
    "get_measurements_menu_page",
    "get_measurements_reports_page",
    "get_log_weight_page",
    "get_glucose_fasting_page",
    "get_glucose_post_meal_page",
    "get_log_hip_page",
    "get_log_waist_page",
    "get_log_neck_page",
    
    # Admin Pages
    "get_invoice_labs_menu_page",
    "get_invoice_updated_info_page",
    "get_last_file_available_page",
    "get_meds_supplies_status_page",
]
