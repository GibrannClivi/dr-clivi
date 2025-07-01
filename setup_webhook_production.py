#!/usr/bin/env python3
"""
Dr. Clivi - Configurador de Webhook para Producción
Maneja ngrok y configura webhook automáticamente
"""

import os
import sys
import json
import time
import asyncio
import httpx
import subprocess
import signal
from pathlib import Path


def print_header():
    print("🌐 Dr. Clivi - Webhook para Producción")
    print("=" * 40)


def kill_existing_ngrok():
    """Matar procesos ngrok existentes"""
    try:
        subprocess.run(['pkill', '-f', 'ngrok'], capture_output=True)
        print("🧹 Procesos ngrok anteriores terminados")
    except:
        pass


def start_ngrok(port=8000):
    """Iniciar ngrok y obtener URL"""
    print(f"🚀 Iniciando ngrok en puerto {port}...")
    
    # Matar procesos anteriores
    kill_existing_ngrok()
    time.sleep(2)
    
    # Iniciar ngrok
    try:
        process = subprocess.Popen(
            ['ngrok', 'http', str(port), '--log', 'stdout'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Esperar a que se inicie
        print("⏳ Esperando que ngrok se inicie...")
        time.sleep(5)
        
        return process
        
    except Exception as e:
        print(f"❌ Error iniciando ngrok: {e}")
        return None


async def get_ngrok_url(max_attempts=10):
    """Obtener URL pública de ngrok"""
    print("🔍 Obteniendo URL pública...")
    
    for attempt in range(max_attempts):
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get("http://localhost:4040/api/tunnels")
                response.raise_for_status()
                
                data = response.json()
                
                for tunnel in data.get('tunnels', []):
                    if tunnel.get('proto') == 'https':
                        url = tunnel['public_url']
                        print(f"✅ URL pública obtenida: {url}")
                        return url
                
        except Exception as e:
            print(f"   Intento {attempt + 1}/{max_attempts}: {e}")
            await asyncio.sleep(2)
    
    return None


async def configure_telegram_webhook(bot_token, webhook_url):
    """Configurar webhook con Telegram"""
    print("🤖 Configurando webhook con Telegram...")
    
    try:
        full_webhook_url = f"{webhook_url}/telegram/webhook"
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://api.telegram.org/bot{bot_token}/setWebhook",
                json={
                    "url": full_webhook_url,
                    "drop_pending_updates": True,
                    "max_connections": 40,
                    "allowed_updates": ["message", "callback_query"]
                }
            )
            response.raise_for_status()
            result = response.json()
            
            if result.get('ok'):
                print(f"✅ Webhook configurado: {full_webhook_url}")
                return True
            else:
                print(f"❌ Error: {result}")
                return False
                
    except Exception as e:
        print(f"❌ Error configurando webhook: {e}")
        return False


def update_env_file(webhook_url):
    """Actualizar .env con la URL del webhook"""
    print("📝 Actualizando archivo .env...")
    
    env_path = Path('.env')
    if not env_path.exists():
        print("❌ Archivo .env no existe")
        return False
    
    # Leer contenido actual
    with open(env_path, 'r') as f:
        content = f.read()
    
    # Actualizar o añadir webhook URL
    webhook_line = f"TELEGRAM_WEBHOOK_URL={webhook_url}"
    
    if "TELEGRAM_WEBHOOK_URL=" in content:
        # Reemplazar línea existente
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.startswith('TELEGRAM_WEBHOOK_URL='):
                lines[i] = webhook_line
                break
        content = '\n'.join(lines)
    else:
        # Añadir nueva línea
        content += f"\n\n# ngrok webhook URL (auto-generada)\n{webhook_line}\n"
    
    # Escribir archivo
    with open(env_path, 'w') as f:
        f.write(content)
    
    print(f"✅ .env actualizado")
    return True


async def verify_webhook(webhook_url):
    """Verificar que el webhook está funcionando"""
    print("🔍 Verificando webhook...")
    
    try:
        test_url = f"{webhook_url}/health"
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(test_url)
            
            if response.status_code == 200:
                print("✅ Webhook accesible desde internet")
                return True
            else:
                print(f"⚠️  Webhook devuelve código {response.status_code}")
                return False
                
    except Exception as e:
        print(f"⚠️  No se pudo verificar webhook: {e}")
        print("   (Esto es normal si el servidor no está ejecutándose aún)")
        return False


def show_next_steps(webhook_url):
    """Mostrar próximos pasos"""
    print("\n🎯 CONFIGURACIÓN COMPLETADA")
    print("=" * 30)
    print(f"🌐 URL pública: {webhook_url}")
    print(f"🤖 Webhook: {webhook_url}/telegram/webhook")
    print(f"📊 Panel ngrok: http://localhost:4040")
    print()
    print("📋 PRÓXIMOS PASOS:")
    print("1️⃣ En otra terminal:")
    print("   python telegram_main.py")
    print()
    print("2️⃣ Probar el bot en Telegram:")
    print("   - Busca tu bot")
    print("   - Envía 'hola'")
    print("   - Usa los menús interactivos")
    print()
    print("3️⃣ Monitorear:")
    print("   - Panel ngrok: http://localhost:4040")
    print("   - Logs del servidor")
    print()
    print("⚠️  IMPORTANTE:")
    print("   - Mantén ngrok ejecutándose")
    print("   - Mantén el servidor telegram_main.py ejecutándose")
    print("   - Para producción real, usa un dominio propio")


async def main():
    print_header()
    
    # Verificar configuración
    from dotenv import load_dotenv
    load_dotenv()
    
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not bot_token or bot_token == 'your_telegram_bot_token_here':
        print("❌ TELEGRAM_BOT_TOKEN no configurado")
        print("   Ejecuta: python setup_credentials.py")
        return
    
    print(f"✅ Bot token configurado: {bot_token[:10]}...")
    
    # Iniciar ngrok
    ngrok_process = start_ngrok(8000)
    if not ngrok_process:
        print("❌ No se pudo iniciar ngrok")
        return
    
    # Obtener URL pública
    webhook_url = await get_ngrok_url()
    if not webhook_url:
        print("❌ No se pudo obtener URL pública de ngrok")
        print("   Verifica que ngrok esté funcionando:")
        print("   curl http://localhost:4040/api/tunnels")
        return
    
    # Configurar webhook con Telegram
    success = await configure_telegram_webhook(bot_token, webhook_url)
    if not success:
        print("❌ No se pudo configurar webhook con Telegram")
        return
    
    # Actualizar .env
    update_env_file(webhook_url)
    
    # Verificar webhook (opcional)
    await verify_webhook(webhook_url)
    
    # Mostrar información final
    show_next_steps(webhook_url)
    
    print("\n🎉 ¡WEBHOOK CONFIGURADO PARA PRODUCCIÓN!")
    print("   El bot está listo para recibir mensajes de Telegram")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Configuración interrumpida")
        # Limpiar ngrok
        subprocess.run(['pkill', '-f', 'ngrok'], capture_output=True)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        # Limpiar ngrok
        subprocess.run(['pkill', '-f', 'ngrok'], capture_output=True)
