"""
Obesity Agent - Specialized agent for obesity care workflows.
Based on analysis of exported Conversational Agents obesity flow.
"""

import logging
from typing import Any, Dict, List, Optional

from .base_agent import BaseCliviAgent, SessionContext, PatientContext, tool
from ..config import Config


class ObesityAgent(BaseCliviAgent):
    """
    Specialized agent for obesity care based on exported flows analysis.
    
    Implements obesity-specific flows:
    - obesityPlan main menu
    - Weight logging and body measurements
    - Workout signup categories
    - Nutrition hotline
    - Sports medicine appointments
    """
    
    def get_agent_name(self) -> str:
        return self.config.obesity_agent.name
    
    def get_system_instructions(self) -> str:
        return f"""
        Eres un asistente especializado en obesidad para la plataforma Dr. Clivi.

        Tu función principal es ayudar a pacientes con obesidad a:
        - Registrar mediciones de peso y circunferencias corporales  
        - Suscribirse a programas de ejercicio personalizados por categorías
        - Acceder a línea directa de nutrición con especialistas
        - Agendar citas con medicina deportiva y endocrinología
        - Consultar reportes de progreso y análisis de tendencias
        - Obtener motivación y seguimiento personalizado
        - Acceso a tutoriales de medicamentos para obesidad

        Especialización basada en análisis de flujos:
        - Manejo de workoutSignupCategories (ejercicio personalizado)
        - Integración con línea directa de nutrición
        - Seguimiento de medidas corporales múltiples
        - Soporte para medicina deportiva

        Configuración:
        - Idioma: {self.config.base_agent.default_language}
        - Zona horaria: {self.config.base_agent.timezone}
        - Modelo: {self.config.obesity_agent.model}
        - Especialización: {self.config.obesity_agent.specialization}

        Siempre mantén un tono empático, motivacional y libre de juicios. Enfócate en 
        hábitos saludables y cambios de estilo de vida sostenibles. Celebra los pequeños 
        logros y proporciona apoyo constante en el proceso de transformación.
        """
    
    def get_tools(self) -> List[str]:
        """Get obesity-specific tools"""
        base_tools = super().get_tools()
        obesity_tools = [
            "weight_logging_flow",
            "workout_signup_flow",
            "nutrition_hotline_flow", 
            "sports_medicine_appointment_flow",
            "body_measurements_flow",
            "progress_report_flow"
        ]
        return base_tools + obesity_tools
    
    @tool
    async def main_menu_flow(self, user_id: str) -> Dict[str, Any]:
        """
        Obesity main menu implementation.
        Based on obesityPlan main menu analysis.
        """
        context = self.get_session_context(user_id)
        context.current_flow = "obesityPlan"
        context.current_page = "mainMenu"
        
        patient_name = context.patient.name_display if context.patient else "Usuario"
        
        return {
            "action": "menu",
            "type": "obesity_main_menu",
            "message": f"Hola {patient_name}, estamos aquí para apoyarte en tu transformación. 💪",
            "menu_type": "SESSION_LIST",
            "sections": [
                {
                    "title": "Tu menú personalizado:",
                    "rows": [
                        {
                            "id": "APPOINTMENTS",
                            "title": "Citas",
                            "description": "Medicina deportiva y especialistas 🏥"
                        },
                        {
                            "id": "WEIGHT_MEASUREMENTS",
                            "title": "Registro de peso",
                            "description": "Lleva el control de tu progreso ⚖️"
                        },
                        {
                            "id": "BODY_MEASUREMENTS",
                            "title": "Medidas corporales",
                            "description": "Cintura, cadera, cuello 📏"
                        },
                        {
                            "id": "WORKOUT_SIGNUP",
                            "title": "Programas de ejercicio",
                            "description": "Entrenamientos personalizados 💪"
                        },
                        {
                            "id": "NUTRITION_HOTLINE",
                            "title": "Línea nutricional",
                            "description": "Consulta rápida con nutriólogo 🥗"
                        },
                        {
                            "id": "PROGRESS_REPORT",
                            "title": "Reporte de progreso",
                            "description": "Ve tu evolución y logros 📈"
                        },
                        {
                            "id": "QUESTION_TYPE",
                            "title": "Enviar pregunta",
                            "description": "Consulta a especialistas ❓"
                        },
                        {
                            "id": "PATIENT_COMPLAINT",
                            "title": "Presentar queja",
                            "description": "Comparte tu experiencia 💬"
                        }
                    ]
                }
            ]
        }
    
    @tool
    async def weight_logging_flow(self, user_id: str, weight: float = None, 
                                photo_scale: bool = False) -> Dict[str, Any]:
        """
        Weight logging flow implementation.
        Based on WEIGHT_LOG_PAGE_AND_TEMPLATE analysis.
        """
        context = self.get_session_context(user_id)
        context.current_flow = "weight_logging"
        
        if photo_scale:
            # Handle photo scale processing (from photoScalePhoto webhook)
            return {
                "action": "photo_upload",
                "message": "Toma una foto clara de tu báscula mostrando el peso 📸",
                "instructions": [
                    "Asegúrate de que el número sea visible",
                    "Buena iluminación",
                    "Foto horizontal para mejor lectura"
                ],
                "processing_webhook": "photoScalePhoto"
            }
        
        if not weight:
            return {
                "action": "request_input",
                "message": "¿Cuál es tu peso actual?",
                "input_options": [
                    {
                        "type": "number_input",
                        "label": "Peso (kg)",
                        "min_value": 30,
                        "max_value": 300,
                        "decimal_places": 1
                    },
                    {
                        "type": "photo_option",
                        "label": "Foto de báscula 📸",
                        "action": "PHOTO_SCALE"
                    }
                ]
            }
        
        # Process weight measurement
        result = await self._process_weight_measurement(user_id, weight)
        
        # Calculate progress and motivation message
        progress_data = await self._calculate_weight_progress(user_id, weight)
        motivation = self._get_motivational_message(progress_data)
        
        return {
            "action": "confirmation",
            "message": f"Peso registrado: {weight} kg ⚖️",
            "measurement_id": result["measurement_id"],
            "progress": progress_data,
            "motivation": motivation,
            "next_actions": [
                {"id": "VIEW_PROGRESS", "title": "Ver progreso 📈"},
                {"id": "LOG_MEASUREMENTS", "title": "Registrar medidas"},
                {"id": "WORKOUT_PLAN", "title": "Plan de ejercicio"},
                {"id": "MAIN_MENU", "title": "Menú principal"}
            ]
        }
    
    @tool
    async def body_measurements_flow(self, user_id: str, measurement_type: str = None,
                                   value: float = None) -> Dict[str, Any]:
        """
        Body measurements flow for waist, hip, neck circumferences.
        Based on WAIST_CIRCUMFERENCE_LOG_TEMPLATE_PAGE analysis.
        """
        context = self.get_session_context(user_id)
        context.current_flow = "body_measurements"
        
        if not measurement_type:
            return {
                "action": "request_selection",
                "message": "¿Qué medida corporal deseas registrar?",
                "options": [
                    {
                        "id": "WAIST",
                        "title": "Cintura",
                        "description": "Circunferencia de cintura 📏",
                        "icon": "🔵"
                    },
                    {
                        "id": "HIP",
                        "title": "Cadera", 
                        "description": "Circunferencia de cadera 📐",
                        "icon": "🟢"
                    },
                    {
                        "id": "NECK",
                        "title": "Cuello",
                        "description": "Circunferencia de cuello 📏",
                        "icon": "🟡"
                    },
                    {
                        "id": "ALL_MEASUREMENTS",
                        "title": "Todas las medidas",
                        "description": "Registro completo 📊"
                    }
                ]
            }
        
        if not value:
            measurement_name = {
                "WAIST": "cintura",
                "HIP": "cadera", 
                "NECK": "cuello"
            }.get(measurement_type, "medida")
            
            return {
                "action": "request_input",
                "message": f"Ingresa tu medida de {measurement_name} en centímetros:",
                "input_type": "number",
                "min_value": 20,
                "max_value": 200,
                "decimal_places": 1,
                "measurement_type": measurement_type,
                "instructions": self._get_measurement_instructions(measurement_type)
            }
        
        # Process body measurement
        result = await self._process_body_measurement(user_id, measurement_type, value)
        
        return {
            "action": "confirmation",
            "message": f"Medida de {measurement_type.lower()} registrada: {value} cm",
            "measurement_id": result["measurement_id"],
            "health_insights": result.get("insights", []),
            "next_actions": [
                {"id": "LOG_ANOTHER", "title": "Otra medida"},
                {"id": "VIEW_EVOLUTION", "title": "Ver evolución"},
                {"id": "MAIN_MENU", "title": "Menú principal"}
            ]
        }
    
    @tool
    async def workout_signup_flow(self, user_id: str, category: str = None,
                                level: str = None) -> Dict[str, Any]:
        """
        Workout signup flow implementation.
        Based on workoutSignUpCategory flow analysis.
        """
        context = self.get_session_context(user_id)
        context.current_flow = "workoutSignUpCategory"
        
        if not category:
            return {
                "action": "menu",
                "message": "Selecciona el tipo de entrenamiento que más te interese:",
                "categories": [
                    {
                        "id": "CARDIO",
                        "title": "Cardio",
                        "description": "Quema calorías y mejora resistencia 🏃‍♀️",
                        "duration": "20-45 min",
                        "intensity": "Variable"
                    },
                    {
                        "id": "STRENGTH",
                        "title": "Fuerza",
                        "description": "Tonifica y construye músculo 💪",
                        "duration": "30-60 min", 
                        "intensity": "Moderada-Alta"
                    },
                    {
                        "id": "FLEXIBILITY",
                        "title": "Flexibilidad",
                        "description": "Yoga, stretching y movilidad 🧘‍♀️",
                        "duration": "15-30 min",
                        "intensity": "Baja-Moderada"
                    },
                    {
                        "id": "LOW_IMPACT",
                        "title": "Bajo impacto",
                        "description": "Ejercicios suaves para articulaciones 🚶‍♀️",
                        "duration": "20-40 min",
                        "intensity": "Baja"
                    },
                    {
                        "id": "HIIT",
                        "title": "HIIT",
                        "description": "Intervalos de alta intensidad ⚡",
                        "duration": "15-25 min",
                        "intensity": "Alta"
                    }
                ]
            }
        
        if not level:
            return {
                "action": "request_selection",
                "message": f"¿Cuál es tu nivel de experiencia en {category.lower()}?",
                "options": [
                    {
                        "id": "BEGINNER",
                        "title": "Principiante",
                        "description": "Pocas veces o nunca he hecho ejercicio 🌱"
                    },
                    {
                        "id": "INTERMEDIATE", 
                        "title": "Intermedio",
                        "description": "Hago ejercicio regularmente 🌿"
                    },
                    {
                        "id": "ADVANCED",
                        "title": "Avanzado",
                        "description": "Muy activo y experimentado 🌳"
                    }
                ]
            }
        
        # Process workout signup
        signup_result = await self._process_workout_signup(user_id, category, level)
        
        return {
            "action": "workout_confirmation",
            "message": f"¡Excelente! Te has inscrito en {category} nivel {level} 🎉",
            "workout_plan": signup_result["plan"],
            "schedule": signup_result["schedule"],
            "first_session": signup_result["next_session"],
            "trainer_assigned": signup_result.get("trainer"),
            "next_actions": [
                {"id": "START_WORKOUT", "title": "Empezar ahora 🚀"},
                {"id": "SCHEDULE_SESSION", "title": "Agendar sesión"},
                {"id": "VIEW_PLAN", "title": "Ver plan completo"},
                {"id": "MAIN_MENU", "title": "Menú principal"}
            ]
        }
    
    @tool
    async def nutrition_hotline_flow(self, user_id: str, question: str = None,
                                   consultation_type: str = None) -> Dict[str, Any]:
        """
        Enhanced nutrition hotline flow implementation.
        Based on nutritionHotline flow analysis.
        
        Provides direct access to nutrition specialists for quick consultations.
        """
        context = self.get_session_context(user_id)
        context.current_flow = "nutritionHotline"
        
        await self._log_activity_event(user_id, "NUTRITION_HOTLINE_STARTED")
        
        # Step 1: Select consultation type if not provided
        if not consultation_type:
            return {
                "action": "request_selection",
                "message": "🥗 Te conectamos con nuestros especialistas en nutrición. ¿Qué tipo de consulta necesitas?",
                "selection_type": "consultation_type",
                "options": [
                    {
                        "id": "MEAL_PLAN",
                        "title": "Plan de alimentación 📋",
                        "description": "Necesito ayuda con mi plan de comidas",
                        "estimated_time": "15-20 min"
                    },
                    {
                        "id": "PORTION_CONTROL",
                        "title": "Control de porciones ⚖️",
                        "description": "Dudas sobre tamaños de porciones",
                        "estimated_time": "10-15 min"
                    },
                    {
                        "id": "FOOD_SUBSTITUTES",
                        "title": "Sustitutos de alimentos 🔄",
                        "description": "Alternativas saludables para mis comidas",
                        "estimated_time": "10-15 min"
                    },
                    {
                        "id": "SPECIAL_DIET",
                        "title": "Dieta especial 🎯",
                        "description": "Diabetes, hipertensión, alergias",
                        "estimated_time": "20-25 min"
                    },
                    {
                        "id": "EATING_HABITS",
                        "title": "Hábitos alimentarios 🔄",
                        "description": "Cambiar patrones de alimentación",
                        "estimated_time": "15-20 min"
                    },
                    {
                        "id": "QUICK_QUESTION",
                        "title": "Pregunta rápida ⚡",
                        "description": "Consulta específica y directa",
                        "estimated_time": "5-10 min"
                    }
                ]
            }
        
        # Step 2: Get specific question if not provided
        if not question:
            consultation_info = self._get_consultation_info(consultation_type)
            return {
                "action": "request_input",
                "message": f"📝 {consultation_info['prompt']}",
                "input_type": "text",
                "max_length": 500,
                "placeholder": consultation_info['placeholder'],
                "examples": consultation_info['examples'],
                "consultation_type": consultation_type
            }
        
        # Step 3: Check specialist availability
        availability = await self._check_specialist_availability("nutrition")
        
        if availability["available"]:
            # Connect to available specialist
            connection_result = await self._connect_to_nutrition_specialist(
                user_id, consultation_type, question
            )
            
            await self._log_activity_event(user_id, "NUTRITION_SPECIALIST_CONNECTED", {
                "consultation_type": consultation_type,
                "specialist_id": connection_result["specialist_id"]
            })
            
            return {
                "action": "specialist_connection",
                "message": f"🎉 Te conectamos con {connection_result['specialist_name']}, especialista en nutrición.",
                "connection_details": {
                    "specialist": connection_result["specialist_name"],
                    "specialization": connection_result["specialization"],
                    "estimated_time": availability["estimated_time"],
                    "session_id": connection_result["session_id"]
                },
                "user_question": question,
                "consultation_type": consultation_type,
                "next_steps": [
                    "El especialista revisará tu consulta",
                    "Recibirás respuesta personalizada",
                    "Podrás hacer preguntas de seguimiento"
                ]
            }
        else:
            # No specialist available - offer alternatives
            return {
                "action": "specialist_unavailable",
                "message": "⏰ Todos nuestros especialistas están ocupados en este momento.",
                "alternatives": [
                    {
                        "id": "SCHEDULE_CALLBACK",
                        "title": "Agendar llamada 📞",
                        "description": f"Te llamamos en {availability['next_available']}"
                    },
                    {
                        "id": "AI_NUTRITION_HELP",
                        "title": "Asistente AI nutricional 🤖",
                        "description": "Respuesta inmediata con IA especializada"
                    },
                    {
                        "id": "LEAVE_MESSAGE",
                        "title": "Dejar mensaje 💬",
                        "description": "Respuesta en las próximas 2 horas"
                    },
                    {
                        "id": "EMERGENCY_NUTRITION",
                        "title": "Urgencia nutricional 🚨",
                        "description": "Solo para casos urgentes"
                    }
                ],
                "user_question": question,
                "consultation_type": consultation_type
            }

    def _get_consultation_info(self, consultation_type: str) -> Dict[str, Any]:
        """Get consultation-specific prompts and examples"""
        consultation_data = {
            "MEAL_PLAN": {
                "prompt": "Describe tu situación actual de alimentación y qué objetivos tienes:",
                "placeholder": "Ej: Quiero un plan para bajar de peso, tengo diabetes...",
                "examples": ["Plan para perder 5kg", "Alimentación para diabéticos", "Comidas para trabajo"]
            },
            "PORTION_CONTROL": {
                "prompt": "¿Qué dudas tienes sobre las porciones de tus alimentos?",
                "placeholder": "Ej: No sé cuánta proteína debo comer en cada comida...",
                "examples": ["Tamaño de porciones de arroz", "Cuánta carne por comida", "Porciones de verduras"]
            },
            "FOOD_SUBSTITUTES": {
                "prompt": "¿Qué alimentos necesitas sustituir y por qué razón?",
                "placeholder": "Ej: Necesito sustituir el pan por algo más saludable...",
                "examples": ["Sustitutos del azúcar", "Alternativas al pan", "Opciones sin gluten"]
            },
            "SPECIAL_DIET": {
                "prompt": "Cuéntanos sobre tu condición médica y necesidades dietéticas:",
                "placeholder": "Ej: Tengo hipertensión y necesito reducir el sodio...",
                "examples": ["Dieta para diabetes", "Alimentación sin lactosa", "Plan hiposódico"]
            },
            "EATING_HABITS": {
                "prompt": "Describe los hábitos que quieres cambiar o mejorar:",
                "placeholder": "Ej: Como muy rápido y no mastico bien...",
                "examples": ["Ansiedad por comer", "Horarios irregulares", "Comer emocional"]
            },
            "QUICK_QUESTION": {
                "prompt": "¿Cuál es tu pregunta específica sobre nutrición?",
                "placeholder": "Ej: ¿Puedo comer fruta en la noche?",
                "examples": ["¿Es malo el huevo?", "¿Cuánta agua debo tomar?", "¿Qué desayuno saludable?"]
            }
        }
        return consultation_data.get(consultation_type, consultation_data["QUICK_QUESTION"])

    async def _check_specialist_availability(self, specialty: str) -> Dict[str, Any]:
        """Check if nutrition specialists are available"""
        # TODO: Implement real availability check with Clivi API
        import random
        return {
            "available": random.choice([True, False]),
            "estimated_time": "5-10 min",
            "next_available": "15 minutos",
            "specialists_online": random.randint(1, 5)
        }
    
    async def _connect_to_nutrition_specialist(self, user_id: str, consultation_type: str, question: str) -> Dict[str, Any]:
        """Connect user to available nutrition specialist"""
        # TODO: Implement real specialist connection
        import random
        specialists = [
            {"name": "Dra. Ana López", "specialization": "Nutrición clínica"},
            {"name": "Lic. Carlos Mejía", "specialization": "Nutrición deportiva"},
            {"name": "Dra. Sofia Ruiz", "specialization": "Nutrición pediátrica"}
        ]
        selected = random.choice(specialists)
        
        return {
            "specialist_id": f"NUT-{random.randint(1000, 9999)}",
            "specialist_name": selected["name"],
            "specialization": selected["specialization"],
            "session_id": f"SESSION-{user_id}-{random.randint(100, 999)}"
        }
        
        if not question:
            return {
                "action": "nutrition_hotline_menu",
                "message": "Línea directa de nutrición 🥗 ¿En qué te podemos ayudar?",
                "options": [
                    {
                        "id": "QUICK_QUESTION",
                        "title": "Pregunta rápida",
                        "description": "Consulta específica sobre alimentación ❓",
                        "response_time": "2-4 horas"
                    },
                    {
                        "id": "MEAL_DOUBT",
                        "title": "Duda sobre comida",
                        "description": "¿Puedo comer esto? Análisis de alimentos 🤔",
                        "response_time": "1-2 horas"
                    },
                    {
                        "id": "EMERGENCY_NUTRITION",
                        "title": "Consulta urgente",
                        "description": "Situación que requiere atención inmediata ⚡",
                        "response_time": "30 minutos"
                    },
                    {
                        "id": "PLAN_ADJUSTMENT",
                        "title": "Ajuste de plan",
                        "description": "Modificar plan nutricional actual 📋",
                        "response_time": "24 horas"
                    }
                ]
            }
        
        # Process nutrition question
        ticket_result = await self._create_nutrition_ticket(user_id, question, urgency)
        
        # Provide immediate AI assistance while waiting for nutritionist
        ai_response = await self._get_nutrition_ai_response(question)
        
        return {
            "action": "nutrition_response",
            "ticket_id": ticket_result["ticket_id"],
            "estimated_response": ticket_result["estimated_response"],
            "immediate_ai_help": ai_response,
            "message": f"Tu consulta ha sido enviada al equipo de nutrición (Ticket: {ticket_result['ticket_id']})",
            "next_actions": [
                {"id": "ASK_ANOTHER", "title": "Otra pregunta"},
                {"id": "TRACK_TICKET", "title": "Seguir consulta"},
                {"id": "EMERGENCY_CONTACT", "title": "Contacto urgente"},
                {"id": "MAIN_MENU", "title": "Menú principal"}
            ]
        }
    
    @tool
    async def sports_medicine_appointment_flow(self, user_id: str, action: str = None) -> Dict[str, Any]:
        """
        Sports medicine appointment management.
        Based on obesity-specific appointment flows.
        """
        context = self.get_session_context(user_id)
        context.current_flow = "sports_medicine_appointments"
        
        if not action:
            return {
                "action": "menu",
                "message": "Medicina deportiva - ¿Qué necesitas?",
                "options": [
                    {
                        "id": "SCHEDULE_EVAL",
                        "title": "Evaluación inicial",
                        "description": "Primera cita de medicina deportiva 🏥"
                    },
                    {
                        "id": "FOLLOW_UP",
                        "title": "Cita de seguimiento", 
                        "description": "Control de progreso 📊"
                    },
                    {
                        "id": "INJURY_CONSULT",
                        "title": "Consulta por lesión",
                        "description": "Evaluación de lesión o dolor 🩹"
                    },
                    {
                        "id": "PERFORMANCE_EVAL",
                        "title": "Evaluación de rendimiento",
                        "description": "Optimización deportiva ⚡"
                    }
                ]
            }
        
        return await self._handle_sports_medicine_action(user_id, action)
    
    @tool
    async def progress_report_flow(self, user_id: str, report_type: str = "complete",
                                 period: str = "month") -> Dict[str, Any]:
        """
        Progress report generation for obesity management.
        """
        context = self.get_session_context(user_id)
        context.current_flow = "progress_report"
        
        # Generate comprehensive progress report
        report_data = await self._generate_progress_report(user_id, report_type, period)
        
        return {
            "action": "progress_report",
            "report_type": report_type,
            "period": period,
            "summary": {
                "weight_change": report_data.get("weight_change"),
                "measurements_change": report_data.get("measurements_change"),
                "workout_adherence": report_data.get("workout_adherence"),
                "goals_achieved": report_data.get("goals_achieved")
            },
            "charts": report_data.get("charts", []),
            "achievements": report_data.get("achievements", []),
            "recommendations": report_data.get("recommendations", []),
            "next_goals": report_data.get("next_goals", []),
            "export_options": [
                {"format": "PDF", "action": "EXPORT_PDF"},
                {"format": "Compartir", "action": "SHARE_PROGRESS"},
                {"format": "Imprimir", "action": "PRINT_REPORT"}
            ]
        }
    
    # Helper methods
    async def _process_weight_measurement(self, user_id: str, weight: float) -> Dict[str, Any]:
        """Process weight measurement submission"""
        measurement_id = f"WEIGHT-{user_id[-4:]}-{hash(str(weight)) % 10000:04d}"
        self.logger.info(f"Processing weight measurement: {weight} kg")
        return {"measurement_id": measurement_id, "status": "success"}
    
    async def _calculate_weight_progress(self, user_id: str, current_weight: float) -> Dict[str, Any]:
        """Calculate weight progress and trends"""
        # TODO: Get historical data from Clivi API
        return {
            "change_since_last": -0.5,  # kg
            "change_since_start": -3.2,  # kg
            "trend": "decreasing",
            "goal_progress": 65.4  # percentage
        }
    
    def _get_motivational_message(self, progress_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate motivational message based on progress"""
        if progress_data.get("change_since_last", 0) < 0:
            return {
                "type": "positive",
                "message": "¡Excelente progreso! Cada paso cuenta hacia tu meta 🌟",
                "emoji": "🎉"
            }
        elif progress_data.get("change_since_last", 0) == 0:
            return {
                "type": "encouraging",
                "message": "Mantener el peso también es un logro. ¡Sigue así! 💪",
                "emoji": "⚖️"
            }
        else:
            return {
                "type": "supportive",
                "message": "No te desanimes, los cambios toman tiempo. ¡Tú puedes! 💪",
                "emoji": "🌱"
            }
    
    def _get_measurement_instructions(self, measurement_type: str) -> List[str]:
        """Get measurement instructions by type"""
        instructions = {
            "WAIST": [
                "Mide en el punto más estrecho del torso",
                "Mantén la cinta horizontal",
                "No aprietes demasiado la cinta",
                "Mide después de exhalar suavemente"
            ],
            "HIP": [
                "Mide en la parte más ancha de las caderas",
                "Mantente de pie con pies juntos",
                "La cinta debe estar horizontal",
                "No comprimas el tejido"
            ],
            "NECK": [
                "Mide justo debajo de la nuez de Adán",
                "Mantén la cabeza erguida",
                "La cinta debe estar cómoda, no apretada",
                "Mide en el mismo lugar siempre"
            ]
        }
        return instructions.get(measurement_type, [])
    
    async def _process_body_measurement(self, user_id: str, measurement_type: str, 
                                      value: float) -> Dict[str, Any]:
        """Process body measurement submission"""
        measurement_id = f"{measurement_type}-{user_id[-4:]}-{hash(str(value)) % 10000:04d}"
        
        # Generate health insights based on measurement
        insights = self._generate_measurement_insights(measurement_type, value)
        
        return {
            "measurement_id": measurement_id,
            "status": "success",
            "insights": insights
        }
    
    def _generate_measurement_insights(self, measurement_type: str, value: float) -> List[str]:
        """Generate health insights for measurements"""
        # Simplified insight generation
        insights = []
        if measurement_type == "WAIST" and value > 88:  # Example threshold for women
            insights.append("Considera enfocarte en ejercicios para reducir cintura")
        return insights
    
    async def _process_workout_signup(self, user_id: str, category: str, level: str) -> Dict[str, Any]:
        """Process workout program signup"""
        # TODO: Integrate with Clivi workout management system
        return {
            "plan": f"Plan {category} - Nivel {level}",
            "schedule": "Lunes, Miércoles, Viernes",
            "next_session": "Mañana 8:00 AM",
            "trainer": "Ana García - Especialista en obesidad"
        }
    
    async def _create_nutrition_ticket(self, user_id: str, question: str, urgency: str) -> Dict[str, Any]:
        """Create nutrition consultation ticket"""
        ticket_id = f"NUT-{user_id[-4:]}-{hash(question) % 10000:04d}"
        
        response_times = {
            "normal": "2-4 horas",
            "urgent": "30 minutos",
            "emergency": "15 minutos"
        }
        
        return {
            "ticket_id": ticket_id,
            "estimated_response": response_times.get(urgency, "2-4 horas")
        }
    
    async def _get_nutrition_ai_response(self, question: str) -> Dict[str, Any]:
        """Get immediate AI nutrition response while waiting for nutritionist"""
        # TODO: Integrate with nutrition AI model
        return {
            "type": "ai_assistance",
            "message": "Mientras esperas la respuesta del nutriólogo, aquí tienes información general...",
            "disclaimer": "Esta es información general. Espera la respuesta personalizada de tu nutriólogo."
        }
    
    async def _handle_sports_medicine_action(self, user_id: str, action: str) -> Dict[str, Any]:
        """Handle sports medicine appointment actions"""
        # TODO: Implement specific sports medicine appointment logic
        return {
            "action": "appointment_scheduling",
            "specialty": "sports_medicine",
            "appointment_type": action
        }
    
    async def _generate_progress_report(self, user_id: str, report_type: str, period: str) -> Dict[str, Any]:
        """Generate comprehensive progress report"""
        # TODO: Integrate with Clivi analytics and progress tracking
        return {
            "weight_change": -2.3,  # kg
            "measurements_change": {
                "waist": -3.5,  # cm
                "hip": -2.1,    # cm
                "neck": -0.5    # cm
            },
            "workout_adherence": 87.5,  # percentage
            "goals_achieved": 3,
            "achievements": [
                "Lost 2kg this month! 🎉",
                "Completed 15 workouts 💪",
                "Reduced waist by 3.5cm 📏"
            ],
            "recommendations": [
                "Increase protein intake",
                "Add 1 more cardio session per week",
                "Focus on strength training"
            ]
        }
