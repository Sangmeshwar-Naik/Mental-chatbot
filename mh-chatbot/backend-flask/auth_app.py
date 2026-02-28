"""
Minimal Flask Backend with Authentication
For Mental Health Chatbot
"""
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import bcrypt
from datetime import datetime, timedelta
import os

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mental_health.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# ========================================
# Database Models
# ========================================

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='user')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        """Check if password matches"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def to_dict(self):
        """Convert user to dictionary"""
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'role': self.role,
            'created_at': self.created_at.isoformat()
        }

# ========================================
# API Routes
# ========================================

@app.route('/')
def index():
    return jsonify({
        'message': 'Mental Health Chatbot API',
        'version': '1.0.0',
        'status': 'running'
    })

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'})

# Authentication Routes
@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        email = data.get('email')
        username = data.get('username')
        password = data.get('password')
        
        # Validation
        if not email or not username or not password:
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Check if user exists
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already registered'}), 400
        
        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Username already taken'}), 400
        
        # Create user
        user = User(email=email, username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'message': 'Registration successful',
            'user': user.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login user"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Missing email or password'}), 400
        
        # Find user
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        if not user.is_active:
            return jsonify({'error': 'Account is disabled'}), 403
        
        # Return user data (in production, return JWT token)
        return jsonify({
            'message': 'Login successful',
            'user': user.to_dict(),
            'token': f'simple-token-{user.id}'  # Simplified token
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/me', methods=['GET'])
def get_current_user():
    """Get current user (simplified - no real auth check)"""
    # In production, verify JWT token from Authorization header
    return jsonify({
        'id': 1,
        'email': 'user@example.com',
        'username': 'testuser',
        'role': 'user'
    })

# Chat Route
@app.route('/api/chat/message', methods=['POST'])
def chat_message():
    """Handle chat messages"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        
        # Simple responses (can integrate with Gemini API later)
        responses = {
            'hello': "Hello! I'm here to support you. How are you feeling today?",
            'hi': "Hi there! I'm your mental health assistant. What's on your mind?",
            'help': "I'm here to help. You can talk to me about your feelings, anxiety, stress, or anything else.",
            'anxious': "I understand you're feeling anxious. Let's try some grounding techniques. Can you name 5 things you can see?",
            'sad': "I hear that you're feeling sad. It's okay to feel this way. Would you like to talk about it?",
        }
        
        response_text = "I'm here to listen and support you. How can I help you today?"
        for keyword, resp in responses.items():
            if keyword in message.lower():
                response_text = resp
                break
        
        return jsonify({
            'success': True,
            'response': response_text,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ========================================
# Initialize Database
# ========================================

def init_database():
    """Create tables and default users"""
    with app.app_context():
        db.create_all()
        
        # Create default admin user if not exists
        if not User.query.filter_by(email='admin@example.com').first():
            admin = User(
                email='admin@example.com',
                username='admin',
                role='admin'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("✅ Default admin created: admin@example.com / admin123")
        
        # Create default test user
        if not User.query.filter_by(email='user@example.com').first():
            user = User(
                email='user@example.com',
                username='testuser',
                role='user'
            )
            user.set_password('user123')
            db.session.add(user)
            db.session.commit()
            print("✅ Default user created: user@example.com / user123")

# ========================================
# Run Application
# ========================================

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Mental Health Chatbot - Backend API")
    print("=" * 60)
    
    # Initialize database
    init_database()
    
    print(f"✅ Server: http://localhost:5000")
    print(f"✅ API Endpoints:")
    print(f"   POST /api/auth/register - Create account")
    print(f"   POST /api/auth/login - Login")
    print(f"   POST /api/chat/message - Chat with AI")
    print(f"\n👤 Test Accounts:")
    print(f"   Admin: admin@example.com / admin123")
    print(f"   User:  user@example.com / user123")
    print("=" * 60)
    print("\nPress Ctrl+C to stop the server\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
