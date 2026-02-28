"""
Check Available Gemini Models
"""
import os
from dotenv import load_dotenv

load_dotenv()

import google.generativeai as genai

gemini_key = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=gemini_key)

print("Available Gemini models:")
for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"✅ {model.name}")

print("\nTrying models...")
# Try different model names
models_to_try = ['gemini-pro', 'models/gemini-pro', 'gemini-1.0-pro']

for model_name in models_to_try:
    try:
        print(f"\nTrying: {model_name}")
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Hello")
        print(f"✅ SUCCESS with {model_name}!")
        print(f"Response: {response.text[:100]}")
        break
    except Exception as e:
        print(f"❌ Failed: {e}")
