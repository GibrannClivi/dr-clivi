# Análisis de Flows - Flujos Conversacionales

## Resumen Ejecutivo

Se analizaron los flows de ambos agentes exportados desde Conversational Agents para entender la arquitectura de flujos conversacionales y su mapeo hacia agentes ADK.

---

## 1. ESTRUCTURA DE FLOWS

### Diabetes Agent - Flows Identificados
1. **Default Start Flow** - Flujo de entrada principal
2. **checkPlanStatus** - Verificación de estado del plan del paciente
3. **diabetesPlans** - Menú principal para pacientes con diabetes
4. **clubPlan** - Funcionalidades específicas del plan Club
5. **helpDeskSubMenu** - Submenú de ayuda y soporte
6. **highSpecializationQuestionTag** - Preguntas de alta especialización
7. **leadInterested** - Gestión de leads interesados
8. **nutritionQuestionTag** - Preguntas específicas de nutrición
9. **presentComplaintTag** - Presentación de quejas
10. **psychoQuestionTag** - Preguntas de psicología
11. **suggestionsFlowCatcher** - Capturador de sugerencias
12. **suppliesQuestionTag** - Preguntas sobre suministros médicos
13. **END_SESSION** - Flujo de finalización de sesión

### Obesity Agent - Flows Identificados
1. **Default Start Flow** - Flujo de entrada principal (similar)
2. **checkPlanStatus** - Verificación de estado del plan
3. **obesityPlan** - Menú principal para pacientes con obesidad
4. **helpDeskSubMenu** - Submenú de ayuda
5. **highSpecializationQuestionTag** - Preguntas especializadas
6. **leadInterested** - Gestión de leads
7. **nutritionHotLine** - Línea directa de nutrición
8. **nutritionQuestionTag** - Preguntas de nutrición
9. **presentComplaintTag** - Quejas
10. **psychoQuestionTag** - Preguntas psicológicas
11. **savesParameters** - Guardado de parámetros
12. **suggestionsFlowCatcher** - Capturador de sugerencias
13. **workoutSignUpCategory** - Categorías de suscripción a ejercicios
14. **END_SESSION** - Finalización de sesión

---

## 2. ANÁLISIS DE FLOW PRINCIPAL: DEFAULT START FLOW

### Estructura Common
```json
{
  "displayName": "Default Start Flow",
  "description": "A start flow created along with the agent",
  "transitionRoutes": [
    {
      "intent": "keyWordMainMenu",
      "targetFlow": "checkPlanStatus"
    },
    {
      "intent": "END_SESSION_TEMPLATE", 
      "targetFlow": "checkPlanStatus"
    }
  ],
  "eventHandlers": [
    {
      "event": "sys.no-match-default",
      "targetPlaybook": "MASTER_AGENT"
    },
    {
      "event": "sys.no-input-default",
      "targetPage": "End Session"
    }
  ]
}
```

### NLU Settings
- **Model Type**: `MODEL_TYPE_ADVANCED`
- **Classification Threshold**: 0.3
- **Language**: Español (es)

---

## 3. ANÁLISIS DE FLOW CRÍTICO: checkPlanStatus

### Funcionalidad
Flow de verificación y enrutamiento basado en el plan del paciente y su estado.

### Lógica de Enrutamiento por Plan
```javascript
// Condiciones de enrutamiento identificadas:

// Plan PRO activo/suspendido
$session.params.userContext.patient.plan = "PRO" 
AND ($session.params.userContext.patient.planStatus = "ACTIVE" 
OR $session.params.userContext.patient.planStatus = "SUSPENDED")
→ targetFlow: "diabetesPlans" (diabetes) / "obesityPlan" (obesity)

// Plan PLUS activo/suspendido
$session.params.userContext.patient.plan = "PLUS"
AND (planStatus = "ACTIVE" OR planStatus = "SUSPENDED")  
→ targetFlow: "diabetesPlans" / "obesityPlan"

// Plan CLUB activo/suspendido
$session.params.userContext.patient.plan = "CLUB"
AND (planStatus = "ACTIVE" OR planStatus = "SUSPENDED")
→ targetFlow: "clubPlan"

// Plan BASIC activo/suspendido
$session.params.userContext.patient.plan = "BASIC"
AND (planStatus = "ACTIVE" OR planStatus = "SUSPENDED")
→ targetFlow: "diabetesPlans" / "obesityPlan"

// Usuario desconocido
$session.params.userContext = "UNKNOWN"
→ targetPage: "userProblems"

// Plan CLUB cancelado
$session.params.userContext.patient.plan = "CLUB" 
AND planStatus = "CANCELED"
→ targetPage: "clubCanceledPlan"
```

