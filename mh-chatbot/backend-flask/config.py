import os
from datetime import timedelta


class Config:
    """Base configuration"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-CHANGE-IN-PRODUCTION')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT Settings
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-CHANGE-IN-PRODUCTION')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 1)))
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=int(os.getenv('JWT_REFRESH_TOKEN_EXPIRES', 30)))
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///mental_health.db')
    
    # Redis
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # Celery
    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
    
    # AI Provider
    AI_PROVIDER = os.getenv('AI_PROVIDER', 'gemini')
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')
    GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')
    
    # AI Model Settings
    AI_MODEL_NAME = os.getenv('AI_MODEL_NAME', 'gemini-1.5-pro')
    AI_TEMPERATURE = float(os.getenv('AI_TEMPERATURE', 0.7))
    AI_MAX_TOKENS = int(os.getenv('AI_MAX_TOKENS', 2048))
    AI_STREAMING = os.getenv('AI_STREAMING', 'True').lower() == 'true'
    
    # Crisis Detection
    CRISIS_KEYWORDS = os.getenv('CRISIS_KEYWORDS', 'suicide,kill myself,end my life,self-harm').split(',')
    CRISIS_HOTLINE_US = os.getenv('CRISIS_HOTLINE_US', '988')
    CRISIS_HOTLINE_INTERNATIONAL = os.getenv('CRISIS_HOTLINE_INTERNATIONAL', '+1-800-273-8255')
    ADMIN_ALERT_EMAIL = os.getenv('ADMIN_ALERT_EMAIL', 'admin@example.com')
    
    # Email
    MAIL_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('SMTP_PORT', 587))
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv('SMTP_USERNAME', '')
    MAIL_PASSWORD = os.getenv('SMTP_PASSWORD', '')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_FROM', 'noreply@mentalhealth.app')
    
    # Twilio (Optional)
    TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID', '')
    TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN', '')
    TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER', '')
    
    # Rate Limiting
    RATELIMIT_ENABLED = os.getenv('RATE_LIMIT_ENABLED', 'True').lower() == 'true'
    RATELIMIT_DEFAULT = os.getenv('RATE_LIMIT_DEFAULT', '100 per hour')
    RATELIMIT_STORAGE_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # Uploads
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_UPLOAD_SIZE', 5 * 1024 * 1024))  # 5MB default
    
    # Vector DB
    VECTOR_DB_TYPE = os.getenv('VECTOR_DB_TYPE', 'chroma')
    VECTOR_DB_PATH = os.getenv('VECTOR_DB_PATH', './chroma_db')
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/app.log')


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False


class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    
    # Override with stronger requirements for production
    @property
    def SECRET_KEY(self):
        secret = os.getenv('SECRET_KEY')
        if not secret or secret == 'dev-secret-key-CHANGE-IN-PRODUCTION':
            raise ValueError('SECRET_KEY must be set in production!')
        return secret
    
    @property
    def JWT_SECRET_KEY(self):
        secret = os.getenv('JWT_SECRET_KEY')
        if not secret or secret == 'jwt-secret-CHANGE-IN-PRODUCTION':
            raise ValueError('JWT_SECRET_KEY must be set in production!')
        return secret


# Config dictionary
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
