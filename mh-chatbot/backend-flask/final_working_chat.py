"""
Complete Authentication System with Database and Sessions
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv()

from flask import Flask, jsonify, request, render_template_string, session, redirect
from flask_cors import CORS
import google.generativeai as genai
import sqlite3
import hashlib
import secrets
from functools import wraps

# Import games API
try:
    from games_api import games_api
    GAMES_API_AVAILABLE = True
except ImportError:
    GAMES_API_AVAILABLE = False
    print("⚠️  Games API not found - game score tracking disabled")


# Configure Flask with static folder in parent directory
app = Flask(__name__, 
            static_folder=os.path.join(os.path.dirname(__file__), '..'),
            static_url_path='')
CORS(app)
app.secret_key = os.getenv('SECRET_KEY', secrets.token_hex(32))

genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# Database setup
def init_db():
    conn = sqlite3.connect('users.db', timeout=30.0)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  email TEXT UNIQUE NOT NULL,
                  password TEXT NOT NULL,
                  phone TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

init_db()

# Register games API blueprint
if GAMES_API_AVAILABLE:
    app.register_blueprint(games_api)
    print("✅ Games API registered successfully!")

# Helper functions
def hash_password(password):
    """Hash password with SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_user(email, password):
    """Verify user credentials"""
    conn = sqlite3.connect('users.db', timeout=30.0)
    c = conn.cursor()
    c.execute('SELECT id, name, email FROM users WHERE email=? AND password=?', 
              (email, hash_password(password)))
    user = c.fetchone()
    conn.close()
    return user

def create_user(name, email, password, phone=None):
    """Create new user"""
    try:
        conn = sqlite3.connect('users.db', timeout=30.0)
        c = conn.cursor()
        c.execute('INSERT INTO users (name, email, password, phone) VALUES (?, ?, ?, ?)',
                  (name, email, hash_password(password), phone))
        conn.commit()
        user_id = c.lastrowid
        conn.close()
        return user_id
    except sqlite3.IntegrityError:
        return None  # User already exists

