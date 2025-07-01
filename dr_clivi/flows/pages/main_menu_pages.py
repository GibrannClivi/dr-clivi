"""
Main Menu Page Definitions
Handles the primary navigation menu for Dr. Clivi
"""

from typing import Any, Dict


def get_main_menu_page() -> Dict[str, Any]:
    """Define main menu page structure"""
    return {
        "display_name": "mainMenu",
        "entry_fulfillment": {
            "message_type": "interactive_list",
            "body_text": "Hola {patient_name}, por favor utiliza el menú de opciones.",
            "action_button_text": "Seleccionar opción",
            "sections": [{
                "title": "Menú:",
                "rows": [
                    {
                        "id": "APPOINTMENTS",
                        "title": "Citas",
                        "description": "Agenda/Re-agendamiento 🗓️"
                    },
                    {
                        "id": "MEASUREMENTS",
                        "title": "Mediciones",
                        "description": "Enviar mediciones 📏"
                    },
                    {
                        "id": "MEASUREMENTS_REPORT",
                        "title": "Reporte mediciones",
                        "description": "Reporte de mediciones 📈"
                    },
                    {
                        "id": "INVOICE_LABS",
                        "title": "Facturas y estudios",
                        "description": "Facturación, estudios y órdenes📂"
                    },
                    {
                        "id": "MEDS_GLP",
                        "title": "Estatus de envíos",
                        "description": "Meds/Glucómetro/Tiras📦"
                    },
                    {
                        "id": "QUESTION_TYPE",
                        "title": "Enviar pregunta",
                        "description": "Enviar pregunta a agente/especialista ❔"
                    },
                    {
                        "id": "NO_NEEDED_QUESTION_PATIENT",
                        "title": "No es necesario",
                        "description": "No requiero apoyo 👍"
                    },
                    {
                        "id": "PATIENT_COMPLAINT",
                        "title": "Presentar queja",
                        "description": "Enviar queja sobre el servicio 📣"
                    }
                ]
            }]
        },
        "transition_routes": {
            "APPOINTMENTS": {
                "target_page": "apptsMenu",
                "event_log": "CLICKED_BUTTON_MAIN_MENU"
            },
            "MEASUREMENTS": {
                "target_page": "measurementsMenu",
                "event_log": "CLICKED_BUTTON_MAIN_MENU"
            },
            "MEASUREMENTS_REPORT": {
                "target_page": "measurementsReports",
                "event_log": "CLICKED_BUTTON_MAIN_MENU"
            },
            "INVOICE_LABS": {
                "target_page": "invoiceLabsMenu",
                "event_log": "CLICKED_BUTTON_MAIN_MENU"
            },
            "MEDS_GLP": {
                "target_page": "medsSuppliesStatus",
                "event_log": "CLICKED_BUTTON_MAIN_MENU"
            },
            "QUESTION_TYPE": {
                "target_page": "questionsTags",
                "event_log": "CLICKED_BUTTON_MAIN_MENU"
            },
            "NO_NEEDED_QUESTION_PATIENT": {
                "target_page": "endSession",
                "event_log": "CLICKED_BUTTON_MAIN_MENU"
            },
            "PATIENT_COMPLAINT": {
                "target_flow": "presentComplaintTag",
                "event_log": "CLICKED_BUTTON_MAIN_MENU"
            }
        }
    }


def get_end_session_page() -> Dict[str, Any]:
    """Define end session page"""
    return {
        "display_name": "endSession",
        "entry_fulfillment": {
            "message_type": "text",
            "text": "Gracias por usar Dr. Clivi. ¡Que tengas un excelente día!"
        },
        "transition_routes": {}
    }


def get_questions_tags_page() -> Dict[str, Any]:
    """Define questions tags page"""
    return {
        "display_name": "questionsTags",
        "entry_fulfillment": {
            "message_type": "button_menu",
            "text_body": "¿Sobre qué tema tienes dudas?",
            "buttons": [
                {
                    "id": "DIABETES_QUESTION",
                    "text": "Diabetes"
                },
                {
                    "id": "NUTRITION_QUESTION",
                    "text": "Nutrición"
                },
                {
                    "id": "PSYCHOLOGY_QUESTION",
                    "text": "Psicología"
                },
                {
                    "id": "SUPPLIES_QUESTION",
                    "text": "Insumos"
                },
                {
                    "id": "HIGH_SPECIALIZATION_QUESTION",
                    "text": "Alta especialidad"
                }
            ]
        },
        "transition_routes": {
            "DIABETES_QUESTION": {
                "target_page": "sendQuestion",
                "set_parameters": {
                    "questionTag": "diabetes"
                }
            },
            "NUTRITION_QUESTION": {
                "target_flow": "nutritionQuestionTag"
            },
            "PSYCHOLOGY_QUESTION": {
                "target_flow": "psychoQuestionTag"
            },
            "SUPPLIES_QUESTION": {
                "target_flow": "suppliesQuestionTag"
            },
            "HIGH_SPECIALIZATION_QUESTION": {
                "target_flow": "highSpecializationQuestionTag"
            }
        }
    }


def get_send_question_page() -> Dict[str, Any]:
    """Define send question page"""
    return {
        "display_name": "sendQuestion",
        "entry_fulfillment": {
            "message_type": "text",
            "text": "Por favor, escribe tu pregunta y nuestro especialista te responderá a la brevedad."
        },
        "transition_routes": {}
    }