---

## 4. ANÁLISIS DE PÁGINAS: mainMenu

### Estructura del Menú Principal (Diabetes)
```json
{
  "bodyText": "Hola $session.params.userContext.patient.nameDisplay, por favor utiliza el menú de opciones.",
  "sections": [
    {
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
    }
  ]
}
```

### Páginas de Diabetes Agent (49 páginas)
- **Citas**: `appointmentNew`, `appointmentReschedule`, `appointmentShowCancelList`, `apptsMenu`
- **Mediciones**: `glucoseValueLogFasting`, `glucoseValueLogPostMeal`, `logWeight`, `logWaist`, `logNeck`, `measurementsMenu`
- **Adherencia**: `adherenceDiabetes`, `adherenceNutri`, `adherencePsycho`
- **Facturación**: `invoiceLabsMenu`, `invoicingCenter`, `offlinePayments`
- **Medicamentos**: `medsSuppliesStatus`, `tutorialMed`
- **Evaluación**: `ratingsDiabetesAppt`, `ratingsNutritionAppt`, `ratingsPsychoAppt`

---

## 5. DIFERENCIAS CLAVE: Diabetes vs Obesity

### Flujos Únicos de Diabetes
- **clubPlan** - Plan específico de club de diabetes
- **suppliesQuestionTag** - Preguntas sobre suministros (glucómetro, tiras)

### Flujos Únicos de Obesity
- **nutritionHotLine** - Línea directa de nutrición
- **workoutSignUpCategory** - Categorías de ejercicios
- **savesParameters** - Guardado de parámetros específicos

### Páginas Específicas de Diabetes
- **glucoseValueLogFasting/PostMeal** - Medición de glucosa
- **tutorialMed** - Tutoriales de medicamentos GLP
- **medsSuppliesStatus** - Estado de suministros médicos

### Páginas Específicas de Obesity
- **workoutSignUpCategory** - Suscripción a ejercicios
- Enfoque en mediciones de peso y circunferencias

---

## 6. MAPEO A ARQUITECTURA ADK

### Flujos Base Comunes
```python
# dr_clivi/flows/base_flows.py
class BaseCliviFlow:
    """Flujo base común para ambos agentes"""
    
    def start_flow(self):
        """Default Start Flow → checkPlanStatus"""
        pass
    
    def check_plan_status(self):
        """Verificación de plan y enrutamiento"""
        pass
    
    def help_desk_submenu(self):
        """Menú de ayuda común"""
        pass
    
    def present_complaint(self):
        """Flujo de quejas común"""
        pass
    
    def end_session(self):
        """Finalización de sesión"""
        pass

# dr_clivi/flows/diabetes_flows.py
class DiabetesFlows(BaseCliviFlow):
    """Flujos específicos de diabetes"""
    
    def diabetes_plans_menu(self):
        """Menú principal de diabetes"""
        pass
    
    def glucose_logging_flow(self):
        """Flujo de logging de glucosa"""
        pass
    
    def medication_tutorial_flow(self):
        """Tutorial de medicamentos"""
        pass
    
    def supplies_status_flow(self):
        """Estado de suministros"""
        pass

# dr_clivi/flows/obesity_flows.py  
class ObesityFlows(BaseCliviFlow):
    """Flujos específicos de obesidad"""
    
    def obesity_plan_menu(self):
        """Menú principal de obesidad"""
        pass
    
    def workout_signup_flow(self):
        """Suscripción a ejercicios"""
        pass
    
    def nutrition_hotline_flow(self):
        """Línea directa nutrición"""
        pass
```

### Gestión de Estado de Sesión
```python
# Estado de sesión identificado
session_params = {
    "userContext": {
        "patient": {
            "nameDisplay": str,
            "plan": ["PRO", "PLUS", "CLUB", "BASIC"],
            "planStatus": ["ACTIVE", "SUSPENDED", "CANCELED"]
        }
    }
}
```

---

## 7. COMPONENTES TÉCNICOS CLAVE

