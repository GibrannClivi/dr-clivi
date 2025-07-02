"""
Measurement Management Pages
Handles all measurement-related page definitions
"""

from typing import Any, Dict


def get_measurements_menu_page() -> Dict[str, Any]:
    """Define measurements menu page"""
    return {
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
    }


def get_measurements_reports_page() -> Dict[str, Any]:
    """Define measurements reports page"""
    return {
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
    }


def get_log_weight_page() -> Dict[str, Any]:
    """Define log weight page"""
    return {
        "display_name": "logWeight",
        "entry_fulfillment": {
            "message_type": "text",
            "text": "Por favor, envía tu peso actual en kilogramos. Ejemplo: 70.5"
        },
        "transition_routes": {}
    }


def get_glucose_fasting_page() -> Dict[str, Any]:
    """Define glucose fasting page"""
    return {
        "display_name": "glucoseValueLogFasting",
        "entry_fulfillment": {
            "message_type": "text",
            "text": "Por favor, envía tu glucosa en ayunas en mg/dl. Ejemplo: 95"
        },
        "transition_routes": {}
    }


def get_glucose_post_meal_page() -> Dict[str, Any]:
    """Define glucose post meal page"""
    return {
        "display_name": "glucoseValueLogPostMeal",
        "entry_fulfillment": {
            "message_type": "text",
            "text": "Por favor, envía tu glucosa post comida en mg/dl. Ejemplo: 140"
        },
        "transition_routes": {}
    }


def get_log_hip_page() -> Dict[str, Any]:
    """Define log hip page"""
    return {
        "display_name": "logHip",
        "entry_fulfillment": {
            "message_type": "text",
            "text": "Por favor, envía tu medida de cadera en centímetros. Ejemplo: 95"
        },
        "transition_routes": {}
    }


def get_log_waist_page() -> Dict[str, Any]:
    """Define log waist page"""
    return {
        "display_name": "logWaist",
        "entry_fulfillment": {
            "message_type": "text",
            "text": "Por favor, envía tu medida de cintura en centímetros. Ejemplo: 80"
        },
        "transition_routes": {}
    }


def get_log_neck_page() -> Dict[str, Any]:
    """Define log neck page"""
    return {
        "display_name": "logNeck",
        "entry_fulfillment": {
            "message_type": "text",
            "text": "Por favor, envía tu medida de cuello en centímetros. Ejemplo: 35"
        },
        "transition_routes": {}
    }
