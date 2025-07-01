# 🏥 Dr. Clivi - Asistente Médico Multi-Agente

![Python](https://img.shields.io/badge/python-v3.11+-blue.svg)
![ADK](https://img.shields.io/badge/ADK-Ready-green.svg)
![WhatsApp](https://img.shields.io/badge/WhatsApp-Business%20API-25D366.svg)
![Telegram](https://img.shields.io/badge/Telegram-Bot%20API-0088CC.svg)
![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)

## 📋 Resumen

Dr. Clivi es un sistema avanzado de asistencia médica multi-agente construido para migrar desde Google Cloud Conversational Agents (ex-Dialogflow CX) a Google ADK (Agent Development Kit). El sistema proporciona atención especializada para diabetes y obesidad a través de múltiples canales (WhatsApp, Telegram), usando agentes especializados con inteligencia artificial y una arquitectura híbrida determinística + IA.

### 🚀 Características Principales

- 🤖 **Arquitectura Multi-Agente**: Agentes especializados para diabetes y obesidad
- 🔄 **Protocolo A2A**: Comunicación entre agentes para flujos complejos  
- 📱 **Multi-Canal**: Soporte nativo para WhatsApp Business API y Telegram Bot API
- � **Arquitectura Híbrida**: Combinación de flujos determinísticos y IA para respuestas precisas y flexibles
- �🏥 **Enfoque Médico**: Guías basadas en evidencia médica y soporte profesional
- ☁️ **Vertex AI Ready**: Optimizado para despliegue en Google Cloud
- 🔒 **Privacidad Médica**: Diseño que considera estándares de privacidad sanitaria
- 📊 **Analytics Avanzado**: Seguimiento de actividad y métricas de uso
- 🚨 **Manejo de Emergencias**: Detección automática y ruteo de situaciones médicas críticas

### 🏗️ Arquitectura del Sistema

```
Sistema Dr. Clivi
├── 🎯 DrCliviCoordinator (Enrutador Principal)
│   ├── Validación de plan de usuario
│   ├── Enrutamiento inteligente por especialidad
│   ├── Arquitectura híbrida (determinística + IA)
│   └── Manejo de usuarios desconocidos
│
├── 🩺 DiabetesAgent (Especialista en Diabetes)
│   ├── Registro de glucosa (ayunas/postprandial)
│   ├── Tutoriales de medicamentos GLP-1
│   ├── Citas con endocrinología
│   └── Reportes de mediciones
│
├── ⚖️ ObesityAgent (Especialista en Obesidad)
│   ├── Categorías de ejercicio personalizadas
│   ├── Línea directa nutricional
│   ├── Seguimiento de peso y medidas
│   └── Medicina deportiva
│
├── 🤖 Flujos Determinísticos
│   ├── Manejo de menús estructurados
│   ├── Navegación por botones inline
│   ├── Validación de entradas específicas
│   └── Gestión de contexto de sesión
│
└── 🔧 Capa de Integración Multi-Canal
    ├── WhatsApp Business API
    ├── Telegram Bot API (con webhooks)
    ├── n8n Webhooks (Plataforma Clivi)
    ├── Sistemas Clivi específicos
    └── Vertex AI
```

## 📱 Integración con Telegram

### 🔧 Configuración del Bot

Dr. Clivi incluye soporte completo para Telegram Bot API con arquitectura de webhooks para comunicación en tiempo real.

#### Características de Telegram:
- ✅ **Webhooks con HTTPS**: Integración segura usando ngrok para desarrollo
- ✅ **Botones Inline**: Navegación intuitiva con teclados estructurados
- ✅ **Manejo de Sesiones**: Contexto persistente durante las conversaciones
- ✅ **Respuestas Inmediatas**: Callback queries para interacción fluida
- ✅ **Manejo de Emergencias**: Detección automática y alertas críticas

#### Flujos Implementados:
- 🏠 **Menú Principal**: Navegación entre diabetes y obesidad
- 📊 **Registro de Mediciones**: Glucosa y peso con validación
- 📅 **Gestión de Citas**: Agendamiento y reprogramación
- 🆘 **Emergencias Médicas**: Detección y ruteo automático
- 🔄 **Navegación Contextual**: Botones de regreso y menú principal

### 🚀 Configuración para Desarrollo

1. **Crear Bot en Telegram**
   ```bash
   # Conversa con @BotFather en Telegram
   /newbot
   # Guarda el token en .env como TELEGRAM_BOT_TOKEN
   ```

2. **Configurar Webhooks con ngrok**
   ```bash
   # Instalar ngrok
   brew install ngrok  # macOS
   
   # Exponer puerto local
   ngrok http 8000
   
   # Configurar webhook
   curl -X POST https://api.telegram.org/bot{TOKEN}/setWebhook \
     -H "Content-Type: application/json" \
     -d '{"url": "https://tu-ngrok-url.ngrok.io/telegram/webhook"}'
   ```

3. **Ejecutar el Bot**
   ```bash
   # Instalar dependencias
   poetry install
   
   # Configurar variables de entorno
   export TELEGRAM_BOT_TOKEN="tu-token-aqui"
   export GOOGLE_AI_STUDIO_API_KEY="tu-api-key-aqui"
   
   # Ejecutar servidor
   poetry run python telegram_main.py
   ```

### 🏗️ Arquitectura Híbrida

El sistema implementa una arquitectura híbrida que combina:

#### 🤖 Flujos Determinísticos
- **Menús Estructurados**: Botones predefinidos para navegación
- **Validación de Entradas**: Reconocimiento de comandos específicos
- **Contexto de Sesión**: Mantenimiento de estado entre mensajes
- **Rutas Fijas**: Flujos predecibles para casos comunes

#### 🧠 IA Generativa (Fallback)
- **Procesamiento de Lenguaje Natural**: Para entradas no estructuradas
- **Análisis de Emergencias**: Detección inteligente de situaciones críticas
- **Respuestas Contextuales**: Cuando los flujos determinísticos no aplican
- **Escalación Inteligente**: Ruteo automático a especialistas

```python
# Ejemplo de lógica híbrida
def route_message(message):
    if is_deterministic_input(message):
        return handle_deterministic_flow(message)
    else:
        return route_to_ai_agent(message)
```

## 🚀 Inicio Rápido

### 📋 Prerrequisitos

- Python 3.11+
- Proyecto de Google Cloud con Vertex AI habilitado
- Poetry para gestión de dependencias
- Cuenta de WhatsApp Business (opcional para desarrollo)

### 💻 Instalación

1. **Clonar el repositorio**
   ```bash
   git clone https://github.com/GibrannClivi/dr-clivi.git
   cd dr-clivi
   ```

2. **Configurar el entorno**
   ```bash
   poetry install
   ```

3. **Configurar variables de entorno**
   ```bash
   cp .env.example .env
   # Editar .env con tus credenciales
   ```

4. **Ejecutar pruebas**
   ```bash
   poetry run python test_agents.py
   ```

### ⚙️ Configuración de Entorno

Copia `.env.example` a `.env` y configura:

```bash
# Google Cloud
GOOGLE_CLOUD_PROJECT=tu-proyecto-id
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_CLOUD_STORAGE_BUCKET=tu-bucket

# Google AI Studio
GOOGLE_AI_STUDIO_API_KEY=tu-api-key-ai-studio

# WhatsApp Business API
WHATSAPP_BUSINESS_API_URL=https://graph.facebook.com/v17.0
WHATSAPP_BUSINESS_TOKEN=tu-token
WHATSAPP_PHONE_ID=tu-phone-id

# Telegram Bot API
TELEGRAM_BOT_TOKEN=tu-bot-token
TELEGRAM_WEBHOOK_URL=https://tu-ngrok-url.ngrok.io/telegram/webhook

# Integración con Plataforma Clivi
# Nota: Clivi no tiene una API unificada. Se integra vía n8n webhooks y servicios específicos
CLIVI_N8N_WEBHOOK_BASE=https://n8n.clivi.com.mx/webhook
CLIVI_PATIENT_DATA_SOURCE=url-fuente-datos-pacientes
CLIVI_MEASUREMENT_STORAGE=url-almacenamiento-mediciones
CLIVI_APPOINTMENT_SYSTEM=url-sistema-citas

# A2A Protocol
A2A_REGISTRY_URL=https://registry.a2a.ai
A2A_AGENT_ID=dr-clivi-coordinator
A2A_SECRET_KEY=tu-secret-key

# Configuración de Flows
SESSION_TIMEOUT_MINUTES=30
NO_INPUT_TIMEOUT_SECONDS=300
ACTIVITY_LOGGING_ENABLED=true
```

## � Estructura del Proyecto

```
dr-clivi/
├── dr_clivi/                    # Código principal
│   ├── __init__.py
│   ├── config.py               # Configuración con Pydantic
│   ├── agents/                 # Implementación de agentes
│   │   ├── base_agent.py       # Clase base común
│   │   ├── coordinator.py      # Coordinador principal
│   │   ├── diabetes_agent.py   # Agente de diabetes
│   │   └── obesity_agent.py    # Agente de obesidad
│   ├── flows/                  # Flujos determinísticos
│   │   ├── deterministic_handler.py  # Lógica híbrida principal
│   │   └── pages/              # Páginas de interfaz
│   │       ├── appointment_pages.py  # Gestión de citas
│   │       ├── diabetes_pages.py     # Flujos de diabetes
│   │       └── obesity_pages.py      # Flujos de obesidad
│   ├── telegram/               # Integración Telegram
│   │   └── telegram_handler.py # Handler de webhooks y mensajes
│   └── tools/                  # Herramientas especializadas
│       ├── messaging.py        # WhatsApp Business API
│       ├── image_processing.py # Procesamiento de imágenes
│       └── generative_ai.py    # IA generativa fallback
├── telegram_main.py            # Servidor FastAPI para Telegram
├── docs/                       # Documentación
│   ├── analysis/              # Análisis de flujos exportados
│   ├── conversational-agents-export/  # Archivos exportados
│   └── implementation-summary.md      # Resumen ejecutivo
├── test_agents.py             # Suite de pruebas completa
├── pyproject.toml            # Configuración del proyecto
└── README.md
```

## 🏥 Funcionalidades por Especialidad

### 🩺 Gestión de Diabetes (`DiabetesAgent`)

- **📊 Monitoreo de Glucosa**
  - Registro de glucosa en ayunas y postprandial
  - Validación médica de rangos seguros (30-600 mg/dL)
  - Análisis de tendencias y retroalimentación personalizada
  - Recomendaciones basadas en historial del paciente

- **💊 Medicamentos GLP-1**
  - Tutoriales para Ozempic, Saxenda, Wegovy
  - Instrucciones de aplicación paso a paso
  - Videos y guías descargables

- **📈 Reportes y Análisis**
  - Reportes semanales/mensuales de glucosa
  - Estadísticas de control glucémico
  - Exportación en PDF y Excel

- **👩‍⚕️ Citas Médicas**
  - Agendamiento con endocrinólogos
  - Recordatorios de citas
  - Reagendamiento automático

### ⚖️ Gestión de Obesidad (`ObesityAgent`)

- **💪 Programas de Ejercicio**
  - Categorías: Cardio, Fuerza, Flexibilidad, HIIT, Bajo Impacto
  - Niveles: Principiante, Intermedio, Avanzado
  - Planes personalizados con duración e intensidad
  - Seguimiento de progreso y motivación

- **🥗 Línea Directa Nutricional**
  - Consultas en tiempo real con especialistas
  - Tipos: Plan alimentario, Control de porciones, Dietas especiales
  - Verificación de disponibilidad de especialistas
  - Alternativas con IA cuando no hay especialistas

- **� Seguimiento Corporal**
  - Registro de peso con validación por foto de báscula
  - Medidas corporales (cintura, cadera, cuello)
  - Análisis de tendencias de peso
  - Celebración de logros

- **🏃‍♀️ Medicina Deportiva**
  - Citas con especialistas en medicina deportiva
  - Evaluaciones de condición física
  - Planes de actividad personalizados

## 🔄 Flujos de Conversación Implementados

### Enrutamiento Principal (`checkPlanStatus`)
```
Usuario → Coordinador → Verificación de Plan
├── PRO/PLUS/BASIC + ACTIVO → Agente Especializado
├── CLUB + ACTIVO/SUSPENDIDO → Flujo Club
├── CLUB + CANCELADO → Reactivación Club
├── Cualquier + CANCELADO → Reactivación Plan
└── DESCONOCIDO → Flujo Problemas Usuario
```

### Menús Principales (SESSION_LIST)
- **Diabetes**: Citas, Mediciones, Reportes, Medicamentos, Suministros
- **Obesidad**: Citas, Peso, Medidas, Ejercicio, Nutrición, Progreso

### Manejo de Errores
- **No Match**: Enrutamiento a MASTER_AGENT (IA generativa)
- **No Input**: Timeout automático con resumen de sesión
- **Valores Críticos**: Alertas médicas y redirección a urgencias

## 🧪 Testing y Validación

### Ejecutar Suite de Pruebas
```bash
# Suite completa de agentes
poetry run python test_agents.py

# Servidor Telegram para pruebas en vivo
poetry run python telegram_main.py
```

**Incluye testing de**:
- ✅ Enrutamiento del coordinador por plan
- ✅ Flujos completos de diabetes (registro glucosa)
- ✅ Flujos completos de obesidad (ejercicio, nutrición)
- ✅ Manejo de errores y fallbacks
- ✅ Herramientas de mensajería WhatsApp
- ✅ Integración con Telegram Bot API
- ✅ Arquitectura híbrida determinística + IA
- ✅ Manejo de contexto de sesión
- ✅ Validaciones médicas críticas
- ✅ Webhooks y callbacks de Telegram

### Casos de Prueba Específicos
```python
# Usuario PRO con diabetes activo
await test_diabetes_glucose_flow()

# Usuario PLUS con obesidad - programa ejercicio
await test_obesity_workout_signup()

# Usuario CLUB cancelado - reactivación
await test_club_plan_reactivation()

# Valores críticos - alertas médicas
await test_critical_glucose_values()

# Flujos específicos de Telegram
telegram_test_flows = {
    "menu_navigation": "Navegación por botones inline",
    "measurement_input": "Registro de peso/glucosa con validación",
    "appointment_booking": "Gestión de citas médicas",
    "emergency_detection": "Detección automática de emergencias",
    "session_context": "Mantenimiento de contexto entre mensajes"
}
```

### 🔄 Pruebas en Tiempo Real con Telegram

1. **Configurar webhook**
   ```bash
   # Verificar estado del webhook
   curl https://api.telegram.org/bot{TOKEN}/getWebhookInfo
   
   # Health check del servidor
   curl http://localhost:8000/health
   ```

2. **Flujos de prueba recomendados**
   - Iniciar con `/start` o "Hola"
   - Navegar por menús usando botones
   - Registrar mediciones (peso: 70.5 kg, glucosa: 120 mg/dL)
   - Agendar citas médicas
   - Probar detección de emergencias (glucosa: 400 mg/dL)

## 🚀 Despliegue

### 🖥️ Desarrollo Local
```bash
# Ejecutar agentes en modo simulación
poetry run python test_agents.py

# Ejecutar servidor Telegram (desarrollo)
poetry run python telegram_main.py

# Ejecutar con configuración específica
LOG_LEVEL=DEBUG poetry run python telegram_main.py
```

#### Configuración de Webhooks para Desarrollo
```bash
# 1. Instalar y configurar ngrok
ngrok http 8000

# 2. Configurar webhook de Telegram
curl -X POST https://api.telegram.org/bot{TOKEN}/setWebhook \
  -H "Content-Type: application/json" \
  -d '{"url": "https://tu-url.ngrok.io/telegram/webhook"}'

# 3. Verificar configuración
curl https://api.telegram.org/bot{TOKEN}/getWebhookInfo
```

### ☁️ Vertex AI Agent Engine
```bash
# Preparar para despliegue (cuando ADK esté disponible)
# El código está estructurado para migración directa

# Configurar credenciales
gcloud auth application-default login

# Desplegar agentes
# poetry run adk deploy --project tu-proyecto --region us-central1
```

### 🐳 Docker/Cloud Run
```bash
# Construir imagen
docker build -t dr-clivi .

# Desplegar en Cloud Run
gcloud run deploy dr-clivi \
  --image dr-clivi \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## 📊 Migración desde Conversational Agents

Este proyecto representa una migración completa desde Google Cloud Conversational Agents (ex-Dialogflow CX) a ADK:

### 🔄 Proceso de Migración Realizado

1. **✅ Exportación de Flujos**: Análisis de archivos ZIP exportados
2. **✅ Mapeo de Intents**: Conversión de intents a herramientas ADK  
3. **✅ Análisis de Entities**: Migración a validaciones Python
4. **✅ Conversión de Webhooks**: Integración con n8n y APIs
5. **✅ Recreación de Flows**: Lógica de flujos en agentes especializados

### 📈 Beneficios de la Migración

| Aspecto | Conversational Agents | ADK Multi-Agente |
|---------|----------------------|------------------|
| **Flexibilidad** | Flujos rígidos visuales | Código Python flexible |
| **Inteligencia** | LLM limitado | Gemini 2.5 nativo |
| **Escalabilidad** | Monolítico | Arquitectura modular |
| **Versionado** | UI manual | Git + CI/CD |
| **Testing** | Manual en consola | Suite automatizada |
| **Mantenimiento** | UI dispersa | Código centralizado |

### 🗂️ Documentación de Análisis

Ver carpeta `docs/analysis/` para:
- `agent-config-analysis.md`: Configuración de agentes
- `intents-entities-tools-analysis.md`: Mapeo de intents y entities
- `flows-analysis.md`: Análisis detallado de flujos
- `executive-summary.md`: Resumen ejecutivo

## 🔐 Seguridad y Privacidad

- 🔐 **Gestión de Secretos**: Variables de entorno para credenciales
- 🛡️ **Datos Médicos**: Consideraciones de privacidad sanitaria
- 🔒 **Autenticación API**: Tokens seguros para todas las integraciones
- 📋 **Auditoría**: Logging completo de actividad sin PII
- 🚫 **Sin PII en Código**: Datos sensibles solo en variables de entorno
- ⚠️ **Validaciones Médicas**: Rangos seguros para mediciones críticas

## 📈 Analytics y Monitoreo

### Eventos de Actividad Rastreados
- `PLAN_STATUS_CHECK_STARTED`: Inicio de verificación de plan
- `GLUCOSE_MEASUREMENT_RECORDED`: Registro de glucosa
- `WORKOUT_SIGNUP_COMPLETED`: Inscripción a ejercicio
- `NUTRITION_SPECIALIST_CONNECTED`: Conexión con nutricionista
- `SESSION_ENDED`: Fin de sesión con resumen

### Métricas Disponibles
- Distribución de usuarios por plan
- Flujos más utilizados por agente
- Tiempo promedio de sesión
- Tasas de finalización de flujos
- Intervenciones médicas críticas

## 🤝 Contribución

1. Fork el repositorio
2. Crear rama de feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit los cambios (`git commit -m 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abrir Pull Request

### 📝 Guías de Desarrollo
- Usar español para comentarios y mensajes de usuario
- Seguir patrones de validación médica existentes
- Mantener compatibilidad con estructura ADK
- Incluir tests para nuevas funcionalidades
- Documentar cambios en flujos médicos

## 📄 Licencia

Este proyecto está licenciado bajo la Licencia Apache 2.0 - ver el archivo [LICENSE](LICENSE) para detalles.

## 🆘 Soporte

- 🐛 Issues: [GitHub Issues](https://github.com/GibrannClivi/dr-clivi/issues)
- 📖 Documentación ADK: [ADK Docs](https://google.github.io/adk-docs/)
- 📊 Análisis del Proyecto: [Implementation Summary](docs/implementation-summary.md)

## 🚨 Descargo de Responsabilidad Médica

**IMPORTANTE**: Dr. Clivi es un asistente de IA para fines educativos y de apoyo. **NO reemplaza el consejo médico profesional, diagnóstico o tratamiento**. Siempre consulta con profesionales de la salud calificados para decisiones médicas. En caso de emergencia médica, contacta inmediatamente a servicios de urgencias.

### ⚠️ Limitaciones del Sistema
- No proporciona diagnósticos médicos
- Las recomendaciones son solo orientativas
- Requiere supervisión médica profesional
- No sustituye consultas médicas regulares

---

**Estado del Proyecto**: ✅ **IMPLEMENTACIÓN COMPLETA**  
**Versión**: 1.1.0  
**Última Actualización**: 4 de enero de 2025  
**Rama**: `dev` 

### 🆕 Novedades v1.1.0 (Rama dev)

- ✅ **Integración completa con Telegram Bot API**
- ✅ **Arquitectura híbrida determinística + IA**
- ✅ **Webhooks con HTTPS y ngrok para desarrollo**
- ✅ **Manejo avanzado de contexto de sesión**
- ✅ **Detección inteligente de emergencias médicas**
- ✅ **Navegación por botones inline y callbacks**
- ✅ **Validación mejorada de mediciones (peso/glucosa)**
- ✅ **Sistema de ruteo optimizado para múltiples canales**
- ✅ **Pruebas en tiempo real con bot funcionando**
- ✅ **Documentación actualizada y versionado en git**

### 🔧 Arquitectura Implementada

- **Servidor FastAPI**: `telegram_main.py` con endpoints de webhook y health check
- **Handler de Telegram**: `telegram_handler.py` con manejo completo de mensajes y callbacks
- **Flujos Determinísticos**: `deterministic_handler.py` con lógica híbrida avanzada
- **Páginas de Interface**: Sistema modular de páginas con navegación contextual
- **Coordinador Mejorado**: Ruteo inteligente entre canales y agentes especializados

## 🔗 Integración con Plataforma Clivi

### ⚠️ Nota Importante sobre "Clivi API"

**Clivi no tiene una API unificada formal**. En el código actual, las referencias a "Clivi API" son **placeholders/simulaciones** que indican dónde iría la integración real con los sistemas de Clivi.

### 🛠️ Integración Real

La integración con la plataforma Clivi se realiza a través de:

1. **n8n Webhooks** (`https://n8n.clivi.com.mx/webhook/`)
   - Endpoint principal para la mayoría de integraciones
   - Procesamiento de imágenes de básculas
   - Envío de mediciones y datos
   - Gestión de actividades y eventos

2. **Sistemas Específicos**
   - **Datos de Pacientes**: Base de datos o sistema CRM de Clivi
   - **Mediciones**: Sistema de almacenamiento de mediciones corporales
   - **Citas**: Sistema de gestión de citas médicas
   - **Mensajería**: WhatsApp Business API directa

3. **Webhooks Identificados en el Análisis**
   ```
   https://n8n.clivi.com.mx/webhook/imgfile-measurement-recognition
   https://n8n.clivi.com.mx/webhook/appointment
   https://n8n.clivi.com.mx/webhook/measurement  
   https://n8n.clivi.com.mx/webhook/complaint
   https://n8n.clivi.com.mx/webhook/activity
   ```

### 🔄 TODOs de Integración

En el código encontrarás comentarios como:
```python
# TODO: Integrate with Clivi platform via n8n webhook
```

Estos indican dónde se debe implementar la integración real con los sistemas de Clivi cuando estén disponibles.

