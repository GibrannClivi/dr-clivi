#!/usr/bin/env python3
"""
Verificador de configuración para Dr. Clivi
"""

import os
import sys
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

print("🔍 VERIFICADOR DE CONFIGURACIÓN DR. CLIVI")
print("=" * 50)

print("\n📋 Variables de entorno:")

# Verificar variables críticas
critical_vars = [
    "GOOGLE_API_KEY",
    "TELEGRAM_BOT_TOKEN"
]

for var in critical_vars:
    value = os.getenv(var)
    if value:
        print(f"✅ {var}: {value[:20]}...")
    else:
        print(f"❌ {var}: NO CONFIGURADO")

print("\n📱 Variables de Telegram:")
telegram_vars = [
    "TELEGRAM_BOT_TOKEN",
    "TELEGRAM_WEBHOOK_URL"
]

for var in telegram_vars:
    value = os.getenv(var)
    if value:
        print(f"✅ {var}: {value[:30]}...")
    else:
        print(f"❌ {var}: NO CONFIGURADO")

print("\n🔧 Prueba de carga de Config:")
try:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from dr_clivi.config import Config
    
    config = Config()
    print(f"✅ Config cargado exitosamente")
    print(f"   Telegram token: {config.telegram.bot_token[:20] if config.telegram.bot_token else 'NO CONFIGURADO'}...")
    print(f"   Webhook URL: {config.telegram.webhook_url[:30] if config.telegram.webhook_url else 'NO CONFIGURADO'}...")
    
except Exception as e:
    print(f"❌ Error cargando config: {e}")

print("\n📄 Contenido del archivo .env:")
try:
    with open('.env', 'r') as f:
        lines = f.readlines()
        for i, line in enumerate(lines[:20], 1):  # Solo mostrar primeras 20 líneas
            if 'API_KEY' in line or 'TOKEN' in line:
                # Censurar valores sensibles
                if '=' in line:
                    key, value = line.split('=', 1)
                    if value.strip() and not value.strip().startswith('#'):
                        print(f"   {i:2d}: {key}={value[:20].strip()}...")
                    else:
                        print(f"   {i:2d}: {line.strip()}")
                else:
                    print(f"   {i:2d}: {line.strip()}")
            elif line.strip() and not line.startswith('#'):
                print(f"   {i:2d}: {line.strip()}")
except FileNotFoundError:
    print("❌ Archivo .env no encontrado")
except Exception as e:
    print(f"❌ Error leyendo .env: {e}")
