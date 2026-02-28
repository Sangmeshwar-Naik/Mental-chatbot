"""
Main Flask Application Factory
"""
import os
from flask import Flask, jsonify
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from config import config
from backend.extensions import init_extensions, db


def create_app(config_name=None):
    """Create and configure Flask application"""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    init_extensions(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Error handlers
    register_error_handlers(app)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        return jsonify({
            'status': 'healthy',
            'service': 'mental-health-chatbot-api',
            'version': '1.0.0'
        }), 200
    
    @app.route('/')
    def index():
        return jsonify({
            'message': 'Mental Health Chatbot API',
            'version': '1.0.0',
            'docs': '/api/docs'
        }), 200
    
    return app


def register_blueprints(app):
    """Register Flask blueprints"""
    from backend.routes.auth import auth_bp
    from backend.routes.user import user_bp
    from backend.routes.chat import chat_bp
    from backend.routes.screenings import screenings_bp
    from backend.routes.admin import admin_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(user_bp, url_prefix='/api/user')
    app.register_blueprint(chat_bp, url_prefix='/api/chat')
    app.register_blueprint(screenings_bp, url_prefix='/api/screenings')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')


def register_error_handlers(app):
    """Register error handlers"""
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'error': 'Bad request', 'message': str(error)}), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({'error': 'Unauthorized', 'message': 'Authentication required'}), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({'error': 'Forbidden', 'message': 'Insufficient permissions'}), 403
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found', 'message': 'Resource not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({'error': 'Internal server error', 'message': 'An unexpected error occurred'}), 500


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
