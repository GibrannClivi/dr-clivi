#!/usr/bin/env python3
"""
Dr. Clivi - Configuración de ngrok para Webhooks
Script para configurar ngrok y webhooks de Telegram
"""

import os
import sys
import json
import time
import asyncio
import httpx
import subprocess
from pathlib import Path


def print_header():
    print("🌐 Dr. Clivi - Configuración de ngrok")
    print("=" * 40)
    print()


def print_step(step: int, title: str):
    print(f"\n📋 PASO {step}: {title}")
    print("-" * 30)


def check_ngrok_installed() -> bool:
    """Verificar si ngrok está instalado"""
    try:
        result = subprocess.run(['ngrok', 'version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ ngrok instalado: {result.stdout.strip()}")
            return True
        else:
            return False
    except FileNotFoundError:
        return False


def install_ngrok():
    """Instalar ngrok"""
    print("📦 Instalando ngrok...")
    
    system = os.uname().sysname.lower()
    
    if system == 'darwin':  # macOS
        print("🍎 Detectado macOS")
        try:
            subprocess.run(['brew', 'install', 'ngrok'], check=True)
            print("✅ ngrok instalado con Homebrew")
            return True
        except subprocess.CalledProcessError:
            print("❌ Error instalando con Homebrew")
            print("   Instala manualmente desde: https://ngrok.com/download")
            return False
    else:
        print(f"🐧 Detectado {system}")
        print("📥 Descarga ngrok manualmente desde: https://ngrok.com/download")
        print("   O usa tu gestor de paquetes:")
        print("   - Ubuntu/Debian: snap install ngrok")
        print("   - Arch: yay -S ngrok")
        return False


async def get_ngrok_tunnels():
    """Obtener túneles activos de ngrok"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:4040/api/tunnels")
            response.raise_for_status()
            return response.json()
    except Exception as e:
        return None


def start_ngrok_tunnel(port: int = 8000):
    """Iniciar túnel ngrok"""
    print(f"🚀 Iniciando túnel ngrok en puerto {port}...")
    
    try:
        # Iniciar ngrok en background
        process = subprocess.Popen(
            ['ngrok', 'http', str(port)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        # Esperar un poco para que se inicie
        time.sleep(3)
        
        return process
    except Exception as e:
        print(f"❌ Error iniciando ngrok: {e}")
        return None


async def get_public_url():
    """Obtener URL pública de ngrok"""
    for attempt in range(10):
        tunnels_data = await get_ngrok_tunnels()
        
        if tunnels_data and 'tunnels' in tunnels_data:
            for tunnel in tunnels_data['tunnels']:
                if tunnel.get('proto') == 'https':
                    return tunnel['public_url']
        
        print(f"   Esperando ngrok... (intento {attempt + 1}/10)")
        await asyncio.sleep(1)
    
    return None


async def set_telegram_webhook(bot_token: str, webhook_url: str):
    """Configurar webhook de Telegram"""
    try:
        url = f"https://api.telegram.org/bot{bot_token}/setWebhook"
        data = {
            "url": f"{webhook_url}/telegram/webhook",
            "drop_pending_updates": True
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data)
            response.raise_for_status()
            result = response.json()
            
            if result.get('ok'):
                print(f"✅ Webhook configurado: {webhook_url}/telegram/webhook")
                return True
            else:
                print(f"❌ Error configurando webhook: {result}")
                return False
                
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def update_env_webhook_url(webhook_url: str):
    """Actualizar TELEGRAM_WEBHOOK_URL en .env"""
    env_path = Path('.env')
    
    if not env_path.exists():
        print("❌ Archivo .env no existe")
        return False
    
    # Leer contenido actual
    with open(env_path, 'r') as f:
        lines = f.readlines()
    
    # Actualizar línea del webhook
    updated = False
    for i, line in enumerate(lines):
        if line.startswith('TELEGRAM_WEBHOOK_URL='):
            lines[i] = f"TELEGRAM_WEBHOOK_URL={webhook_url}/telegram/webhook\n"
            updated = True
            break
    
    # Si no existía, añadirla
    if not updated:
        lines.append(f"\n# ngrok webhook URL\nTELEGRAM_WEBHOOK_URL={webhook_url}/telegram/webhook\n")
    
    # Escribir archivo actualizado
    with open(env_path, 'w') as f:
        f.writelines(lines)
    
    print(f"✅ .env actualizado con webhook URL")
    return True


async def main():
    print_header()
    
    # Verificar que tenemos las credenciales básicas
    from dotenv import load_dotenv
    load_dotenv()
    
    telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not telegram_token or telegram_token == 'your_telegram_bot_token_here':
        print("❌ TELEGRAM_BOT_TOKEN no configurado")
        print("   Ejecuta primero: python setup_credentials.py")
        return
    
    # PASO 1: Verificar/instalar ngrok
    print_step(1, "Verificar ngrok")
    
    if not check_ngrok_installed():
        print("❌ ngrok no está instalado")
        print("\n¿Quieres instalarlo automáticamente? (s/n):", end=" ")
        
        if input().lower().strip() in ['s', 'si', 'y', 'yes']:
            if not install_ngrok():
                return
        else:
            print("📥 Instala ngrok manualmente desde: https://ngrok.com/download")
            return
    
    # PASO 2: Verificar si ya hay un túnel activo
    print_step(2, "Verificar túneles existentes")
    
    existing_url = await get_public_url()
    if existing_url:
        print(f"✅ Túnel ngrok ya activo: {existing_url}")
        
        print("\n¿Quieres usar este túnel existente? (s/n):", end=" ")
        if input().lower().strip() in ['s', 'si', 'y', 'yes']:
            webhook_url = existing_url
        else:
            print("⚠️  Cierra ngrok manualmente y vuelve a ejecutar este script")
            return
    else:
        # PASO 3: Iniciar nuevo túnel
        print_step(3, "Iniciar túnel ngrok")
        
        ngrok_process = start_ngrok_tunnel(8000)
        if not ngrok_process:
            return
        
        webhook_url = await get_public_url()
        if not webhook_url:
            print("❌ No se pudo obtener URL pública de ngrok")
            print("   Verifica que ngrok esté funcionando")
            return
        
        print(f"✅ Túnel creado: {webhook_url}")
    
    # PASO 4: Configurar webhook con Telegram
    print_step(4, "Configurar webhook con Telegram")
    
    success = await set_telegram_webhook(telegram_token, webhook_url)
    if not success:
        return
    
    # PASO 5: Actualizar .env
    print_step(5, "Actualizar configuración")
    update_env_webhook_url(webhook_url)
    
    # PASO 6: Información final
    print_step(6, "¡Configuración completada!")
    
    print(f"🌐 URL pública: {webhook_url}")
    print(f"🤖 Webhook: {webhook_url}/telegram/webhook")
    print(f"📊 Panel ngrok: http://localhost:4040")
    print()
    print("📋 PRÓXIMOS PASOS:")
    print("1. En otra terminal: python telegram_main.py")
    print("2. Prueba tu bot en Telegram")
    print("3. Monitorea logs en el panel de ngrok")
    print()
    print("⚠️  IMPORTANTE:")
    print("   - Mantén ngrok ejecutándose")
    print("   - Si reinicias ngrok, ejecuta este script de nuevo")
    print("   - Para producción, usa un dominio real")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Configuración cancelada")
    except Exception as e:
        print(f"\n❌ Error: {e}")
