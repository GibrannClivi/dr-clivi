"""
Page Type Definitions for Dialogflow CX Pages
"""

from enum import Enum


class PageType(Enum):
    """Tipos de página según Dialogflow CX"""
    MAIN_MENU = "mainMenu"
    APPTS_MENU = "apptsMenu"
    MEASUREMENTS_MENU = "measurementsMenu"
    MEASUREMENTS_REPORTS = "measurementsReports"
    INVOICE_LABS_MENU = "invoiceLabsMenu"
    INVOICE_UPDATED_INFO = "invoiceUpdatedInfo"
    LAST_FILE_AVAILABLE = "lastFileAvailable"
    MEDS_SUPPLIES_STATUS = "medsSuppliesStatus"
    QUESTIONS_TAGS = "questionsTags"
    END_SESSION = "endSession"
    
    # Páginas de citas
    APPOINTMENTS_LIST = "appointmentsList"
    APPOINTMENTS_VIEW = "appointmentsView"
    APPOINTMENT_SCHEDULE = "appointmentSchedule"
    APPOINTMENT_CONFIRM = "appointmentConfirm"
    APPOINTMENT_RESCHEDULE = "appointmentReschedule"
    APPOINTMENT_CANCEL = "appointmentCancel"
    
    # Páginas de mediciones
    LOG_WEIGHT = "logWeight"
    GLUCOSE_VALUE_LOG_FASTING = "glucoseValueLogFasting"
    GLUCOSE_VALUE_LOG_POST_MEAL = "glucoseValueLogPostMeal"
    LOG_HIP = "logHip"
    LOG_WAIST = "logWaist"
    LOG_NECK = "logNeck"
    
    # Página de preguntas
    SEND_QUESTION = "sendQuestion"


class MessageType(Enum):
    """Tipos de mensaje según Dialogflow CX"""
    INTERACTIVE_LIST = "interactive_list"
    BUTTON_MENU = "button_menu"
    TEXT = "text"
    BUTTONS = "buttons"


class ResponseType(Enum):
    """Tipos de respuesta para el renderizado"""
    WHATSAPP_MENU = "whatsapp_menu"
    PAGE_NAVIGATION = "page_navigation"
    GENERAL_RESPONSE = "general_response"


class RoutingType(Enum):
    """Tipos de routing para las páginas"""
    DETERMINISTIC = "deterministic"
    ERROR_FALLBACK = "error_fallback"
    INTELLIGENT_ROUTING = "intelligent_routing"