### Event Handlers
- **sys.no-match-default** → `MASTER_AGENT` playbook
- **sys.no-input-default** → End Session
- **flow.failed** → `MASTER_AGENT` playbook

### Transition Route Groups
- **DEFAULT_CATCH** - Grupos de rutas por defecto
- **GLP_CATCHER** - Capturador específico de GLP (obesity)

### Advanced Settings
- **playbackInterruptionSettings** - Configuración de interrupciones
- **dtmfSettings** - Configuración DTMF para voz
- **useSystemEntityRule**: false

---

## 8. ARQUITECTURA ADK PROPUESTA

### Router/Coordinator Agent
```python
class DrCliviCoordinator:
    """Agente coordinador principal"""
    
    async def route_to_specialist(self, user_input: str, context: dict):
        """Enrutar a agente especializado basado en contexto"""
        
        user_context = context.get("userContext", {})
        patient = user_context.get("patient", {})
        plan = patient.get("plan")
        plan_status = patient.get("planStatus")
        
        if plan in ["PRO", "PLUS", "BASIC"] and plan_status in ["ACTIVE", "SUSPENDED"]:
            # Determinar especialidad basada en historial/contexto
            if self.is_diabetes_related(user_input):
                return await self.diabetes_agent.handle(user_input, context)
            elif self.is_obesity_related(user_input):
                return await self.obesity_agent.handle(user_input, context)
        elif plan == "CLUB":
            return await self.club_plan_handler.handle(user_input, context)
        elif user_context == "UNKNOWN":
            return await self.onboarding_agent.handle(user_input, context)
```

### Specialized Agents
```python
class DiabetesAgent(BaseCliviAgent):
    """Agente especializado en diabetes"""
    
    flows = {
        "main_menu": DiabetesMainMenuFlow,
        "glucose_logging": GlucoseLoggingFlow,
        "medication_tutorial": MedicationTutorialFlow,
        "supplies_management": SuppliesManagementFlow
    }

class ObesityAgent(BaseCliviAgent):
    """Agente especializado en obesidad"""
    
    flows = {
        "main_menu": ObesityMainMenuFlow, 
        "workout_signup": WorkoutSignupFlow,
        "nutrition_hotline": NutritionHotlineFlow,
        "weight_tracking": WeightTrackingFlow
    }
```

---

## 9. PLAN DE MIGRACIÓN

### Fase 1: Core Flows
1. ✅ **BaseCliviFlow** - Funcionalidad común
2. 🔄 **Start Flow** - Entrada y enrutamiento
3. 🔄 **Plan Status Check** - Verificación de planes
4. 🔄 **Main Menu** - Menús principales por especialidad

### Fase 2: Specialized Flows  
1. **Diabetes Flows**: Glucose logging, medication tutorials
2. **Obesity Flows**: Workout signup, nutrition hotline
3. **Common Flows**: Appointments, measurements, billing

### Fase 3: Advanced Features
1. **Master Agent Integration** - Fallback IA
2. **Event Handling** - Error recovery
3. **Session Management** - Estado persistente
4. **A2A Communication** - Entre agentes

---

## 10. HALLAZGOS CLAVE

### Complejidad Identificada
- **13 flows** por agente con múltiples páginas cada uno
- **Lógica de enrutamiento compleja** basada en planes
- **49 páginas** en diabetes agent con funcionalidades específicas
- **Estado de sesión rico** con contexto de paciente

### Oportunidades ADK
- **A2A routing** entre agentes especializados
- **State management** mejorado con Vertex AI
- **Flow reusability** entre agentes
- **Better error handling** con event handlers

### Riesgos de Migración
- **Business logic** embebida en conditions
- **UI components** específicos de WhatsApp
- **Session state** complejo a migrar
- **Plan-based routing** debe replicarse exactamente

---

## 11. PRÓXIMOS PASOS

1. 🔄 **Implementar BaseCliviAgent** - Clase base con flows comunes
2. 📋 **Crear Router/Coordinator** - Lógica de enrutamiento por plan
3. 📋 **Migrar Main Menu flows** - Menús principales
4. 📋 **Implementar session management** - Estado de contexto
5. 📋 **Setup A2A communication** - Entre agentes especializados

El análisis de flows revela una **arquitectura sofisticada** que requiere mapeo cuidadoso a ADK para preservar toda la lógica de negocio y experiencia de usuario existente.
