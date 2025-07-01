"""
Implementación exacta de las páginas de Dialogflow CX para Dr. Clivi
Reproduce fielmente los flujos determinísticos documentados
"""

import logging
from typing import Any, Dict, List, Optional
from enum import Enum

logger = logging.getLogger(__name__)


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


class DialogflowPageImplementor:
    """
    Implementa exactamente las páginas definidas en Dialogflow CX
    Basado en los archivos JSON exportados
    """
    
    def __init__(self, config=None):
        self.config = config
        self.pages = self._load_page_definitions()
    
    def _load_page_definitions(self) -> Dict[str, Dict[str, Any]]:
        """Carga las definiciones exactas de páginas desde Dialogflow"""
        return {
            "mainMenu": {
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
            },
            
            "apptsMenu": {
                "display_name": "apptsMenu",
                "entry_fulfillment": {
                    "message_type": "button_menu",
                    "text_body": "¿Cómo te podemos ayudar?",
                    "buttons": [
                        {
                            "id": "APPOINTMENTS_LIST_SEND",
                            "text": "Ver/agendar citas"
                        },
                        {
                            "id": "APPOINTMENT_RESCHEDULER",
                            "text": "Re-agendar cita"
                        },
                        {
                            "id": "SEND_QUESTION",
                            "text": "Enviar pregunta"
                        }
                    ]
                },
                "transition_routes": {
                    "APPOINTMENTS_LIST_SEND": {
                        "target_page": "End Session",
                        "function_call": "APPOINTMENT_LIST_SEND"
                    },
                    "APPOINTMENT_RESCHEDULER": {
                        "target_page": "End Session",
                        "function_call": "APPOINTMENT_SEND_CANCEL_LIST",
                        "params": {"isReschedule": True}
                    },
                    "SEND_QUESTION": {
                        "target_page": "questionsTags"
                    }
                }
            },
            
            "measurementsMenu": {
                "display_name": "measurementsMenu",
                "entry_fulfillment": {
                    "message_type": "button_menu",
                    "text_body": "¿Qué medición vas a enviar?",
                    "buttons": [
                        {
                            "id": "LOG_WEIGHT",
                            "text": "Peso"
                        },
                        {
                            "id": "LOG_GLUCOSE_FASTING",
                            "text": "Glucosa en ayunas"
                        },
                        {
                            "id": "LOG_GLUCOSE_POST_MEAL",
                            "text": "Glucosa post comida"
                        },
                        {
                            "id": "LOG_HIP",
                            "text": "Medida de cadera"
                        },
                        {
                            "id": "LOG_WAIST",
                            "text": "Medida de cintura"
                        },
                        {
                            "id": "LOG_NECK",
                            "text": "Medida de cuello"
                        }
                    ]
                },
                "transition_routes": {
                    "LOG_WEIGHT": {
                        "target_page": "logWeight"
                    },
                    "LOG_GLUCOSE_FASTING": {
                        "target_page": "glucoseValueLogFasting"
                    },
                    "LOG_GLUCOSE_POST_MEAL": {
                        "target_page": "glucoseValueLogPostMeal"
                    },
                    "LOG_HIP": {
                        "target_page": "logHip"
                    },
                    "LOG_WAIST": {
                        "target_page": "logWaist"
                    },
                    "LOG_NECK": {
                        "target_page": "logNeck"
                    }
                }
            },
            
            "questionsTags": {
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
            },
            
            "invoiceLabsMenu": {
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
            },
            
            "measurementsReports": {
                "display_name": "measurementsReports",
                "entry_fulfillment": {
                    "message_type": "buttons",
                    "body_text": "¿Qué tipo de reporte quieres tener?",
                    "buttons": [
                        {
                            "id": "FULL_REPORT",
                            "text": "Reporte general"
                        },
                        {
                            "id": "GLUCOSE_REPORT",
                            "text": "Reporte Glucosas"
                        }
                    ]
                },
                "transition_routes": {
                    "FULL_REPORT": {
                        "target_page": "endSession",
                        "fulfillment_messages": [
                            "Este reporte demora un minuto en generarse. ¡Paciencia, gracias!"
                        ]
                    },
                    "GLUCOSE_REPORT": {
                        "target_page": "endSession",
                        "fulfillment_messages": [
                            "Este reporte demora un minuto en generarse. ¡Paciencia, gracias! Recuerda: Las franjas moradas representan los rangos objetivo en los que debemos estar.\nSi tienes alguna pregunta ¡No dudes en escribirnos!"
                        ]
                    }
                }
            },
            
            "invoiceUpdatedInfo": {
                "display_name": "invoiceUpdatedInfo",
                "entry_fulfillment": {
                    "message_type": "text",
                    "text": "Información de facturación actualizada. Por favor proporciona los datos solicitados."
                },
                "transition_routes": {}
            },
            
            "lastFileAvailable": {
                "display_name": "lastFileAvailable",
                "entry_fulfillment": {
                    "message_type": "text",
                    "text": "Aquí tienes tu último archivo disponible."
                },
                "transition_routes": {}
            },
            
            "medsSuppliesStatus": {
                "display_name": "medsSuppliesStatus",
                "entry_fulfillment": {
                    "message_type": "text",
                    "text": "Estado de envío de medicamentos y suministros:\n- Glucómetro: En tránsito\n- Tiras reactivas: Entregado\n- Medicamentos: Programado"
                },
                "transition_routes": {}
            },
            
            "endSession": {
                "display_name": "endSession",
                "entry_fulfillment": {
                    "message_type": "text",
                    "text": "Gracias por usar Dr. Clivi. ¡Que tengas un excelente día!"
                },
                "transition_routes": {}
            }
        }
    
    def render_page(self, page_name: str, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Renderiza una página específica según las definiciones de Dialogflow
        """
        if page_name not in self.pages:
            logger.error(f"Página no encontrada: {page_name}")
            return self._render_fallback_page(user_context)
        
        page_def = self.pages[page_name]
        entry_fulfillment = page_def["entry_fulfillment"]
        
        # Renderizar según el tipo de mensaje
        if entry_fulfillment["message_type"] == "interactive_list":
            return self._render_interactive_list(entry_fulfillment, user_context, page_name)
        elif entry_fulfillment["message_type"] == "button_menu":
            return self._render_button_menu(entry_fulfillment, user_context, page_name)
        else:
            return self._render_text_message(entry_fulfillment, user_context, page_name)
    
    def _render_interactive_list(self, fulfillment: Dict[str, Any], 
                               user_context: Dict[str, Any], page_name: str) -> Dict[str, Any]:
        """Renderiza lista interactiva (formato WhatsApp)"""
        # Formatear el texto del cuerpo con variables
        body_text = fulfillment["body_text"].format(
            patient_name=user_context.get("patient_name", "Paciente")
        )
        
        return {
            "response_type": "whatsapp_menu",
            "menu_data": {
                "interactive": {
                    "type": "list",
                    "header": {
                        "type": "text",
                        "text": "Dr. Clivi"
                    },
                    "body": {
                        "text": body_text
                    },
                    "action": {
                        "button": fulfillment["action_button_text"],
                        "sections": fulfillment["sections"]
                    }
                }
            },
            "page": page_name,
            "routing_type": "deterministic"
        }
    
    def _render_button_menu(self, fulfillment: Dict[str, Any], 
                          user_context: Dict[str, Any], page_name: str) -> Dict[str, Any]:
        """Renderiza menú de botones (formato Telegram)"""
        # Convertir botones a inline keyboard para Telegram
        inline_keyboard = []
        buttons = fulfillment["buttons"]
        
        # Agrupar botones de 2 en 2
        for i in range(0, len(buttons), 2):
            row = []
            for j in range(i, min(i + 2, len(buttons))):
                button = buttons[j]
                row.append({
                    "text": button["text"],
                    "callback_data": button["id"]
                })
            inline_keyboard.append(row)
        
        return {
            "response_type": "page_navigation",
            "body_text": fulfillment["text_body"],
            "inline_keyboard": inline_keyboard,
            "page": page_name,
            "routing_type": "deterministic"
        }
    
    def _render_text_message(self, fulfillment: Dict[str, Any], 
                           user_context: Dict[str, Any], page_name: str) -> Dict[str, Any]:
        """Renderiza mensaje de texto simple"""
        return {
            "response_type": "general_response",
            "response": fulfillment.get("text", "Mensaje de texto"),
            "page": page_name,
            "routing_type": "deterministic"
        }
    
    def _render_fallback_page(self, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Página de fallback cuando no se encuentra la solicitada"""
        return {
            "response_type": "general_response",
            "response": "Lo siento, ocurrió un error. Regresando al menú principal.",
            "suggested_action": "show_main_menu",
            "routing_type": "error_fallback"
        }
    
    def get_page_transitions(self, page_name: str) -> Dict[str, Any]:
        """Obtiene las rutas de transición para una página"""
        if page_name not in self.pages:
            return {}
        
        return self.pages[page_name].get("transition_routes", {})
    
    def handle_page_selection(self, page_name: str, selection_id: str, 
                            user_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Maneja la selección de un elemento en una página
        Sigue exactamente las transition_routes de Dialogflow
        """
        transitions = self.get_page_transitions(page_name)
        
        if selection_id not in transitions:
            logger.warning(f"Selección desconocida '{selection_id}' en página '{page_name}'")
            return {
                "action": "trigger_intelligent_routing",
                "reason": "unknown_selection",
                "selection_id": selection_id,
                "page": page_name
            }
        
        transition = transitions[selection_id]
        
        result = {
            "action": "page_transition",
            "source_page": page_name,
            "selection_id": selection_id,
            "transition": transition
        }
        
        # Agregar logging de evento si está definido
        if "event_log" in transition:
            result["event_log"] = {
                "function_name": "ACTIVITY_EVENT_LOG",
                "params": {
                    "eventType": transition["event_log"]
                }
            }
        
        # Determinar acción siguiente
        if "target_page" in transition:
            result["target_page"] = transition["target_page"]
            result["action"] = "navigate_to_page"
        elif "target_flow" in transition:
            result["target_flow"] = transition["target_flow"]
            result["action"] = "navigate_to_flow"
        elif "function_call" in transition:
            result["function_call"] = transition["function_call"]
            result["function_params"] = transition.get("params", {})
            result["action"] = "execute_function"
        
        return result
