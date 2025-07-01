# 🚀 Guía de Despliegue - Dr. Clivi Telegram Bot

## Configuración Inicial (5 minutos)

### 1. Crear Bot de Telegram
```bash
# En Telegram, busca @BotFather
# Comandos:
/newbot
# Sigue las instrucciones y guarda el token
```

### 2. Obtener Google AI Studio Key
```bash
# Ve a: https://aistudio.google.com
# Crea cuenta / inicia sesión
# Ve a "Get API Key"
# Crea nueva API key y guárdala
```

### 3. Configurar Entorno
```bash
# Clonar y configurar
git clone <repo>
cd dr-clivi

# Configurar dependencias
pip install -r requirements.txt
# o con poetry:
poetry install

# Configurar variables
cp .env.example .env
# Editar .env con tus tokens:
# GOOGLE_API_KEY=tu_api_key_aqui
# TELEGRAM_BOT_TOKEN=tu_bot_token_aqui
```

### 4. Probar Localmente
```bash
# Validar configuración
python setup_telegram.py

# Ejecutar tests
python test_telegram_bot.py

# Iniciar bot (modo polling)
python telegram_main.py
```

## Desarrollo con Webhooks (ngrok)

Para probar webhooks en desarrollo:

```bash
# Instalar ngrok
brew install ngrok  # macOS
# o: https://ngrok.com/download

# Terminal 1: Exponer puerto
ngrok http 8000

# Terminal 2: Configurar URL en .env
# TELEGRAM_WEBHOOK_URL=https://tu-url.ngrok.io

# Configurar webhook
curl -X POST http://localhost:8000/telegram/set_webhook

# Iniciar bot
python telegram_main.py
```

## Funcionalidades Disponibles

### 🤖 Experiencia del Usuario
1. **Inicio**: Usuario manda cualquier mensaje
2. **Menú**: Bot presenta opciones con botones
3. **Especialización**: Usuario selecciona diabetes/obesidad
4. **Asistencia**: Agente especializado responde
5. **IA**: Para consultas fuera de menú, ruteo inteligente
6. **Emergencias**: Detección automática y respuesta prioritaria

### 🏥 Capacidades Médicas
- ✅ Registro y seguimiento de glucosa
- ✅ Tutoriales de medicamentos
- ✅ Agendamiento de citas
- ✅ Planes de ejercicio personalizados
- ✅ Consultas nutricionales
- ✅ Detección de emergencias médicas
- ✅ Reportes y análisis

### 🔧 Características Técnicas
- ✅ Arquitectura híbrida (determinístico + IA)
- ✅ Sesiones persistentes por usuario
- ✅ Inline keyboards (botones interactivos)
- ✅ Formateo con Markdown
- ✅ Manejo robusto de errores
- ✅ Logging detallado

## Solución de Problemas

### Bot no responde
```bash
# Verificar configuración
python setup_telegram.py

# Verificar logs
tail -f logs/telegram_bot.log
```

### Error de API
```bash
# Verificar tokens en .env
cat .env | grep -E "(GOOGLE_API_KEY|TELEGRAM_BOT_TOKEN)"

# Probar conexión
curl "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/getMe"
```

### Webhook no funciona
```bash
# Verificar ngrok
curl http://localhost:4040/api/tunnels

# Reconfigurar webhook
curl -X DELETE http://localhost:8000/telegram/webhook
curl -X POST http://localhost:8000/telegram/set_webhook
```

## Migración a Producción

### Opción 1: Google Cloud Run
```bash
# Crear Dockerfile
# Configurar Cloud Run
# Usar dominio real para webhook
```

### Opción 2: VPS/Servidor
```bash
# Instalar en servidor
# Configurar nginx/reverse proxy  
# Usar certificado SSL
# Configurar systemd service
```

### Opción 3: Railway/Vercel
```bash
# Configurar despliegue automático
# Variables de entorno en plataforma
# Webhook con dominio de plataforma
```

## Monitoreo

### Logs
```bash
# Ver logs en tiempo real
tail -f logs/telegram_bot.log

# Buscar errores
grep ERROR logs/telegram_bot.log
```

### Métricas
- Usuarios activos por día
- Tipos de consultas más comunes
- Tiempo de respuesta promedio
- Tasa de detección de emergencias

### Health Check
```bash
# Endpoint de salud
curl http://localhost:8000/health

# Verificar uptime
curl http://localhost:8000/
```

## Roadmap

### Próximas Funcionalidades
- [ ] Soporte para imágenes (análisis de básculas)
- [ ] Integración con calendarios para citas
- [ ] Reportes PDF automatizados
- [ ] Notificaciones proactivas
- [ ] Dashboard de administración

### Integraciones Futuras
- [ ] WhatsApp Business API (producción)
- [ ] Sistemas EMR/HIS
- [ ] Wearables y dispositivos médicos
- [ ] Telemedicina integrada
