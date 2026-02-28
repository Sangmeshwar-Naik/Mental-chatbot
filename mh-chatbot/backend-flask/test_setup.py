"""
Quick Test Script - Verify Gemini API Setup
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=" * 50)
print("Testing AI Mental Health Chatbot Setup")
print("=" * 50)

# Test 1: Check API Key
gemini_key = os.getenv('GEMINI_API_KEY')
if gemini_key:
    print("✅ Gemini API key found:", gemini_key[:20] + "...")
else:
    print("❌ No Gemini API key found")
    exit(1)

# Test 2: Test Gemini API Connection
print("\nTesting Gemini API connection...")
try:
    import google.generativeai as genai
    genai.configure(api_key=gemini_key)
    model = genai.GenerativeModel('models/gemini-2.5-flash')  # Using latest Gemini model
    
    response = model.generate_content("Say 'Hello! I'm ready to help with mental health support.'")
    print("✅ Gemini API working!")
    print("Response:", response.text)
    
except Exception as e:
    print(f"❌ Gemini API error: {e}")
    exit(1)

# Test 3: Check Flask imports
print("\nChecking Flask installation...")
try:
    import flask
    print(f"✅ Flask version: {flask.__version__}")
except ImportError as e:
    print(f"❌ Flask import error: {e}")
    exit(1)

print("\n" + "=" * 50)
print("✅ ALL TESTS PASSED!")
print("="  * 50)
print("\nYour backend is ready to run!")
print("Next step: python app.py")
