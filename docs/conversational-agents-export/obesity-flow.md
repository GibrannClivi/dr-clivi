# Flujo de Obesidad - Conversational Agents (ex-Dialogflow CX)

## Información General
- **Nombre del Flujo**: Obesity Management
- **Propósito**: Gestión de peso, nutrición, planes de ejercicio
- **Proyecto**: dtwo-qa
- **Última actualización**: [FECHA]

## Intents Principales

### 1. Intent: weight_tracking
- **Training phrases**: 
  - "Peso 85 kilos"
  - "Mi peso actual es 70kg"
  - "Subí 2 kilos esta semana"
  - "Bajé 1.5 kg"
- **Parameters**:
  - weight: @sys.number
  - weight_unit: @sys.unit (kg, lb)
  - weight_change: @sys.number (opcional)
- **Response**: Registrando tu peso...

### 2. Intent: nutrition_question
- **Training phrases**:
  - "¿Qué debo comer para bajar de peso?"
  - "¿Cuántas calorías debo consumir?"
  - "¿Es malo comer carbohidratos?"
  - "Necesito un menú saludable"
- **Parameters**:
  - nutrition_topic: @nutrition_entity
- **Response**: Información nutricional personalizada...

### 3. Intent: exercise_planning
- **Training phrases**:
  - "¿Qué ejercicios me recomiendas?"
  - "Quiero empezar a hacer ejercicio"
  - "¿Cuánto debo caminar al día?"
  - "Rutina para principiantes"
- **Parameters**:
  - fitness_level: @fitness_level_entity
  - exercise_type: @exercise_entity
- **Response**: Plan de ejercicios personalizado...

### 4. Intent: calculate_bmi
- **Training phrases**:
  - "¿Cuál es mi IMC?"
  - "Calcular índice de masa corporal"
  - "Mido 1.70 y peso 80kg"
- **Parameters**:
  - height: @sys.number
  - height_unit: @sys.unit (cm, m, ft)
  - weight: @sys.number
- **Response**: Calculando tu IMC...

### 5. Intent: motivation_support
- **Training phrases**:
  - "No puedo bajar de peso"
  - "Me desanimé con la dieta"
  - "Necesito motivación"
  - "Quiero rendirme"
- **Response**: Apoyo emocional y motivacional...

## Pages/Estados del Flujo

### Page 1: Initial Assessment
- **Entry fulfillment**: "¡Hola! Soy Dr. Clivi, tu coach de peso saludable. ¿Cómo puedo ayudarte hoy?"
- **Intent routes**:
  - weight_tracking → weight_analysis_page
  - nutrition_question → nutrition_guidance_page
  - exercise_planning → exercise_plan_page
  - calculate_bmi → bmi_calculation_page
  - motivation_support → motivation_page

### Page 2: Weight Analysis
- **Entry fulfillment**: "Registrando tu peso actual..."
- **Form parameters**:
  - weight: required
  - height: required (si es primera vez)
  - target_weight: optional
- **Conditional responses**:
  - Si BMI > 30: "Tu IMC indica obesidad. Vamos a crear un plan..."
  - Si BMI 25-30: "Tienes sobrepeso. Te ayudo a alcanzar tu peso ideal..."
  - Si BMI 18.5-25: "Tu peso está en rango normal. ¿Quieres mantenerlo?"

### Page 3: Nutrition Guidance
- **Entry fulfillment**: "Te ayudo con tu alimentación saludable..."
- **Form parameters**:
  - dietary_restrictions: optional
  - preferred_foods: optional
  - daily_calories: optional
- **Intent routes**:
  - meal_planning → meal_plan_page
  - calorie_counting → calorie_tracker_page

### Page 4: Exercise Plan
- **Entry fulfillment**: "Creemos un plan de ejercicios para ti..."
- **Form parameters**:
  - fitness_level: required
  - available_time: required
  - preferred_activities: optional
- **Conditional responses**:
  - Si fitness_level = "beginner": Plan básico 3x semana
  - Si fitness_level = "intermediate": Plan 4-5x semana
  - Si fitness_level = "advanced": Plan intensivo

### Page 5: BMI Calculation
- **Entry fulfillment**: "Calculando tu índice de masa corporal..."
- **Form parameters**:
  - height: required
  - weight: required
- **Response calculation**: BMI = weight(kg) / height(m)²

### Page 6: Motivation Page
- **Entry fulfillment**: "Entiendo que puedes sentirte desanimado/a..."
- **Response variants**:
  - Mensajes de motivación personalizados
  - Recordatorio de objetivos
  - Celebración de pequeños logros
  - Técnicas de manejo de ansiedad

## Entities Personalizadas

### @nutrition_entity
- **Values**:
  - carbohidratos
  - proteínas
  - grasas
  - calorías
  - vitaminas
  - fibra

