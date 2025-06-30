# Análisis de Intents, EntityTypes, Webhooks y Tools

## Resumen Ejecutivo

Se analizaron los intents, entidades, webhooks y herramientas de ambos agentes exportados desde Conversational Agents para identificar patrones, funcionalidades y mapeo hacia agentes ADK.

---

## 1. ANÁLISIS DE INTENTS

### Diabetes Agent - Intents Principales
**Total de intents**: ~174 intents identificados

#### Categorías principales:

**📅 Gestión de Citas**
- `DIABETES_ENDO` - Agendamiento endocrinólogo
- `NUTRITION` / `NUTRI_RESCHEDULE_APPT` / `NUTRI_SCHEDULE_APPT`
- `PSYCHOLOGIST` / `PSYCHO_RESCHEDULE_APPT` / `PSYCHO_SCHEDULE_APPT`
- `APPOINTMENTS_MAIN_MENU_PAGE` / `RESCHECHULE_APPTS_MENU`
- `CONFIRM_APPTS_TEMPLATE_REMINDER`

**🩺 Monitoreo de Salud**
- `LOG_GLUCOSE` / `LOG_GLUCOSE_TEMPLATE_PAGE`
- `FASTING` / `POST_MEAL` (medición glucosa)
- `WEIGHT_LOG_PAGE_AND_TEMPLATE`
- `WAIST_CIRCUMFERENCE_LOG_TEMPLATE_PAGE`
- `LOG_BODY_MEASUREMENTS_TEMPLATE_MAIN_MENU_PAGE`

**💊 Medicamentos y Suministros**
- `CONFIRM_MED_REMINDER`
- `MEDS_SUPPLIES_STATUS_MAIN_PAGE`
- `OZEMPIC` / `SAXENDA` / `WEGOVY` (medicamentos GLP)
- `GLP_TUTORIAL` / `INYEC_DATE_GLP`

**📊 Reportes y Resultados**
- `GLUCOSE_REPORT_TEMPLATE_PAGE`
- `LAST_LABS_RESULTS_BUTTON_PAGE`
- `LAST_PRESCRIPTION_BUTTON_PAGE`
- `MEASUREMENTS_REPORT_MAIN_MENU_PAGE`

**🤖 IA y Soporte**
- `AI_AGENT_CALLING_MAIN_MENU`
- `Ask OpenAI` functionality
- `HIGH_SPECIALIZATION_QUESTION_TAG`

**💳 Pagos y Facturación**
- `INVOICE_PAGE_TEMPLATE` / `INVOICE_LABS_MAIN_MENU_PAGE`
- `PAYMENTS_ISSUES` / `UPDATE_PAYMENT`
- `OFFLINE_PAYMENTS`

### Obesity Agent - Intents Principales
**Total de intents**: ~189 intents identificados

#### Diferencias clave vs Diabetes:

**🏃‍♀️ Ejercicio y Medicina Deportiva**
- `SPORTS_MEDICINE_NO_SHOW`
- `Encuesta de ejercicios`
- `PX_ADHERENCIA_SPORT_MAS75` / `PX_ADHERENCIA_SPORT_MENOS75`
- `WORKOUT_FLOW_BEGINNING`

**⚖️ Monitoreo de Peso Especializado**
- `WEIGHT_LOG` / `WEIGHT_LOG_PAGE_AND_TEMPLATE`
- `PHOTO_SCALE` (fotos de báscula)
- `NECK_LOG_PAGE_AND_TEMPLATE`

**🎯 Especialización en Obesidad**
- `OBESITY` / `OBESITY_QA` / `OBESITY_SURVEY`
- `OBESITY_RESCHEDULE_APPT` / `SCHEDULE_OBESITY`
- `LOW_IMPACT_ENROLL` / `LOW_IMPACT_LEVEL`

**👨‍⚕️ Especialistas Adicionales**
- `AVAILABLE_FOR_SPECIALIST` / `LATER_FOR_SPECIALIST`
- `SPECIALIST_REASON`

---

## 2. ANÁLISIS DE ENTITY TYPES

### Estructura de Entidades
- **Tipo**: `KIND_MAP` (entidades de mapeo)
- **Idioma**: Español (`es`)
- **Formato**: Valor + sinónimos

### Entidades Clave Identificadas:

**📅 Gestión de Citas**
- `DIABETES_ENDO` - Endocrinología diabetes
- `APPOINTMENTS_*` - Múltiples entidades de citas
- `RESCHEDULE_*` - Reagendamiento

**🏥 Especialidades Médicas**
- `NUTRI_*` - Nutrición
- `PSYCHO_*` - Psicología
- Especialidades por condición

**📊 Mediciones y Datos**
- `FASTING` / `POST_MEAL` - Tipos de medición
- `MEASUREMENTS_*` - Mediciones corporales

**💊 Medicamentos**
- `GLP_*` - Medicamentos GLP-1
- `SIDE_EFFECTS` - Efectos secundarios

---

## 3. ANÁLISIS DE WEBHOOKS

### Webhooks Identificados:

**📸 Procesamiento de Imágenes**
- **Nombre**: `photoScalePhoto`
- **Endpoint**: `https://n8n.clivi.com.mx/webhook/imgfile-measurement-recognition`
- **Método**: POST
- **Función**: Reconocimiento de mediciones en imágenes
- **Timeout**: 5 segundos
- **Autenticación**: Ninguna

