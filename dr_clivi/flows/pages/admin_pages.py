"""
Administrative Pages (Invoices, Labs, Supplies)
Handles billing, file management, and supply tracking pages
"""

from typing import Any, Dict


def get_invoice_labs_menu_page() -> Dict[str, Any]:
    """Define invoice and labs menu page"""
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


def get_invoice_updated_info_page() -> Dict[str, Any]:
    """Define invoice updated info page"""
    return {
        "display_name": "invoiceUpdatedInfo",
        "entry_fulfillment": {
            "message_type": "text",
            "text": "Información de facturación actualizada. Por favor proporciona los datos solicitados."
        },
        "transition_routes": {}
    }


def get_last_file_available_page() -> Dict[str, Any]:
    """Define last file available page"""
    return {
        "display_name": "lastFileAvailable",
        "entry_fulfillment": {
            "message_type": "text",
            "text": "Aquí tienes tu último archivo disponible."
        },
        "transition_routes": {}
    }


def get_meds_supplies_status_page() -> Dict[str, Any]:
    """Define meds and supplies status page"""
    return {
        "display_name": "medsSuppliesStatus",
        "entry_fulfillment": {
            "message_type": "text",
            "text": "Estado de envío de medicamentos y suministros:\n- Glucómetro: En tránsito\n- Tiras reactivas: Entregado\n- Medicamentos: Programado"
        },
        "transition_routes": {}
    }
