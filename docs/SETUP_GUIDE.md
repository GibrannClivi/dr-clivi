# 🚀 GUÍA PASO A PASO - Dr. Clivi con ADK + Telegram

## ✅ ESTADO ACTUAL
- ✅ Código ADK implementado y funcionando
- ✅ Arquitectura híbrida (determinístico + IA) lista
- ✅ Handler de Telegram implementado
- ✅ Tests automáticos validados
- 🔧 **PENDIENTE: Solo credenciales y configuración**

---

## 🎯 LO QUE NECESITAMOS HACER AHORA

### **FASE 1: Credenciales (10 minutos)**

#### 1️⃣ Ejecutar script interactivo
```bash
cd /Users/gibrann/Documents/adk-samples/python/agents/dr-clivi
python setup_credentials.py
```

**El script te guiará para:**
- ✅ Obtener Google AI Studio API Key
- ✅ Crear bot de Telegram con @BotFather  
- ✅ Configurar .env automáticamente
- ✅ Validar que todo funciona

#### 2️⃣ Obtener credenciales manualmente (si prefieres)

**Google AI Studio:**
1. Ve a: https://aistudio.google.com
2. Inicia sesión con tu cuenta Google
3. Click "Get API Key" → "Create API Key"
4. Copia la key (empieza con `AI...`)

**Telegram Bot:**
1. Abre Telegram
2. Busca `@BotFather`
3. Envía: `/newbot`
4. Nombre: `Dr Clivi Test Bot`
5. Username: `drclivi_test_bot` (o similar)
6. Copia el token (formato: `123456789:ABCD...`)

**Configurar .env:**
```bash
# Editar manualmente
nano .env

# O reemplazar valores:
GOOGLE_API_KEY=tu_api_key_aqui
TELEGRAM_BOT_TOKEN=tu_bot_token_aqui
```

---

### **FASE 2: Testing Local (5 minutos)**

#### 1️⃣ Probar configuración
```bash
python test_telegram_bot.py
```

#### 2️⃣ Iniciar bot en modo polling
```bash
python telegram_main.py
```

#### 3️⃣ Probar en Telegram
- Busca tu bot en Telegram
- Envía `/start` o `hola`
- Debería responder con menú de opciones

---

### **FASE 3: Webhooks con ngrok (10 minutos)**

#### 1️⃣ Configurar ngrok automáticamente
```bash
python setup_ngrok.py
```

**El script hará:**
- ✅ Instalar ngrok (si no está)
- ✅ Crear túnel público (https://xxx.ngrok.io)
- ✅ Configurar webhook con Telegram
- ✅ Actualizar .env automáticamente

#### 2️⃣ O configurar ngrok manualmente

**Instalar ngrok:**
```bash
# macOS
brew install ngrok

# Linux
snap install ngrok

# Windows: descargar de https://ngrok.com
```

**Iniciar túnel:**
```bash
# Terminal 1: Exponer puerto 8000
ngrok http 8000

# Copiar URL que aparece (https://abc123.ngrok.io)
```

**Configurar webhook:**
```bash
# Reemplazar con tu bot token y URL de ngrok
curl -X POST "https://api.telegram.org/bot<TU_BOT_TOKEN>/setWebhook" \
  -d "url=https://abc123.ngrok.io/telegram/webhook"
```

#### 3️⃣ Iniciar servidor webhook
```bash
# Terminal 2: Iniciar servidor
python telegram_main.py
```

---

### **FASE 4: Validación Final (5 minutos)**

#### 1️⃣ Verificar endpoints
```bash
# Health check
curl http://localhost:8000/health

# Panel ngrok (si usas webhooks)
open http://localhost:4040
```

#### 2️⃣ Probar funcionalidades completas

**En Telegram, prueba:**
- ✅ Mensaje inicial: `hola`
- ✅ Menú interactivo con botones
- ✅ Especialización: Click "Diabetes" 
- ✅ Pregunta libre: `¿cómo registro mi glucosa?`
- ✅ Emergencia: `tengo dolor en el pecho`

#### 3️⃣ Monitorear logs
```bash
# Ver logs en tiempo real
tail -f logs/dr_clivi.log

# O ver en panel ngrok: http://localhost:4040
```

---

## 🎯 DECISIÓN ARQUITECTURA ADK

### **Configuración Actual (Óptima para desarrollo)**
- ✅ **Google AI Studio**: Gratis, sin configuración GCP
- ✅ **Gemini 2.0 Flash**: Modelo más nuevo y eficiente
- ✅ **Telegram**: Testing rápido sin restricciones empresariales

### **Para Producción (Futuro)**
- 🔄 **Vertex AI**: Escalabilidad empresarial
- 🔄 **WhatsApp Business**: Canal de producción
- 🔄 **Cloud Run**: Despliegue automático

### **¿Necesitamos cambiar algo en ADK ahora?**
**NO.** La implementación actual es correcta:
- ✅ Usa `google-adk` con la arquitectura correcta
- ✅ Compatible con AI Studio Y Vertex AI
- ✅ Fácil migración cuando sea necesario

---

## 🚀 COMANDOS RÁPIDOS

### Setup completo automatizado:
```bash
# 1. Credenciales
python setup_credentials.py

# 2. Testing local
python telegram_main.py

# 3. Webhooks (otra terminal)
python setup_ngrok.py
```

### Troubleshooting:
```bash
# Verificar configuración
python -c "from dr_clivi.config import Config; print('✅ OK')"

# Probar Google AI
python -c "import google.generativeai as genai; print('✅ OK')"

# Ver logs
tail -f logs/dr_clivi.log
```

### Testing manual:
```bash
# Probar API de Telegram
curl "https://api.telegram.org/bot<TOKEN>/getMe"

# Probar webhook local
curl -X POST http://localhost:8000/telegram/webhook \
  -H "Content-Type: application/json" \
  -d '{"message":{"text":"test"}}'
```

---

## ❓ ¿QUÉ NECESITAS QUE HAGA?

**Opción A (Recomendada):** Ejecuta los scripts automáticos
```bash
python setup_credentials.py
```

**Opción B:** Dame las credenciales y yo configuro
1. Google AI Studio API Key
2. Telegram Bot Token

**Opción C:** Configuración manual paso a paso
- Te guío en cada paso específico

**¿Cuál prefieres?** 🤔
