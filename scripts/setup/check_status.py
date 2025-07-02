#!/usr/bin/env python3
"""
Dr. Clivi - Verificación de Estado del Proyecto
Comprueba que todo está listo para implementación
"""

import os
import sys
from pathlib import Path


def check_mark(condition: bool) -> str:
    return "✅" if condition else "❌"


def warning_mark(condition: bool) -> str:
    return "✅" if condition else "⚠️ "


def print_header():
    print("🏥 Dr. Clivi - Estado del Proyecto")
    print("=" * 40)


def check_project_structure():
    """Verificar estructura del proyecto"""
    print("\n📁 ESTRUCTURA DEL PROYECTO")
    print("-" * 30)
    
    required_files = [
        "dr_clivi/__init__.py",
        "dr_clivi/config.py",
        "dr_clivi/agents/coordinator.py",
        "dr_clivi/agents/diabetes_agent.py",
        "dr_clivi/flows/deterministic_handler.py",
        "dr_clivi/telegram/telegram_handler.py",
        "pyproject.toml",
        ".env.example",
        "telegram_main.py",
        "setup_credentials.py",
        "setup_ngrok.py"
    ]
    
    all_good = True
    for file_path in required_files:
        exists = Path(file_path).exists()
        print(f"{check_mark(exists)} {file_path}")
        if not exists:
            all_good = False
    
    return all_good


def check_dependencies():
    """Verificar dependencias Python"""
    print("\n📦 DEPENDENCIAS")
    print("-" * 20)
    
    dependencies = [
        ("google-adk", "google.adk"),
        ("fastapi", "fastapi"),
        ("uvicorn", "uvicorn"),
        ("httpx", "httpx"),
        ("pydantic", "pydantic"),
        ("python-dotenv", "dotenv")
    ]
    
    all_good = True
    for package_name, import_name in dependencies:
        try:
            __import__(import_name)
            print(f"✅ {package_name}")
        except ImportError:
            print(f"❌ {package_name} (pip install {package_name})")
            all_good = False
    
    return all_good


def check_configuration():
    """Verificar configuración"""
    print("\n⚙️  CONFIGURACIÓN")
    print("-" * 20)
    
    # Verificar .env
    env_exists = Path('.env').exists()
    print(f"{check_mark(env_exists)} Archivo .env")
    
    if env_exists:
        # Cargar variables
        from dotenv import load_dotenv
        load_dotenv()
        
        # Verificar variables clave
        google_api_key = os.getenv('GOOGLE_API_KEY', '')
        telegram_token = os.getenv('TELEGRAM_BOT_TOKEN', '')
        
        google_configured = google_api_key and google_api_key != 'your_ai_studio_api_key_here'
        telegram_configured = telegram_token and telegram_token != 'your_telegram_bot_token_here'
        
        print(f"{check_mark(google_configured)} Google AI Studio API Key")
        print(f"{check_mark(telegram_configured)} Telegram Bot Token")
        
        if google_configured and telegram_configured:
            return True
    
    return False


def check_adk_implementation():
    """Verificar implementación ADK"""
    print("\n🤖 IMPLEMENTACIÓN ADK")
    print("-" * 25)
    
    try:
        from dr_clivi.config import Config
        config = Config()
        print("✅ Configuración ADK cargada")
        
        from dr_clivi.agents.coordinator import IntelligentCoordinator
        coordinator = IntelligentCoordinator(config)
        print("✅ IntelligentCoordinator inicializado")
        
        from dr_clivi.flows.deterministic_handler import DeterministicFlowHandler
        flow_handler = DeterministicFlowHandler(config)
        print("✅ DeterministicFlowHandler inicializado")
        
        from dr_clivi.telegram.telegram_handler import TelegramBotHandler
        telegram_handler = TelegramBotHandler(config)
        print("✅ TelegramBotHandler inicializado")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en implementación: {e}")
        return False


def check_scripts():
    """Verificar scripts de configuración"""
    print("\n🔧 SCRIPTS DE CONFIGURACIÓN")
    print("-" * 30)
    
    scripts = [
        "setup_credentials.py",
        "setup_ngrok.py", 
        "telegram_main.py",
        "test_telegram_bot.py"
    ]
    
    all_good = True
    for script in scripts:
        exists = Path(script).exists()
        executable = os.access(script, os.X_OK) if exists else False
        
        status = "✅" if exists and executable else "⚠️" if exists else "❌"
        print(f"{status} {script}")
        
        if not exists:
            all_good = False
    
    return all_good


def get_next_steps(config_ready: bool):
    """Obtener próximos pasos"""
    print("\n🎯 PRÓXIMOS PASOS")
    print("-" * 20)
    
    if not config_ready:
        print("1️⃣ Configurar credenciales:")
        print("   python setup_credentials.py")
        print()
        print("2️⃣ O configurar manualmente:")
        print("   - Google AI Studio: https://aistudio.google.com")
        print("   - Telegram @BotFather: /newbot")
        print("   - Editar .env con los tokens")
    else:
        print("1️⃣ Testing local:")
        print("   python telegram_main.py")
        print()
        print("2️⃣ Testing con webhooks:")
        print("   python setup_ngrok.py")
        print()
        print("3️⃣ Probar en Telegram:")
        print("   Busca tu bot y envía 'hola'")


def main():
    print_header()
    
    # Verificaciones
    structure_ok = check_project_structure()
    deps_ok = check_dependencies()
    config_ok = check_configuration()
    adk_ok = check_adk_implementation()
    scripts_ok = check_scripts()
    
    # Resumen
    print("\n📊 RESUMEN")
    print("-" * 15)
    print(f"{check_mark(structure_ok)} Estructura del proyecto")
    print(f"{check_mark(deps_ok)} Dependencias Python")
    print(f"{check_mark(config_ok)} Configuración (.env)")
    print(f"{check_mark(adk_ok)} Implementación ADK")
    print(f"{warning_mark(scripts_ok)} Scripts de configuración")
    
    all_ready = structure_ok and deps_ok and adk_ok and scripts_ok
    
    if all_ready and config_ok:
        print("\n🎉 ¡TODO LISTO PARA USAR!")
        print("   Ejecuta: python telegram_main.py")
    elif all_ready:
        print("\n⚠️  LISTO PARA CONFIGURAR")
        print("   Solo faltan las credenciales")
    else:
        print("\n❌ NECESITA CONFIGURACIÓN")
        
        if not deps_ok:
            print("   Instala dependencias: pip install -r requirements.txt")
        if not structure_ok:
            print("   Verifica archivos del proyecto")
        if not adk_ok:
            print("   Revisa implementación ADK")
    
    get_next_steps(config_ok)
    
    print("\n" + "="*40)
    print("📖 Para ayuda completa: cat SETUP_GUIDE.md")


if __name__ == "__main__":
    main()
