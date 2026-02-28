"""
Flask Extensions Initialization
"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_cors import CORS

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
cors = CORS()

def init_extensions(app):
    """Initialize Flask extensions with app"""
    db.init_app(app)
    login_manager.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})
    
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please login to access this page.'
    
    @login_manager.user_loader
    def load_user(user_id):
        from backend.models import User
        return User.query.get(int(user_id))
    
    return app
