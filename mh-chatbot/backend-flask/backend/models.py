"""
Database models for Mental Health Chatbot Platform
"""
from datetime import datetime
from backend.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
import enum


class UserRole(enum.Enum):
    """User role enumeration"""
    USER = "user"
    ADMIN = "admin"
    CLINICIAN = "clinician"


class RiskLevel(enum.Enum):
    """Risk assessment level"""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class User(db.Model):
    """User account model"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum(UserRole), default=UserRole.USER, nullable=False)
    
    # Profile Information
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    age = db.Column(db.Integer)
    timezone = db.Column(db.String(50), default='UTC')
    language = db.Column(db.String(10), default='en')
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    email_notifications = db.Column(db.Boolean, default=True)
    
    # Risk Assessment
    current_risk_level = db.Column(db.Enum(RiskLevel), default=RiskLevel.LOW)
    last_risk_assessment = db.Column(db.DateTime)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    conversations = db.relationship('Conversation', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    mood_logs = db.relationship('MoodLog', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    screening_results = db.relationship('ScreeningResult', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    admin_notes = db.relationship('AdminNote', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert user to dictionary"""
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'role': self.role.value,
            'is_active': self.is_active,
            'current_risk_level': self.current_risk_level.value if self.current_risk_level else None,
            'created_at': self.created_at.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None
        }


class Conversation(db.Model):
    """Chat conversation model"""
    __tablename__ = 'conversations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    title = db.Column(db.String(200), default='New Conversation')
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    is_flagged = db.Column(db.Boolean, default=False)
    flag_reason = db.Column(db.Text)
    
    # Risk tracking
    max_risk_level = db.Column(db.Enum(RiskLevel), default=RiskLevel.LOW)
    crisis_detected = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    messages = db.relationship('Message', backref='conversation', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert conversation to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'is_active': self.is_active,
            'is_flagged': self.is_flagged,
            'crisis_detected': self.crisis_detected,
            'max_risk_level': self.max_risk_level.value if self.max_risk_level else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'message_count': self.messages.count()
        }


class Message(db.Model):
    """Individual message model"""
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversations.id'), nullable=False, index=True)
    role = db.Column(db.String(20), nullable=False)  # 'user' or 'assistant'
    content = db.Column(db.Text, nullable=False)
    
    # AI Metadata
    model_used = db.Column(db.String(50))
    tokens_used = db.Column(db.Integer)
    
    # Sentiment & Risk Analysis
    sentiment_score = db.Column(db.Float)  # -1 to 1
    risk_level = db.Column(db.Enum(RiskLevel))
    contains_crisis_keywords = db.Column(db.Boolean, default=False)
    
    # Feedback
    user_feedback = db.Column(db.Integer)  # 1-5 rating
    feedback_comment = db.Column(db.Text)
    
    # Timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def to_dict(self):
        """Convert message to dictionary"""
        return {
            'id': self.id,
            'conversation_id': self.conversation_id,
            'role': self.role,
            'content': self.content,
            'sentiment_score': self.sentiment_score,
            'risk_level': self.risk_level.value if self.risk_level else None,
            'created_at': self.created_at.isoformat()
        }


class MoodLog(db.Model):
    """Daily mood tracking"""
    __tablename__ = 'mood_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Mood data
    mood_score = db.Column(db.Integer, nullable=False)  # 1-10 scale
    mood_label = db.Column(db.String(50))  # happy, sad, anxious, etc.
    notes = db.Column(db.Text)
    
    # Context
    sleep_hours = db.Column(db.Float)
    exercise_minutes = db.Column(db.Integer)
    social_interaction = db.Column(db.Boolean)
    
    # Timestamp
    log_date = db.Column(db.Date, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'log_date', name='unique_user_date'),
    )
    
    def to_dict(self):
        """Convert mood log to dictionary"""
        return {
            'id': self.id,
            'mood_score': self.mood_score,
            'mood_label': self.mood_label,
            'notes': self.notes,
            'sleep_hours': self.sleep_hours,
            'exercise_minutes': self.exercise_minutes,
            'log_date': self.log_date.isoformat(),
            'created_at': self.created_at.isoformat()
        }


class ScreeningResult(db.Model):
    """Mental health screening results (PHQ-9, GAD-7, etc.)"""
    __tablename__ = 'screening_results'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Screening details
    screening_type = db.Column(db.String(50), nullable=False)  # PHQ-9, GAD-7, etc.
    total_score = db.Column(db.Integer, nullable=False)
    severity_level = db.Column(db.String(50))  # minimal, mild, moderate, severe
    responses = db.Column(db.JSON)  # Store individual question responses
    
    # Interpretation
    interpretation = db.Column(db.Text)
    recommendations = db.Column(db.Text)
    
    # Timestamp
    completed_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def to_dict(self):
        """Convert screening result to dictionary"""
        return {
            'id': self.id,
            'screening_type': self.screening_type,
            'total_score': self.total_score,
            'severity_level': self.severity_level,
            'responses': self.responses,
            'interpretation': self.interpretation,
            'completed_at': self.completed_at.isoformat()
        }


class AdminNote(db.Model):
    """Admin/Clinician notes about users"""
    __tablename__ = 'admin_notes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Note content
    note = db.Column(db.Text, nullable=False)
    note_type = db.Column(db.String(50))  # observation, intervention, followup
    is_critical = db.Column(db.Boolean, default=False)
    
    # Timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    admin = db.relationship('User', foreign_keys=[admin_id], backref='notes_created')
    
    def to_dict(self):
        """Convert admin note to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'admin_id': self.admin_id,
            'note': self.note,
            'note_type': self.note_type,
            'is_critical': self.is_critical,
            'created_at': self.created_at.isoformat()
        }
