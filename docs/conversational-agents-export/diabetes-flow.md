# Flujo de Diabetes - Conversational Agents (ex-Dialogflow CX)

## Información General
- **Nombre del Flujo**: Diabetes Management
- **Propósito**: Gestión de diabetes, monitoreo de glucosa, educación
- **Proyecto**: dtwo-qa
- **Última actualización**: [FECHA]

## Intents Principales

### 1. Intent: glucose_reading
- **Training phrases**: 
  - "Mi glucosa está en 120"
  - "Tengo 180 de azúcar"
  - "Mi glucómetro marca 95"
  - "El nivel de azúcar es 250"
- **Parameters**:
  - glucose_level: @sys.number
  - unit: @sys.unit (mg/dL, mmol/L)
- **Response**: Procesando lectura de glucosa...

### 2. Intent: medication_question
- **Training phrases**:
  - "¿Cuándo debo tomar metformina?"
  - "Olvidé tomar mi insulina"
  - "¿Qué pasa si me salto una dosis?"
- **Parameters**:
  - medication_name: @medication_entity
- **Response**: Información sobre medicación...

### 3. Intent: diabetes_education
- **Training phrases**:
  - "¿Qué es la diabetes?"
  - "¿Cómo controlar la diabetes?"
  - "Síntomas de hipoglucemia"
- **Response**: Información educativa...

### 4. Intent: emergency_situation
- **Training phrases**:
  - "Me siento mareado"
  - "Tengo mucha sed y vómitos"
  - "No puedo bajar mi azúcar"
- **Response**: Derivación a emergencias...

## Pages/Estados del Flujo

### Page 1: Initial Assessment
- **Entry fulfillment**: "¡Hola! Soy Dr. Clivi, tu asistente para diabetes. ¿En qué puedo ayudarte hoy?"
- **Intent routes**:
  - glucose_reading → glucose_analysis_page
  - medication_question → medication_info_page
  - diabetes_education → education_page
  - emergency_situation → emergency_page

### Page 2: Glucose Analysis
- **Entry fulfillment**: "Procesando tu lectura de glucosa..."
- **Form parameters**:
  - glucose_level: required
  - measurement_time: optional
- **Conditional responses**:
  - Si glucose > 180: "Tu nivel está alto. Te recomiendo..."
  - Si glucose < 70: "⚠️ ALERTA: Hipoglucemia. Toma azúcar inmediatamente"
  - Si 70-180: "Tu nivel está en rango normal."

### Page 3: Medication Info
- **Entry fulfillment**: "Te ayudo con información sobre medicamentos..."
- **Intent routes**:
  - forgot_medication → forgot_dose_flow
  - medication_timing → timing_info

### Page 4: Education Page
- **Entry fulfillment**: "¿Sobre qué aspecto de la diabetes quieres aprender?"
- **Response variants**:
  - Información sobre diabetes tipo 1
  - Información sobre diabetes tipo 2
  - Complicaciones y prevención

### Page 5: Emergency Page
- **Entry fulfillment**: "⚠️ Detecté una situación que puede requerir atención médica urgente..."
- **Response**: "Contacta inmediatamente a tu médico o llama al 911..."

## Entities Personalizadas

### @medication_entity
- **Values**:
  - metformina
  - insulina
  - glibenclamida
  - januvia
  - jardiance

### @glucose_range_entity
- **Values**:
  - normal (70-140 mg/dL)
  - alto (>140 mg/dL)
  - bajo (<70 mg/dL)

## Webhooks/Integraciones

### Webhook: /process-glucose-reading
- **Trigger**: Cuando se captura glucose_level
- **Función**: 
  - Validar rango de glucosa
  - Calcular recomendaciones
  - Guardar en historial del paciente
- **Response**: JSON con recomendaciones

### Webhook: /get-patient-history
- **Trigger**: Al inicio de conversación
- **Función**:
  - Obtener historial médico
  - Verificar medicamentos actuales
  - Cargar preferencias del paciente

## Lógica Condicional

### Glucose Level Logic:
```
IF glucose_level < 70:
  RESPONSE = "⚠️ HIPOGLUCEMIA - Acción inmediata requerida"
  ACTION = trigger_emergency_protocol()

ELIF glucose_level > 300:
  RESPONSE = "⚠️ NIVEL CRÍTICO - Contacta a tu médico"
  ACTION = schedule_medical_consultation()

ELIF glucose_level > 180:
  RESPONSE = "Nivel alto - Revisa tu alimentación y medicación"
  ACTION = provide_management_tips()

ELSE:
  RESPONSE = "Nivel normal - ¡Excelente control!"
  ACTION = provide_encouragement()
```

## Responses Template

### Respuestas Estáticas:
- **Saludo**: "¡Hola! Soy Dr. Clivi, especializado en diabetes."
- **Despedida**: "Cuídate y recuerda monitorear tu glucosa regularmente."
- **Error**: "No entendí tu consulta. ¿Puedes reformularla?"

### Respuestas Dinámicas:
- **Glucose feedback**: Basado en el valor ingresado
- **Medication info**: Según el medicamento consultado
- **Emergency protocol**: Según síntomas reportados

## Métricas de Uso
- **Intent más frecuente**: glucose_reading (45%)
- **Intent menos usado**: emergency_situation (2%)
- **Tasa de finalización**: 78%
- **Puntos de abandono**: medication_info_page (12%)

## Pain Points Identificados
1. **Confusión en unidades**: Usuarios no especifican mg/dL vs mmol/L
2. **Información incompleta**: Falta contexto sobre horario de comida
3. **Emergencias no detectadas**: Algunos casos críticos no se escalaban
4. **Respuestas repetitivas**: Falta personalización basada en historial

## Mejoras Deseadas para ADK
1. **Mejor detección de emergencias** con ML
2. **Personalización** basada en historial del paciente
3. **Integración directa** con Clivi API
4. **Respuestas más naturales** con Gemini 2.5
5. **Multi-modal**: Soporte para imágenes de glucómetro
