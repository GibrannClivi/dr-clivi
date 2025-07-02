#!/usr/bin/env python3
"""
Dr. Clivi - Script de Acceso Rápido
Facilita la ejecución de scripts comunes del proyecto
"""

import os
import sys
import subprocess
from pathlib import Path


def print_header():
    print("🏥 Dr. Clivi - Acceso Rápido")
    print("=" * 40)
    print()


def show_menu():
    print("📋 Opciones disponibles:")
    print()
    print("🔧 CONFIGURACIÓN:")
    print("  1. Verificar configuración")
    print("  2. Verificar estado del proyecto")
    print("  3. Configurar credenciales")
    print("  4. Configurar Telegram")
    print("  5. Configurar ngrok")
    print()
    print("🚀 EJECUCIÓN:")
    print("  6. Inicio rápido")
    print("  7. Servidor Telegram (webhook)")
    print("  8. Servidor Telegram (polling)")
    print()
    print("📊 EJEMPLOS Y DEMOS:")
    print("  9. Ejemplo de uso general")
    print(" 10. Demo Quick Ask")
    print(" 11. Demo integración backend")
    print()
    print("🧪 TESTS Y DEBUG:")
    print(" 12. Test cumplimiento ADK")
    print(" 13. Debug routing inteligente")
    print(" 14. Ejecutar todos los tests")
    print()
    print("  0. Salir")
    print()


def execute_script(script_path: str, description: str):
    """Ejecutar un script y mostrar el resultado"""
    print(f"🔄 Ejecutando: {description}")
    print("-" * 40)
    
    try:
        result = subprocess.run([sys.executable, script_path], 
                              capture_output=False, 
                              text=True, 
                              cwd=Path(__file__).parent)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error ejecutando {description}: {e}")
        return False


def main():
    print_header()
    
    while True:
        show_menu()
        choice = input("Selecciona una opción (0-14): ").strip()
        print()
        
        if choice == "0":
            print("👋 ¡Hasta luego!")
            break
        elif choice == "1":
            execute_script("scripts/setup/check_config.py", "Verificación de configuración")
        elif choice == "2":
            execute_script("scripts/setup/check_status.py", "Verificación de estado")
        elif choice == "3":
            execute_script("scripts/setup/setup_credentials.py", "Configuración de credenciales")
        elif choice == "4":
            execute_script("scripts/setup/setup_telegram.py", "Configuración de Telegram")
        elif choice == "5":
            execute_script("scripts/setup/setup_ngrok.py", "Configuración de ngrok")
        elif choice == "6":
            execute_script("scripts/quick_start.py", "Inicio rápido")
        elif choice == "7":
            execute_script("scripts/telegram_main.py", "Servidor Telegram (webhook)")
        elif choice == "8":
            execute_script("scripts/telegram_polling.py", "Servidor Telegram (polling)")
        elif choice == "9":
            execute_script("examples/example_usage.py", "Ejemplo de uso general")
        elif choice == "10":
            execute_script("examples/quick_ask_demo.py", "Demo Quick Ask")
        elif choice == "11":
            execute_script("examples/demo_backend_integration.py", "Demo integración backend")
        elif choice == "12":
            execute_script("test_adk_compliance.py", "Test cumplimiento ADK")
        elif choice == "13":
            execute_script("scripts/tools/debug_intelligent_routing.py", "Debug routing inteligente")
        elif choice == "14":
            print("🧪 Ejecutando todos los tests...")
            subprocess.run([sys.executable, "-m", "pytest", "tests/", "-v"], cwd=Path(__file__).parent)
        else:
            print("❌ Opción no válida. Intenta de nuevo.")
        
        input("\n⏎ Presiona Enter para continuar...")
        print("\n" + "="*50 + "\n")


if __name__ == "__main__":
    main()
