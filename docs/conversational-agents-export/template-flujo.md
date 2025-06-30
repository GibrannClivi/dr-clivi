# Template para Documentar tus Flujos de Conversational Agents

Este archivo te ayuda a documentar sistemáticamente tus flujos actuales de Conversational Agents (ex-Dialogflow CX) para migrar a ADK.

## 📋 Instrucciones de Uso

1. **Copia este template** para cada flujo que tengas
2. **Completa cada sección** con la información de tu flujo actual
3. **Incluye ejemplos reales** de conversaciones
4. **Documenta edge cases** y situaciones problemáticas
5. **Identifica mejoras** que quieres en la versión ADK

## 🎯 Template por Flujo

### Nombre del Flujo: [COMPLETAR]

## Información General
- **Nombre del Flujo**: [Nombre descriptivo]
- **Propósito**: [Descripción en 1-2 líneas]
- **Proyecto GCP**: [dtwo-qa u otro]
- **Última actualización**: [Fecha]
- **Estado**: [Activo/En desarrollo/Deprecated]

## Intents Principales

### Intent 1: [nombre_intent]
- **Training phrases**: 
  - "[ejemplo 1]"
  - "[ejemplo 2]"
  - "[ejemplo 3]"
- **Parameters**:
  - param1: @entity_type
  - param2: @sys.number
- **Response**: [Respuesta del bot]

### Intent 2: [nombre_intent]
- **Training phrases**: 
  - "[ejemplo 1]"
  - "[ejemplo 2]"
- **Parameters**:
  - param1: @entity_type
- **Response**: [Respuesta del bot]

[Repetir para cada intent]

## Pages/Estados del Flujo

### Page 1: [nombre_page]
- **Entry fulfillment**: "[Mensaje inicial]"
- **Form parameters**:
  - param1: required/optional
  - param2: required/optional
- **Intent routes**:
  - intent1 → page2
  - intent2 → page3
- **Conditional responses**:
  - Si condición1: "Respuesta A"
  - Si condición2: "Respuesta B"

### Page 2: [nombre_page]
[Repetir estructura]

## Entities Personalizadas

### @entity_name
- **Values**:
  - valor1
  - valor2
  - valor3

[Repetir para cada entity]

## Webhooks/Integraciones

### Webhook: /endpoint-name
- **Trigger**: [Cuándo se ejecuta]
- **Función**: 
  - [Qué hace el webhook]
  - [Qué datos procesa]
- **Response**: [Qué devuelve]

## Lógica Condicional

Describe la lógica de tu flujo:

```
SI condición1:
  ENTONCES acción1
SINO SI condición2:
  ENTONCES acción2
SINO:
  ENTONCES acción_default
```

## Responses Template

### Respuestas Estáticas:
- **Saludo**: "[Mensaje de bienvenida]"
- **Despedida**: "[Mensaje de cierre]"
- **Error**: "[Mensaje cuando no entiende]"

### Respuestas Dinámicas:
- **Variable1**: [Cómo se personaliza]
- **Variable2**: [Basado en qué datos]

## Métricas de Uso (si las tienes)
- **Intent más frecuente**: [nombre] (X%)
- **Intent menos usado**: [nombre] (X%)
- **Tasa de finalización**: X%
- **Puntos de abandono**: [donde se van los usuarios]

## Pain Points Identificados
1. **Problema 1**: [Descripción]
2. **Problema 2**: [Descripción]
3. **Problema 3**: [Descripción]

## Mejoras Deseadas para ADK
1. **Mejora 1**: [Qué quieres que haga mejor]
2. **Mejora 2**: [Nueva funcionalidad deseada]
3. **Mejora 3**: [Integración que necesitas]

## Ejemplos de Conversaciones Reales

### Conversación Exitosa:
```
Usuario: [mensaje inicial]
Bot: [respuesta]
Usuario: [seguimiento]
Bot: [respuesta final]
```

### Conversación Problemática:
```
Usuario: [mensaje que causa problemas]
Bot: [respuesta inadecuada]
Usuario: [confusión del usuario]
```

## Notas Adicionales
- [Cualquier información relevante]
- [Dependencias con otros sistemas]
- [Restricciones técnicas actuales]

---

## 🚀 Próximos Pasos Después de Documentar

1. **Priorizar flujos** por importancia/uso
2. **Mapear a arquitectura ADK** (Single/Multi-agent)
3. **Identificar tools necesarias** para cada funcionalidad
4. **Planificar integrations** con Clivi API
5. **Diseñar estrategia de testing** y migración gradual