### Estructura del Request:
```json
{
  "mime_type": "image/jpeg",
  "image-file": "$session.params.image.sha256"
}
```

---

## 4. ANÁLISIS DE TOOLS

### Tools del Diabetes Agent:

**📨 SEND_MESSAGE**
- **Función**: Envío de mensajes template
- **Input**: `templateName`, `actionType`, `type`
- **Output**: `success` boolean

**🤖 Ask OpenAI**
- **Función**: Consultas a IA generativa
- **Input**: `userRequest`, `context`, `functionName`
- **Output**: `success` boolean

**📅 APPOINTMENT_CONFIRM**
- **Función**: Confirmación de citas

**🔗 ONBOARDING_SEND_LINK**
- **Función**: Envío de enlaces de onboarding

**⚙️ PROPERTY_UPDATER**
- **Función**: Actualización de propiedades

**💬 QUESTION_SET_LAST_MESSAGE**
- **Función**: Gestión de último mensaje

### Tools del Obesity Agent:
- **Mismas tools base** + `DR_CLIVI_HOW_IT_WORKS`

---

## 5. MAPEO A ADK

### Arquitectura Propuesta:

```python
# dr_clivi/agents/base_agent.py
class BaseCliviAgent:
    """Agente base con funcionalidades comunes"""
    
    tools = [
        "send_template_message",
        "ask_generative_ai", 
        "appointment_manager",
        "measurement_logger",
        "image_processor"
    ]

# dr_clivi/agents/diabetes_agent.py  
class DiabetesAgent(BaseCliviAgent):
    """Agente especializado en diabetes"""
    
    specialized_tools = [
        "glucose_logger",
        "medication_reminder", 
        "endocrinology_scheduler",
        "glp_medication_tracker"
    ]
    
    intents = [
        "log_glucose_fasting",
        "log_glucose_post_meal", 
        "schedule_endocrinology",
        "medication_adherence",
        "glucose_report_request"
    ]

# dr_clivi/agents/obesity_agent.py
class ObesityAgent(BaseCliviAgent):
    """Agente especializado en obesidad"""
    
    specialized_tools = [
        "weight_logger",
        "exercise_tracker",
        "sports_medicine_scheduler", 
        "body_measurement_analyzer"
    ]
    
    intents = [
        "log_weight",
        "exercise_adherence",
        "schedule_obesity_consultation",
        "body_measurement_report"
    ]
```

### Herramientas ADK a Implementar:

**🖼️ Image Processing Tool**
```python
# Migrar webhook photoScalePhoto
@tool
def process_scale_image(image_data: str) -> dict:
    """Procesa imágenes de báscula para extraer mediciones"""
    # Integrar con n8n.clivi.com.mx endpoint
    pass
```

**📨 Template Message Tool**
```python
@tool  
def send_template_message(template_name: str, user_id: str) -> bool:
    """Envía mensajes template vía WhatsApp"""
    # Integrar con Twilio/WhatsApp Business API
    pass
```

**🤖 Generative AI Tool**
```python
@tool
def ask_generative_ai(user_request: str, context: str) -> str:
    """Consulta IA generativa para respuestas especializadas"""
    # Usar Vertex AI Gemini
    pass
```

---

## 6. PRIORIDADES DE MIGRACIÓN

### Fase 1: Core Functionality
1. ✅ **Agent Configuration** - Completado
2. 🔄 **Intent Recognition** - Mapear intents principales 
3. 🔄 **Template Messaging** - Tool SEND_MESSAGE
4. 🔄 **Basic Logging** - Mediciones básicas

### Fase 2: Specialized Features  
1. 📋 **Image Processing** - Webhook photoScalePhoto
2. 📋 **Appointment Management** - Tools de citas
3. 📋 **Generative AI** - Ask OpenAI functionality
4. 📋 **Medication Tracking** - Diabetes específico

### Fase 3: Advanced Integration
1. 📋 **A2A Communication** - Entre agentes
2. 📋 **Analytics & Reporting** - Dashboards
3. 📋 **WhatsApp Business** - Integración completa
4. 📋 **Payment Processing** - Facturación

---

## 7. HALLAZGOS CLAVE

### Complejidad Identificada:
- **174-189 intents** por agente = Alta especialización
- **Múltiples especialidades** médicas integradas
- **Procesamiento de imágenes** avanzado
- **IA generativa** ya integrada
- **Sistema de templates** complejo

### Oportunidades ADK:
- **Código reutilizable** entre agentes  
- **A2A communication** nativa
- **Vertex AI** más potente que OpenAI integration
- **Mejor observabilidad** y debugging
- **Escalabilidad** mejorada

### Riesgos de Migración:
- **Pérdida de templates** específicos
- **Integración n8n** compleja
- **Training phrases** extensivo
- **Business logic** embebida en flujos

---

## 8. PRÓXIMOS PASOS

1. 🔄 **Analizar flows/** - Mapear flujos conversacionales
2. 📋 **Implementar BaseCliviAgent** - Funcionalidad común
3. 📋 **Crear herramientas core** - send_message, image_processor
4. 📋 **Migrar intents principales** - Por prioridad de uso
5. 📋 **Configurar A2A** - Comunicación entre agentes
