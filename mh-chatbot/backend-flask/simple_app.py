"""
Enhanced Simple Flask App with Chat Endpoint
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv()

from flask import Flask, jsonify, request
from flask_cors import CORS
import google.generativeai as genai

# Create Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
CORS(app)  # Allow cross-origin requests from HTML file

# Configure Gemini
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

@app.route('/')
def index():
    return jsonify({
        'message': 'AI Mental Health Chatbot API',
        'status': 'running',
        'ai_provider': 'Google Gemini',
        'version': '1.0.0'
    })

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'ai': 'gemini-configured'})

@app.route('/chat')
def chat_page():
    """Serve the chatbot HTML page"""
    import os
    html_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'chatbot.html')
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "Chatbot HTML not found", 404

@app.route('/test-ai', methods=['GET', 'POST'])  
def test_ai():
    """Chat with Gemini AI"""
    try:
        # Get message from request (if POST) or use default
        if request.method == 'POST':
            data = request.get_json() or {}
            user_message = data.get('message', 'Hello')
        else:
            user_message = "Say hello and introduce yourself as a mental health support AI assistant in one sentence."
        
        # Call Gemini
        model = genai.GenerativeModel('models/gemini-2.5-flash')
        
        # Create a mental health support prompt
        prompt = f"""You are a compassionate AI mental health support assistant. 
        Respond with empathy, understanding, and helpful guidance.
        If the user mentions crisis keywords (suicide, self-harm), provide crisis hotline information.
        
        User message: {user_message}
        
        Your response:"""
        
        response = model.generate_content(prompt)
        
        return jsonify({
            'success': True,
            'response': response.text,
            'model': 'gemini-2.5-flash'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 AI Mental Health Chatbot Backend")
    print("=" * 60)
    print(f"✅ Gemini API: Configured")
    print(f"✅ Server: http://localhost:5000")
    print(f"✅ Chat API: http://localhost:5000/test-ai")
    print(f"\n📱 Open the website:")
    print(f"   file:///g:/My Drive/chatbot/mh-chatbot/chatbot.html")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5000, debug=True)
