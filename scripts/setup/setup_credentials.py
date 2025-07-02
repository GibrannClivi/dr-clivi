#!/usr/bin/env python3
"""
Dr. Clivi - Configuración Interactiva
Script para configurar credenciales paso a paso
"""

import os
import sys
import asyncio
import httpx
from pathlib import Path


def print_header():
    print("🏥 Dr. Clivi - Configuración Paso a Paso")
    print("=" * 45)
    print()


def print_step(step: int, title: str):
    print(f"\n📋 PASO {step}: {title}")
    print("-" * 40)


def input_with_validation(prompt: str, validator=None, required=True):
    """Input con validación"""
    while True:
        value = input(prompt).strip()
        
        if not required and not value:
            return None
            
        if not value and required:
            print("❌ Este campo es obligatorio")
            continue
            
        if validator and not validator(value):
            continue
            
        return value


def validate_google_api_key(key: str) -> bool:
    """Validar formato de Google API Key"""
    if not key or len(key) < 20:
        print("❌ La API key parece muy corta")
        return False
    
    if not key.startswith('AI'):
        print("⚠️  La API key no tiene el formato esperado (debería empezar con 'AI')")
        print("   ¿Estás seguro que es correcta? (s/n):", end=" ")
        confirm = input().lower().strip()
        return confirm in ['s', 'si', 'y', 'yes']
    
    return True


def validate_telegram_token(token: str) -> bool:
    """Validar formato de Telegram bot token"""
    if not token or ':' not in token:
        print("❌ El token debe tener el formato: 123456789:ABCD-efgh...")
        return False
    
    parts = token.split(':')
    if len(parts) != 2 or not parts[0].isdigit():
        print("❌ Formato incorrecto del token")
        return False
    
    return True


async def test_google_api_key(api_key: str) -> bool:
    """Probar la API key de Google"""
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        
        # Crear un modelo simple para probar
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content("Hello")
        
        print("✅ Google AI Studio API key funciona correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error con Google AI Studio: {e}")
        return False


async def test_telegram_token(token: str) -> bool:
    """Probar el token de Telegram"""
    try:
        url = f"https://api.telegram.org/bot{token}/getMe"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            
            if data.get('ok'):
                bot_info = data.get('result', {})
                print(f"✅ Token de Telegram válido")
                print(f"   Bot: @{bot_info.get('username', 'unknown')}")
                print(f"   Nombre: {bot_info.get('first_name', 'unknown')}")
                return True
            else:
                print(f"❌ Token inválido: {data}")
                return False
                
    except Exception as e:
        print(f"❌ Error probando token: {e}")
        return False


def update_env_file(google_api_key: str, telegram_token: str, ngrok_url: str = None):
    """Actualizar archivo .env con las credenciales"""
    env_path = Path('.env')
    
    # Leer archivo actual
    if env_path.exists():
        with open(env_path, 'r') as f:
            content = f.read()
    else:
        # Copiar desde .env.example
        with open('.env.example', 'r') as f:
            content = f.read()
    
    # Actualizar valores
    content = content.replace('your_ai_studio_api_key_here', google_api_key)
    content = content.replace('your_telegram_bot_token_here', telegram_token)
    
    if ngrok_url:
        content = content.replace('https://your-ngrok-url.ngrok.io/telegram/webhook', ngrok_url)
    
    # Escribir archivo actualizado
    with open(env_path, 'w') as f:
        f.write(content)
    
    print(f"✅ Archivo .env actualizado")


async def main():
    print_header()
    
    # Verificar que estamos en el directorio correcto
    if not Path('.env.example').exists():
        print("❌ No se encuentra .env.example")
        print("   Asegúrate de estar en el directorio del proyecto")
        return
    
    # PASO 1: Google AI Studio
    print_step(1, "Configurar Google AI Studio")
    print("1. Ve a: https://aistudio.google.com")
    print("2. Inicia sesión con tu cuenta Google")
    print("3. Click en 'Get API Key' (botón azul)")
    print("4. Click en 'Create API Key'")
    print("5. Copia la API key")
    print()
    
    google_api_key = input_with_validation(
        "Pega tu Google AI Studio API key: ",
        validate_google_api_key
    )
    
    print("\n🔍 Probando Google AI Studio...")
    if not await test_google_api_key(google_api_key):
        print("❌ La API key no funciona. Verifica que sea correcta.")
        return
    
    # PASO 2: Telegram Bot
    print_step(2, "Configurar Bot de Telegram")
    print("1. Abre Telegram")
    print("2. Busca @BotFather")
    print("3. Envía: /newbot")
    print("4. Sigue las instrucciones")
    print("5. Copia el token (formato: 123456789:ABCD...)")
    print()
    
    telegram_token = input_with_validation(
        "Pega tu Telegram bot token: ",
        validate_telegram_token
    )
    
    print("\n🔍 Probando token de Telegram...")
    if not await test_telegram_token(telegram_token):
        print("❌ El token no funciona. Verifica que sea correcto.")
        return
    
    # PASO 3: Actualizar .env
    print_step(3, "Actualizar configuración")
    update_env_file(google_api_key, telegram_token)
    
    # PASO 4: Probar configuración
    print_step(4, "Probar configuración completa")
    
    try:
        # Cargar .env actualizado
        from dotenv import load_dotenv
        load_dotenv(override=True)
        
        # Probar configuración
        from dr_clivi.config import Config
        config = Config()
        
        print("✅ Configuración cargada correctamente")
        
        # Ejecutar tests
        print("\n🧪 Ejecutando tests...")
        os.system("python test_telegram_bot.py")
        
    except Exception as e:
        print(f"❌ Error en configuración: {e}")
        return
    
    # SIGUIENTE PASO
    print("\n🎉 ¡Configuración completada!")
    print("\n📋 PRÓXIMOS PASOS:")
    print("1. Para testing local: python telegram_main.py")
    print("2. Para webhooks: configura ngrok (siguiente script)")
    print("3. Para producción: deploy en Cloud Run")
    print()
    print("¿Quieres configurar ngrok ahora? (s/n):", end=" ")
    
    if input().lower().strip() in ['s', 'si', 'y', 'yes']:
        print("\n🚀 Ejecuta: python setup_ngrok.py")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Configuración cancelada")
    except Exception as e:
        print(f"\n❌ Error: {e}")
