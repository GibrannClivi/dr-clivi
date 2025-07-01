#!/usr/bin/env python3
"""
Dr. Clivi - Quick Start Script for Telegram
Simplifies the initial setup and testing process.
"""

import os
import sys
import subprocess
import asyncio
from pathlib import Path


def print_header():
    """Print welcome header"""
    print("🤖 Dr. Clivi - Quick Start")
    print("==========================")
    print("Configuración automática para desarrollo con Telegram")
    print()


def check_dependencies():
    """Check if required dependencies are installed"""
    print("📦 Verificando dependencias...")
    
    try:
        import fastapi
        import httpx
        import google.generativeai
        print("✅ Dependencias principales encontradas")
        return True
    except ImportError as e:
        print(f"❌ Falta dependencia: {e}")
        print("Instalando dependencias...")
        
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
            print("✅ Dependencias instaladas")
            return True
        except subprocess.CalledProcessError:
            print("❌ Error instalando dependencias. Instala manualmente:")
            print("pip install fastapi uvicorn httpx google-generativeai pydantic pydantic-settings python-dotenv")
            return False


def setup_env_file():
    """Setup .env file if it doesn't exist"""
    print("\n⚙️  Configurando archivo .env...")
    
    env_path = Path(".env")
    env_example_path = Path(".env.example")
    
    if not env_path.exists():
        if env_example_path.exists():
            import shutil
            shutil.copy(env_example_path, env_path)
            print("✅ Archivo .env creado desde .env.example")
        else:
            # Create basic .env
            with open(env_path, 'w') as f:
                f.write("# Dr. Clivi Configuration\n")
                f.write("GOOGLE_API_KEY=your_google_ai_studio_key_here\n")
                f.write("TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here\n")
                f.write("LOG_LEVEL=INFO\n")
            print("✅ Archivo .env básico creado")
    else:
        print("✅ Archivo .env ya existe")
    
    return env_path


def check_configuration(env_path):
    """Check if required configuration is present"""
    print("\n🔍 Verificando configuración...")
    
    # Read .env file
    env_vars = {}
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env_vars[key] = value
    
    missing = []
    
    # Check Google API Key
    google_key = env_vars.get('GOOGLE_API_KEY', '')
    if not google_key or google_key in ['', 'your_google_ai_studio_key_here']:
        missing.append('GOOGLE_API_KEY')
    
    # Check Telegram Bot Token
    telegram_token = env_vars.get('TELEGRAM_BOT_TOKEN', '')
    if not telegram_token or telegram_token in ['', 'your_telegram_bot_token_here']:
        missing.append('TELEGRAM_BOT_TOKEN')
    
    if missing:
        print(f"❌ Faltan configuraciones: {', '.join(missing)}")
        print("\n📝 Pasos para completar la configuración:")
        
        if 'GOOGLE_API_KEY' in missing:
            print("1. Ve a https://aistudio.google.com")
            print("   - Crea cuenta o inicia sesión")
            print("   - Ve a 'Get API Key'")
            print("   - Crea nueva API key")
            print("   - Copia la clave en GOOGLE_API_KEY en .env")
        
        if 'TELEGRAM_BOT_TOKEN' in missing:
            print("2. En Telegram, busca @BotFather")
            print("   - Envía /newbot")
            print("   - Sigue las instrucciones")
            print("   - Copia el token en TELEGRAM_BOT_TOKEN en .env")
        
        print(f"\n3. Edita el archivo .env:")
        print(f"   nano {env_path}")
        print("\n4. Ejecuta este script de nuevo")
        return False
    
    print("✅ Configuración completa")
    return True


def run_tests():
    """Run the test suite"""
    print("\n🧪 Ejecutando tests...")
    
    try:
        result = subprocess.run([sys.executable, "test_telegram_bot.py"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Tests completados exitosamente")
            # Show only the summary
            lines = result.stdout.split('\n')
            for line in lines:
                if '📊 Test Results:' in line or '🎉' in line:
                    print(line)
            return True
        else:
            print("❌ Algunos tests fallaron")
            print(result.stdout)
            return False
            
    except Exception as e:
        print(f"❌ Error ejecutando tests: {e}")
        return False


def start_bot():
    """Start the Telegram bot"""
    print("\n🚀 Iniciando Dr. Clivi Telegram Bot...")
    print("Presiona Ctrl+C para detener")
    print()
    
    try:
        subprocess.run([sys.executable, "telegram_main.py"])
    except KeyboardInterrupt:
        print("\n👋 Bot detenido. ¡Gracias por usar Dr. Clivi!")
    except Exception as e:
        print(f"❌ Error iniciando bot: {e}")


def main():
    """Main setup flow"""
    print_header()
    
    # Step 1: Dependencies
    if not check_dependencies():
        return
    
    # Step 2: Environment file
    env_path = setup_env_file()
    
    # Step 3: Configuration
    if not check_configuration(env_path):
        return
    
    # Step 4: Tests
    if not run_tests():
        print("\n⚠️  Tests fallaron, pero puedes continuar")
        response = input("¿Continuar de todas formas? (y/N): ")
        if response.lower() != 'y':
            return
    
    # Step 5: Start bot
    print("\n🎉 ¡Todo listo!")
    print("Dr. Clivi está configurado y listo para usar")
    print("\nOpciones:")
    print("1. Iniciar bot ahora")
    print("2. Salir (iniciar manualmente con: python telegram_main.py)")
    
    choice = input("\nSelección (1/2): ").strip()
    
    if choice == "1":
        start_bot()
    else:
        print("\n✅ Configuración completa")
        print("Para iniciar el bot: python telegram_main.py")
        print("Para tests: python test_telegram_bot.py")


if __name__ == "__main__":
    main()