### @fitness_level_entity
- **Values**:
  - principiante
  - intermedio
  - avanzado
  - sedentario

### @exercise_entity
- **Values**:
  - caminar
  - correr
  - natación
  - yoga
  - pesas
  - cardio

### @bmi_category_entity
- **Values**:
  - bajo_peso (<18.5)
  - normal (18.5-24.9)
  - sobrepeso (25-29.9)
  - obesidad (≥30)

## Webhooks/Integraciones

### Webhook: /calculate-bmi
- **Trigger**: Cuando se capturan height y weight
- **Función**: 
  - Calcular BMI
  - Determinar categoría de peso
  - Generar recomendaciones
- **Response**: JSON con BMI y categoría

### Webhook: /generate-meal-plan
- **Trigger**: nutrition_guidance intent
- **Función**:
  - Crear plan de comidas personalizado
  - Calcular calorías necesarias
  - Considerar restricciones dietéticas
- **Response**: Plan de menús semanal

### Webhook: /track-progress
- **Trigger**: weight_tracking intent
- **Función**:
  - Guardar peso en historial
  - Calcular tendencia de pérdida/ganancia
  - Generar gráficos de progreso
- **Response**: Análisis de progreso

## Lógica Condicional

### BMI Classification Logic:
```
IF BMI < 18.5:
  CATEGORY = "Bajo peso"
  RECOMMENDATION = "Consulta con nutricionista para ganar peso saludablemente"

ELIF BMI >= 18.5 AND BMI < 25:
  CATEGORY = "Peso normal"
  RECOMMENDATION = "¡Excelente! Mantén tu peso actual con alimentación balanceada"

ELIF BMI >= 25 AND BMI < 30:
  CATEGORY = "Sobrepeso"
  RECOMMENDATION = "Te ayudo a perder peso gradualmente"

ELSE: # BMI >= 30
  CATEGORY = "Obesidad"
  RECOMMENDATION = "Recomiendo plan estructurado y seguimiento médico"
```

### Weight Loss Progress Logic:
```
IF weight_change < 0: # Perdió peso
  IF weight_loss_rate > 2kg/semana:
    ALERT = "Pérdida muy rápida - consulta médico"
  ELSE:
    RESPONSE = "¡Excelente progreso! Continúa así"

ELIF weight_change > 0: # Ganó peso
  RESPONSE = "No te desanimes, analicemos qué pasó esta semana"

ELSE: # Sin cambio
  RESPONSE = "Peso estable. ¿Cómo te sientes con tu alimentación?"
```

## Responses Template

### Respuestas Estáticas:
- **Saludo**: "¡Hola! Soy Dr. Clivi, tu coach personal de peso saludable."
- **Motivación**: "Cada pequeño paso cuenta en tu camino hacia un peso saludable."
- **Error**: "No entendí. ¿Puedes decirme tu peso actual o tu pregunta sobre nutrición?"

### Respuestas Dinámicas:
- **BMI feedback**: Basado en el cálculo actual
- **Progress tracking**: Según la tendencia de peso
- **Meal suggestions**: Personalizadas por restricciones
- **Exercise recommendations**: Según nivel de fitness

## Calculadoras Integradas

### 1. Calculadora de Calorías Diarias:
- **Fórmula Hombres**: BMR = 88.362 + (13.397 × peso) + (4.799 × altura) - (5.677 × edad)
- **Fórmula Mujeres**: BMR = 447.593 + (9.247 × peso) + (3.098 × altura) - (4.330 × edad)
- **Factor actividad**: BMR × (1.2-1.9 según nivel)

### 2. Calculadora de Pérdida de Peso:
- **Déficit calórico**: 3500 cal = 0.45kg
- **Pérdida semanal segura**: 0.5-1kg
- **Meta calórica**: BMR - déficit deseado

## Métricas de Uso
- **Intent más frecuente**: weight_tracking (40%)
- **Intent popular**: nutrition_question (25%)
- **Intent menos usado**: motivation_support (8%)
- **Tasa de retención**: 65% (usuarios regresan)
- **Tiempo promedio sesión**: 4.2 minutos

## Pain Points Identificados
1. **Falta de personalización**: Respuestas muy genéricas
2. **Sin seguimiento**: No rastrea progreso a largo plazo
3. **Motivación limitada**: Mensajes repetitivos, no adaptativos
4. **Cálculos simples**: Falta considerar factores individuales
5. **Sin integración médica**: No conecta con datos de salud

## Mejoras Deseadas para ADK
1. **Seguimiento inteligente** con ML para detectar patrones
2. **Personalización avanzada** basada en historial completo
3. **Integración con wearables** (Fitbit, Apple Health)
4. **Coaching adaptativo** que aprende del usuario
5. **Planes de comida dinámicos** con IA generativa
6. **Soporte emocional** más sofisticado para motivación
7. **Alertas inteligentes** para check-ins proactivos
