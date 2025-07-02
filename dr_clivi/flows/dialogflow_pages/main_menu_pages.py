"""
Páginas del menú principal de Dr. Clivi
"""

from typing import Any, Dict


class MainMenuPages:
    """Definiciones de páginas del menú principal"""
    
    @staticmethod
    def get_main_menu_page() -> Dict[str, Any]:
        """Página principal del menú"""
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
    
    @staticmethod
    def get_end_session_page() -> Dict[str, Any]:
        """Página de fin de sesión"""
        return {
            "display_name": "endSession",
            "entry_fulfillment": {
                "message_type": "text",
                "text": "Gracias por usar Dr. Clivi. ¡Que tengas un excelente día!"
            },
            "transition_routes": {}
        }
    
    @staticmethod
    def get_invoice_labs_menu_page() -> Dict[str, Any]:
        """Página del menú de facturas y laboratorios"""
        return {
            "display_name": "invoiceLabsMenu",
            "entry_fulfillment": {
                "message_type": "interactive_list",
                "body_text": "¿Qué necesitas?",
                "action_button_text": "Selecciona",
                "sections": [{
                    "title": "Menú",
                    "rows": [
                        {
                            "id": "INVOICE",
                            "title": "Facturación",
                            "description": "Facturas"
                        },
                        {
                            "id": "UPLOAD_LABS",
                            "title": "Labs/Recetas/Plan",
                            "description": "Obtener último archivo"
                        },
                        {
                            "id": "CALL_SUPPORT",
                            "title": "Marcar a Clivi",
                            "description": "Llamar equipo Clivi"
                        },
                        {
                            "id": "PX_QUESTION_TAG",
                            "title": "Requiero soporte",
                            "description": "Soporte/servicio"
                        }
                    ]
                }]
            },
            "transition_routes": {
                "INVOICE": {
                    "target_page": "invoiceUpdatedInfo"
                },
                "UPLOAD_LABS": {
                    "target_page": "lastFileAvailable"
                },
                "CALL_SUPPORT": {
                    "target_page": "endSession",
                    "fulfillment_messages": [
                        "Presiona en el número de abajo para marcarnos, por favor",
                        "+525588409477"
                    ]
                },
                "PX_QUESTION_TAG": {
                    "target_flow": "helpDeskSubMenu"
                }
            }
        }
    
    @staticmethod
    def get_meds_supplies_status_page() -> Dict[str, Any]:
        """Página de estado de medicamentos y suministros"""
        return {
            "display_name": "medsSuppliesStatus",
            "entry_fulfillment": {
                "message_type": "text",
                "text": "Estado de envío de medicamentos y suministros:\n- Glucómetro: En tránsito\n- Tiras reactivas: Entregado\n- Medicamentos: Programado"
            },
            "transition_routes": {}
        }
    
    @staticmethod
    def get_invoice_updated_info_page() -> Dict[str, Any]:
        """Página de información de facturación actualizada"""
        return {
            "display_name": "invoiceUpdatedInfo",
            "entry_fulfillment": {
                "message_type": "text",
                "text": "Información de facturación actualizada. Por favor proporciona los datos solicitados."
            },
            "transition_routes": {}
        }
    
    @staticmethod
    def get_last_file_available_page() -> Dict[str, Any]:
        """Página de último archivo disponible"""
        return {
            "display_name": "lastFileAvailable",
            "entry_fulfillment": {
                "message_type": "text",
                "text": "Aquí tienes tu último archivo disponible."
            },
            "transition_routes": {}
        }
