"""
WORKING Flask App with Built-in Chat Interface
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv()

from flask import Flask, jsonify, request, render_template_string
from flask_cors import CORS
import google.generativeai as genai

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
CORS(app)

genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# Inline HTML template
CHAT_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>AI Mental Health Chatbot</title>
    <style>
        body { font-family: Arial; margin: 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; display: flex; align-items: center; justify-content: center; }
        .container { width: 600px; height: 700px; background: white; border-radius: 20px; display: flex; flex-direction: column; box-shadow: 0 20px 60px rgba(0,0,0,0.3); }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center; border-radius: 20px 20px 0 0; }
        .crisis { background: #ef4444; color: white; padding: 10px; text-align: center; font-weight: bold; }
        #messages { flex: 1; padding: 20px; overflow-y: auto; background: #f5f5f5; }
        .msg { margin: 10px 0; padding: 12px; border-radius: 15px; max-width: 70%; }
        .user { background: #667eea; color: white; margin-left: auto; text-align: right; }
        .bot { background: white; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .input-area { padding: 15px; background: white; border-radius: 0 0 20px 20px; }
        input { width: calc(100% - 100px); padding: 12px; border: 2px solid #e0e0e0; border-radius: 25px; }
        button { width: 80px; padding: 12px; background: #667eea; color: white; border: none; border-radius: 25px; cursor: pointer; margin-left: 10px; }
        button:hover { background: #764ba2; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2 style="margin:0;">🤖 AI Mental Health Support</h2>
            <p style="margin:5px 0 0 0; font-size:14px;">Powered by Google Gemini</p>
        </div>
        <div class="crisis">⚠️ Crisis? Call 988 (US) or +1-800-273-8255</div>
        <div id="messages">
            <div class="msg bot">Hello! I'm your AI mental health support assistant. How are you feeling today?</div>
        </div>
        <div class="input-area">
            <input id="input" type="text" placeholder="Type your message..." onkeypress="if(event.key==='Enter')send()">
            <button onclick="send()">Send</button>
        </div>
    </div>
    <script>
        function addMsg(text, isUser) {
            const div = document.createElement('div');
            div.className = 'msg ' + (isUser ? 'user' : 'bot');
            div.textContent = text;
            document.getElementById('messages').appendChild(div);
            document.getElementById('messages').scrollTop = 999999;
        }
        
        async function send() {
            const input = document.getElementById('input');
            const msg = input.value.trim();
            if (!msg) return;
            
            input.value = '';
            addMsg(msg, true);
            addMsg('Typing...', false);
            
            try {
                const res = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message: msg})
                });
                const data = await res.json();
                
                document.getElementById('messages').lastChild.remove();
                addMsg(data.response || 'Sorry, I had trouble responding.', false);
            } catch(e) {
                document.getElementById('messages').lastChild.remove();
                addMsg('Error: Could not connect to server', false);
            }
        }
    </script>
</body>
</html>
'''

@app.route('/')
@app.route('/chat')
def chat():
    return render_template_string(CHAT_HTML)

@app.route('/api/chat', methods=['POST'])
def api_chat():
    try:
        data = request.get_json()
        user_msg = data.get('message', '')
        
        model = genai.GenerativeModel('models/gemini-2.5-flash')
        prompt = f"""You are a compassionate mental health support AI assistant.
Provide empathetic, helpful guidance. Keep responses concise (2-3 sentences).

User: {user_msg}

Response:"""
        
        response = model.generate_content(prompt)
        return jsonify({'response': response.text, 'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("="*60)
    print("🚀 AI Mental Health Chatbot - READY!")
    print("="*60)
    print("✅ Open in browser: http://localhost:5000")
    print("✅ Gemini AI: Configured")
    print("="*60)
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
