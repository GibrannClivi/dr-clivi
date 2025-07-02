"""
Definiciones de tipos y enums para las páginas de Dialogflow
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


class MessageType(Enum):
    """Tipos de mensaje soportados"""
    INTERACTIVE_LIST = "interactive_list"
    BUTTON_MENU = "button_menu"
    TEXT = "text"


class ResponseType(Enum):
    """Tipos de respuesta del sistema"""
    WHATSAPP_MENU = "whatsapp_menu"
    PAGE_NAVIGATION = "page_navigation"
    GENERAL_RESPONSE = "general_response"
    ERROR_FALLBACK = "error_fallback"
