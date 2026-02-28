"""
Minimal Flask Backend for Chatbot - No dependencies on dotenv
"""
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return jsonify({
        'message': 'AI Mental Health Chatbot API',
        'status': 'running',
        'version': '1.0.0'
    })

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'})

@app.route('/test-ai', methods=['GET', 'POST'])
def test_ai():
    """Simple AI response endpoint"""
    try:
        if request.method == 'POST':
            data = request.get_json() or {}
            user_message = data.get('message', 'Hello')
        else:
            user_message = 'Hello'
        
        # Simple responses without AI (for testing)
        responses = {
            'hello': "Hello! I'm here to listen and provide support. How are you feeling today?",
            'hi': "Hi there! I'm your mental health support assistant. What's on your mind?",
            'anxious': "I understand you're feeling anxious. Let's try some grounding techniques. Can you name 5 things you can see around you?",
            'sad': "I hear that you're feeling sad. It's okay to feel this way. Would you like to talk about what's making you feel down?",
            'help': "I'm here to help. You can talk to me about anything - anxiety, stress, mood, or just to chat. What would you like to discuss?",
        }
        
        # Find matching response
        response_text = "I'm here to listen and support you. How can I help you today?"
        for keyword, resp in responses.items():
            if keyword in user_message.lower():
                response_text = resp
                break
        
        return jsonify({
            'success': True,
            'response': response_text,
            'model': 'simple-rules'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'response': "I'm having trouble processing that. Could you try again?"
        }), 500

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 AI Mental Health Chatbot Backend")
    print("=" * 60)
    print(f"✅ Server: http://localhost:5000")
    print(f"✅ Chat API: http://localhost:5000/test-ai")
    print(f"\n📱 Open in browser:")
    print(f"   file:///G:/My%20Drive/chatbot/mh-chatbot/chatbot.html")
    print("=" * 60)
    print("\n🎤 Voice features are enabled in chatbot.html!")
    print("Press Ctrl+C to stop the server\n")
    app.run(host='0.0.0.0', port=5000, debug=True)
