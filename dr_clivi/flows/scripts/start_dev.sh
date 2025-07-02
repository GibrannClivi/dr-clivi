#!/bin/bash
# start_dev.sh

echo "🚀 Iniciando Dr. Clivi en modo desarrollo..."

# 1. Verificar que las variables estén configuradas
if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo "❌ Falta TELEGRAM_BOT_TOKEN"
    exit 1
fi

# 2. Limpiar puerto si está ocupado
echo "🧹 Limpiando puerto 8000..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || true

# 3. Iniciar servidor
echo "📱 Iniciando servidor en puerto 8000..."
poetry run python telegram_main.py &

# 4. Esperar que el servidor esté listo
sleep 3

# 5. Health check
echo "🔍 Verificando salud del servidor..."
curl -s http://localhost:8000/health | jq '.'

echo "✅ Servidor iniciado. Configura ngrok y webhook manualmente."