def login_required(f):
    """Decorator to protect routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function

# HTML Templates (embedded for simplicity)
HTML = '''<!DOCTYPE html>
<html><head><title>AI Mental Health Chatbot</title>
<style>
body{font-family:Arial;margin:0;padding:0;background:linear-gradient(135deg,#667eea,#764ba2);min-height:100vh}
.logout-btn{position:fixed;top:20px;right:20px;padding:12px 24px;background:rgba(255,255,255,0.2);backdrop-filter:blur(10px);color:#fff;border:2px solid rgba(255,255,255,0.3);border-radius:25px;cursor:pointer;font-weight:600;font-size:14px;transition:all 0.3s;z-index:999;display:flex;align-items:center;gap:8px}
.logout-btn:hover{background:rgba(255,255,255,0.3);transform:translateY(-2px);box-shadow:0 4px 12px rgba(0,0,0,0.2)}
.games-btn{position:fixed;top:20px;right:140px;padding:12px 24px;background:rgba(255,255,255,0.2);backdrop-filter:blur(10px);color:#fff;border:2px solid rgba(255,255,255,0.3);border-radius:25px;cursor:pointer;font-weight:600;font-size:14px;transition:all 0.3s;z-index:999;display:flex;align-items:center;gap:8px;text-decoration:none}
.games-btn:hover{background:rgba(255,255,255,0.3);transform:translateY(-2px);box-shadow:0 4px 12px rgba(0,0,0,0.2)}
.chat-widget{position:fixed;bottom:20px;right:20px;z-index:1000}
.chat-icon{width:60px;height:60px;background:linear-gradient(135deg,#667eea,#764ba2);border-radius:50%;display:flex;align-items:center;justify-content:center;cursor:pointer;box-shadow:0 4px 20px rgba(0,0,0,0.3);transition:transform 0.3s,box-shadow 0.3s}
.chat-icon:hover{transform:scale(1.1);box-shadow:0 6px 30px rgba(0,0,0,0.4)}
.chat-icon span{font-size:30px;color:#fff}
.chat-window{position:fixed;bottom:90px;right:20px;width:400px;height:600px;background:#fff;border-radius:20px;display:none;flex-direction:column;box-shadow:0 20px 60px rgba(0,0,0,0.3);animation:slideIn 0.3s ease-out}
.chat-window.show{display:flex}
@keyframes slideIn{from{opacity:0;transform:translateY(20px)}to{opacity:1;transform:translateY(0)}}
.header{background:linear-gradient(135deg,#667eea,#764ba2);color:#fff;padding:15px 20px;border-radius:20px 20px 0 0;display:flex;justify-content:space-between;align-items:center}
.header h2{margin:0;font-size:18px}
.close-btn{background:rgba(255,255,255,0.2);border:none;color:#fff;width:30px;height:30px;border-radius:50%;cursor:pointer;font-size:18px;display:flex;align-items:center;justify-content:center;transition:background 0.3s}
.close-btn:hover{background:rgba(255,255,255,0.3)}
#msgs{flex:1;padding:20px;overflow-y:auto;background:#f5f5f5}
.msg{margin:10px 0;padding:12px;border-radius:15px;max-width:70%;word-wrap:break-word}
.user{background:#667eea;color:#fff;margin-left:auto;text-align:right}
.bot{background:#fff;box-shadow:0 2px 5px rgba(0,0,0,0.1)}
.input-area{padding:15px;background:#fff;border-radius:0 0 20px 20px;display:flex;gap:10px}
#inp{flex:1;padding:12px;border:2px solid #e0e0e0;border-radius:25px;font-size:14px;outline:none}
#inp:focus{border-color:#667eea}
.send-btn{padding:12px 24px;background:#667eea;color:#fff;border:none;border-radius:25px;cursor:pointer;font-weight:600;transition:background 0.3s}
.send-btn:hover{background:#764ba2}
</style></head><body>
<a href="/games" class="games-btn">
<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
<path d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z"/>
<path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/>
</svg>
🎮 Games
</a>
<button class="logout-btn" onclick="logout()">
<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4M16 17l5-5-5-5M21 12H9"/>
</svg>
Logout
</button>
<div class="chat-widget">
<div class="chat-window" id="chatWindow">
<div class="header">
<h2>🤖 Mental Health Support</h2>
<button class="close-btn" id="closeBtn">×</button>
</div>
<div id="msgs"><div class="msg bot">Hello! I'm your AI mental health support assistant. How are you feeling today?</div></div>
<div class="input-area">
<input id="inp" type="text" placeholder="Type message here...">
<button class="send-btn" id="btn">SEND</button>
</div>
</div>
<div class="chat-icon" id="chatIcon">
<span>💬</span>
</div>
</div>
<script>
const inp=document.getElementById('inp');
const btn=document.getElementById('btn');
const msgs=document.getElementById('msgs');
const chatIcon=document.getElementById('chatIcon');
const chatWindow=document.getElementById('chatWindow');
const closeBtn=document.getElementById('closeBtn');

chatIcon.addEventListener('click',()=>{
chatWindow.classList.add('show');
chatIcon.style.display='none';
inp.focus();
});

closeBtn.addEventListener('click',()=>{
chatWindow.classList.remove('show');
chatIcon.style.display='flex';
});

function add(txt,isUser){
const d=document.createElement('div');
d.className='msg '+(isUser?'user':'bot');
d.textContent=txt;
msgs.appendChild(d);
msgs.scrollTop=999999;
}

async function send(){
const msg=inp.value.trim();
if(!msg)return;
inp.value='';
add(msg,true);
add('Typing...',false);
try{
const r=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:msg})});
const data=await r.json();
msgs.lastChild.remove();
add(data.response||'Sorry, error occurred',false);
}catch(e){
msgs.lastChild.remove();
add('ERROR: Cannot connect to server',false);
console.error(e);
}
}

btn.addEventListener('click',send);
inp.addEventListener('keypress',e=>{if(e.key==='Enter')send()});

function logout(){
if(confirm('Are you sure you want to logout?')){
window.location.href='/logout';
}
}

console.log('Chat widget ready!');
</script></body></html>'''

@app.route('/')
@app.route('/login')
def login_page():
    # If already logged in, redirect to chat
    if 'user_id' in session:
        return redirect('/chat')
    
    auth_path = os.path.join(os.path.dirname(__file__), '..', 'auth.html')
    try:
        with open(auth_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: auth.html not found at {auth_path}", 404

@app.route('/chat')
@login_required
def chat():
    # Serve the full dashboard with all features
    index_path = os.path.join(os.path.dirname(__file__), '..', 'index.html')
    try:
        with open(index_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: index.html not found", 404

@app.route('/games')
@login_required
def games_page():
    games_path = os.path.join(os.path.dirname(__file__), '..', 'games.html')
    try:
        with open(games_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: games.html not found", 404

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/api/auth/login', methods=['POST'])
def api_login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        user = verify_user(email, password)
        if user:
            session['user_id'] = user[0]
            session['user_name'] = user[1]
            session['user_email'] = user[2]
            return jsonify({'success': True, 'message': 'Login successful'})
        else:
            return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/signup', methods=['POST'])
def api_signup():
    try:
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        
        if not name or not email or not password:
            return jsonify({'success': False, 'error': 'All fields required'}), 400
        
        user_id = create_user(name, email, password)
        if user_id:
            session['user_id'] = user_id
            session['user_name'] = name
            session['user_email'] = email
            return jsonify({'success': True, 'message': 'Account created'})
        else:
            return jsonify({'success': False, 'error': 'Email already exists'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/otp/send', methods=['POST'])
def send_otp():
    try:
        data = request.get_json()
        phone = data.get('phone')
        # TODO: Implement OTP sending via SMS/Email
        return jsonify({'success': True, 'requestId': '12345'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/otp/verify', methods=['POST'])
def verify_otp():
    try:
        data = request.get_json()
        otp = data.get('otp')
        request_id = data.get('requestId')
        # TODO: Implement OTP verification
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def api_chat():
    try:
        data = request.get_json()
        msg = data.get('message', '')
        print(f"[CHAT] Received message: {msg}")
        model = genai.GenerativeModel('models/gemini-2.5-flash')
        prompt = f"You are a compassionate mental health support AI. Respond empathetically and concisely (2-3 sentences).\n\nUser: {msg}\n\nResponse:"
        resp = model.generate_content(prompt)
        print(f"[CHAT] Response generated successfully")
        return jsonify({'response': resp.text, 'success': True})
    except Exception as e:
        print(f"[CHAT ERROR] {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("=" * 60)
    print("🎉 CHATBOT READY - OPEN: http://localhost:5000")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5000, debug=True)
