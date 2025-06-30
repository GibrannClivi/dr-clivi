# Análisis de Configuración de Agentes - agent.json

## Resumen Ejecutivo

Se analizaron los archivos `agent.json` de ambos flujos exportados desde Google Cloud Conversational Agents (ex-Dialogflow CX) para entender la configuración base que debe migrar a los agentes ADK.

## Configuración del Agente de Diabetes

### Información General
- **Display Name**: `diabetes`
- **Idioma por defecto**: `es` (Español)
- **Zona horaria**: `America/Chicago`
- **Proyecto**: `456314813706`
- **Flujo de inicio**: `Default Start Flow`

### Configuraciones Habilitadas
- ✅ Logging habilitado (`enableLogging: true`)
- ✅ Stackdriver logging habilitado (`enableStackdriverLogging: true`)
- ✅ Interaction logging habilitado (`enableInteractionLogging: true`)

### Configuraciones de Voz
- **Sensibilidad del endpoint**: 90
- **Timeout sin habla**: 5 segundos
- Speech-to-Text y Text-to-Speech configurados pero sin parámetros específicos

### UI/UX
- **Border radius**: 0 (diseño cuadrado)

## Configuración del Agente de Obesidad

### Información General
- **Display Name**: `obesity`
- **Idioma por defecto**: `es` (Español)
- **Zona horaria**: `America/Chicago`
- **Proyecto**: `456314813706` (mismo proyecto)
- **Flujo de inicio**: `Default Start Flow`

### Configuraciones Habilitadas
- ✅ Logging habilitado (`enableLogging: true`)
- ✅ Stackdriver logging habilitado (`enableStackdriverLogging: true`)
- ✅ Interaction logging habilitado (`enableInteractionLogging: true`)

### Diferencias Clave vs Diabetes
- ✅ **GenApp Builder Settings**: Configurado con engine específico
  - Engine: `projects/456314813706/locations/us/collections/default_collection/engines/3c7a3867-2722-433b-af0a-369cfd22c2ca-chat-1750251928`
- ❌ **BigQuery Export Settings**: No configurado (ausente en diabetes también)

### Configuraciones de Voz
- **Sensibilidad del endpoint**: 90 (igual que diabetes)
- **Timeout sin habla**: 5 segundos (igual que diabetes)

## Mapeo a ADK

### Configuración Común a Migrar
```python
# dr_clivi/config.py - Configuración base común
AGENT_CONFIG = {
    "default_language": "es",
    "timezone": "America/Chicago",
    "logging_enabled": True,
    "interaction_logging": True,
    "speech_timeout": 5,
    "endpoint_sensitivity": 90
}

DIABETES_AGENT_CONFIG = {
    **AGENT_CONFIG,
    "agent_name": "diabetes",
    "start_flow": "diabetes_intake_flow"
}

OBESITY_AGENT_CONFIG = {
    **AGENT_CONFIG,
    "agent_name": "obesity", 
    "start_flow": "obesity_intake_flow",
    "genapp_builder_engine": "3c7a3867-2722-433b-af0a-369cfd22c2ca-chat-1750251928"
}
```

### Consideraciones para ADK

1. **Logging**: Implementar logging compatible con Vertex AI y Google Cloud Logging
2. **Multi-idioma**: Aunque configurado para ES, ADK permite fácil expansión a otros idiomas
3. **Flujos de inicio**: Mapear "Default Start Flow" a flows específicos de ADK
4. **GenApp Builder**: El agente de obesidad usa generative AI - considerar integración con Vertex AI
5. **Zona horaria**: Importante para scheduling y timestamps en WhatsApp
6. **Proyecto unificado**: Ambos agentes del mismo proyecto - facilita A2A communication

### Recomendaciones de Migración

1. **Configuración unificada**: Crear clase base `BaseCliviAgent` con configuración común
2. **Especialización**: Extender para `DiabetesAgent` y `ObesityAgent` con sus particularidades
3. **Logging estructurado**: Implementar logging compatible con Cloud Operations
4. **Estado compartido**: Diseñar para comunicación A2A entre agentes
5. **Escalabilidad**: Preparar para futuros agentes (hipertensión, etc.)

## Próximos Pasos

1. ✅ **Completado**: Análisis de agent.json
2. 🔄 **Siguiente**: Analizar flows/ para entender flujos conversacionales
3. 📋 **Pendiente**: Revisar intents/ y entityTypes/
4. 📋 **Pendiente**: Examinar webhooks/ y tools/
5. 📋 **Pendiente**: Implementar agentes base ADK

## Hallazgos Importantes

- **Proyecto unificado**: Facilita la comunicación entre agentes
- **Configuración similar**: Permite reutilización de código base
- **GenApp Builder en obesidad**: Indica uso de IA generativa avanzada
- **Logging completo**: Importante para debugging y analytics
- **Configuración de voz**: Sugiere uso en canal de voz además de texto/WhatsApp
