"""
Appointment Management Pages
Handles all appointment-related page definitions
"""

from typing import Any, Dict


def get_appointments_menu_page() -> Dict[str, Any]:
    """Define appointments menu page"""
    return {
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
                "target_page": "appointmentsList",
                "function_call": "APPOINTMENT_LIST_SEND"
            },
            "APPOINTMENT_RESCHEDULER": {
                "target_page": "appointmentReschedule",
                "function_call": "APPOINTMENT_SEND_CANCEL_LIST",
                "params": {"isReschedule": True}
            },
            "SEND_QUESTION": {
                "target_page": "questionsTags"
            }
        }
    }


def get_appointments_list_page() -> Dict[str, Any]:
    """Define appointments list page"""
    return {
        "display_name": "appointmentsList",
        "entry_fulfillment": {
            "message_type": "button_menu",
            "text_body": "📅 **Gestión de Citas Médicas**\n\n¿Qué te gustaría hacer?",
            "buttons": [
                {
                    "id": "VIEW_CURRENT_APPOINTMENTS",
                    "text": "👀 Ver mis citas actuales"
                },
                {
                    "id": "SCHEDULE_NEW_APPOINTMENT",
                    "text": "📝 Agendar nueva cita"
                },
                {
                    "id": "RESCHEDULE_APPOINTMENT",
                    "text": "🔄 Re-agendar cita existente"
                },
                {
                    "id": "CANCEL_APPOINTMENT",
                    "text": "❌ Cancelar cita"
                },
                {
                    "id": "BACK_TO_MAIN_MENU",
                    "text": "🔙 Volver al menú principal"
                }
            ]
        },
        "transition_routes": {
            "VIEW_CURRENT_APPOINTMENTS": {
                "target_page": "appointmentsView",
                "function_call": "APPOINTMENT_LIST_SEND"
            },
            "SCHEDULE_NEW_APPOINTMENT": {
                "target_page": "appointmentSchedule",
                "function_call": "APPOINTMENT_SCHEDULE_NEW"
            },
            "RESCHEDULE_APPOINTMENT": {
                "target_page": "appointmentReschedule",
                "function_call": "APPOINTMENT_SEND_CANCEL_LIST",
                "params": {"isReschedule": True}
            },
            "CANCEL_APPOINTMENT": {
                "target_page": "appointmentCancel",
                "function_call": "APPOINTMENT_SEND_CANCEL_LIST",
                "params": {"isCancel": True}
            },
            "BACK_TO_MAIN_MENU": {
                "target_page": "mainMenu"
            }
        }
    }


def get_appointments_view_page() -> Dict[str, Any]:
    """Define appointments view page"""
    return {
        "display_name": "appointmentsView",
        "entry_fulfillment": {
            "message_type": "text",
            "text": "📋 **Tus Citas Programadas:**\n\n🔹 **Próxima cita:** Endocrinología\n📅 Fecha: 15 de Julio, 2025\n🕐 Hora: 10:00 AM\n👩‍⚕️ Dr. María González\n💻 Modalidad: Virtual\n\n✅ Estado: Confirmada\n\n📝 **Preparación:**\n- Ten lista tu glucómetro\n- Lleva tu registro de glucosas\n- Prepara tus medicamentos actuales\n\n¿Te gustaría modificar esta cita o agendar una nueva?"
        },
        "transition_routes": {}
    }


def get_appointment_schedule_page() -> Dict[str, Any]:
    """Define appointment schedule page"""
    return {
        "display_name": "appointmentSchedule",
        "entry_fulfillment": {
            "message_type": "button_menu",
            "text_body": "📅 **Agendar Nueva Cita**\n\n¿Qué tipo de especialista necesitas?",
            "buttons": [
                {
                    "id": "ENDOCRINOLOGIST",
                    "text": "🩺 Endocrinólogo"
                },
                {
                    "id": "NUTRITIONIST",
                    "text": "🥗 Nutriólogo"
                },
                {
                    "id": "PSYCHOLOGIST", 
                    "text": "🧠 Psicólogo"
                },
                {
                    "id": "GENERAL_MEDICINE",
                    "text": "👨‍⚕️ Medicina General"
                }
            ]
        },
        "transition_routes": {
            "ENDOCRINOLOGIST": {
                "target_page": "appointmentConfirm",
                "set_parameters": {"specialty": "endocrinology"}
            },
            "NUTRITIONIST": {
                "target_page": "appointmentConfirm", 
                "set_parameters": {"specialty": "nutrition"}
            },
            "PSYCHOLOGIST": {
                "target_page": "appointmentConfirm",
                "set_parameters": {"specialty": "psychology"}
            },
            "GENERAL_MEDICINE": {
                "target_page": "appointmentConfirm",
                "set_parameters": {"specialty": "general"}
            }
        }
    }


def get_appointment_confirm_page() -> Dict[str, Any]:
    """Define appointment confirm page"""
    return {
        "display_name": "appointmentConfirm",
        "entry_fulfillment": {
            "message_type": "text",
            "text": "✅ **Cita Programada Exitosamente**\n\n📋 **Detalles de tu cita:**\n🔹 Especialidad: {specialty}\n📅 Fecha: Próximo disponible\n🕐 Hora: Se te notificará\n\n📞 **Próximos pasos:**\n1. Recibirás confirmación en 24 horas\n2. Te enviaremos el enlace de videollamada\n3. Recordatorio 1 día antes\n\n¿Necesitas algo más?"
        },
        "transition_routes": {}
    }


def get_appointment_reschedule_page() -> Dict[str, Any]:
    """Define appointment reschedule page"""
    return {
        "display_name": "appointmentReschedule", 
        "entry_fulfillment": {
            "message_type": "text",
            "text": "🔄 **Re-agendar Cita**\n\nPara re-agendar tu cita, por favor contacta a nuestro equipo:\n\n📞 **Teléfono:** +52 55 8840 9477\n💬 **WhatsApp:** Disponible 24/7\n\nNuestro equipo te ayudará a encontrar una nueva fecha que se ajuste a tu agenda."
        },
        "transition_routes": {}
    }


def get_appointment_cancel_page() -> Dict[str, Any]:
    """Define appointment cancel page"""
    return {
        "display_name": "appointmentCancel",
        "entry_fulfillment": {
            "message_type": "text", 
            "text": "❌ **Cancelar Cita**\n\n⚠️ **Importante:** Las cancelaciones deben hacerse con al menos 24 horas de anticipación.\n\nPara cancelar tu cita, por favor contacta:\n\n📞 **Teléfono:** +52 55 8840 9477\n💬 **WhatsApp:** Disponible 24/7\n\n¿Estás seguro que quieres cancelar? Nuestro equipo puede ayudarte a encontrar una mejor fecha."
        },
        "transition_routes": {}
    }
