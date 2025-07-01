#!/usr/bin/env python3
"""
Test simple de la API de Google GenAI para verificar que funciona.
"""

import asyncio
import os
import sys
from pathlib import Path

# Agregar el directorio padre al path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Cargar variables de entorno
from dotenv import load_dotenv
load_dotenv()

async def test_genai_simple():
    """Test simple de Google GenAI"""
    print("🧪 TESTING GOOGLE GENAI API")
    print("=" * 40)
    
    try:
        import google.genai as genai
        
        # Configure API key
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            print("❌ GOOGLE_API_KEY not found in environment")
            return
        
        print(f"✅ API Key found: {api_key[:20]}...")
        
        # Initialize client
        client = genai.Client(api_key=api_key)
        print("✅ Client initialized")
        
        # Simple test
        test_prompt = """
        Analiza esta consulta médica y clasifica la especialidad:
        
        Consulta: "Tengo diabetes y mi glucosa está en 180 mg/dl"
        
        Responde solo con: diabetes, obesity, general, o emergency
        """
        
        print("🤖 Sending test prompt to Gemini...")
        
        response = await asyncio.to_thread(
            client.models.generate_content,
            model="gemini-2.0-flash-exp",
            contents=test_prompt
        )
        
        print(f"✅ Response received: {response.text}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_genai_simple())
