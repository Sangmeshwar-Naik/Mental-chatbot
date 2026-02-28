"""
User Routes - Profile management, mood logging
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, date

from backend.extensions import db
from backend.models import User, MoodLog

user_bp = Blueprint('user', __name__)


@user_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get user profile"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify(user.to_dict()), 200


@user_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update user profile"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    
    # Update allowed fields
    if 'first_name' in data:
        user.first_name = data['first_name']
    if 'last_name' in data:
        user.last_name = data['last_name']
    if 'age' in data:
        user.age = data['age']
    if 'timezone' in data:
        user.timezone = data['timezone']
    if 'language' in data:
        user.language = data['language']
    if 'email_notifications' in data:
        user.email_notifications = data['email_notifications']
    
    user.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        'message': 'Profile updated successfully',
        'user': user.to_dict()
    }), 200


@user_bp.route('/mood', methods=['POST'])
@jwt_required()
def log_mood():
    """Log daily mood"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    mood_score = data.get('mood_score')
    
    if not mood_score or mood_score < 1 or mood_score > 10:
        return jsonify({'error': 'Mood score must be between 1 and 10'}), 400
    
    today = date.today()
    
    # Check if mood already logged today
    existing_log = MoodLog.query.filter_by(
        user_id=current_user_id,
        log_date=today
    ).first()
    
    if existing_log:
        # Update existing log
        existing_log.mood_score = mood_score
        existing_log.mood_label = data.get('mood_label')
        existing_log.notes = data.get('notes')
        existing_log.sleep_hours = data.get('sleep_hours')
        existing_log.exercise_minutes = data.get('exercise_minutes')
        existing_log.social_interaction = data.get('social_interaction')
        mood_log = existing_log
    else:
        # Create new log
        mood_log = MoodLog(
            user_id=current_user_id,
            mood_score=mood_score,
            mood_label=data.get('mood_label'),
            notes=data.get('notes'),
            sleep_hours=data.get('sleep_hours'),
            exercise_minutes=data.get('exercise_minutes'),
            social_interaction=data.get('social_interaction'),
            log_date=today
        )
        db.session.add(mood_log)
    
    db.session.commit()
    
    return jsonify({
        'message': 'Mood logged successfully',
        'mood_log': mood_log.to_dict()
    }), 200


@user_bp.route('/mood-history', methods=['GET'])
@jwt_required()
def get_mood_history():
    """Get mood history with optional date range"""
    current_user_id = get_jwt_identity()
    
    # Optional query parameters
    days = request.args.get('days', 30, type=int)
    
    mood_logs = MoodLog.query.filter_by(
        user_id=current_user_id
    ).order_by(MoodLog.log_date.desc()).limit(days).all()
    
    # Calculate statistics
    if mood_logs:
        scores = [log.mood_score for log in mood_logs]
        avg_mood = sum(scores) / len(scores)
        min_mood = min(scores)
        max_mood = max(scores)
    else:
        avg_mood = min_mood = max_mood = None
    
    return jsonify({
        'mood_logs': [log.to_dict() for log in mood_logs],
        'statistics': {
            'average_mood': avg_mood,
            'min_mood': min_mood,
            'max_mood': max_mood,
            'total_entries': len(mood_logs)
        }
    }), 200


@user_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard():
    """Get user dashboard summary"""
    current_user_id = get_jwt_identity()
    
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Get recent mood logs (last 7 days)
    from datetime import timedelta
    week_ago = date.today() - timedelta(days=7)
    recent_moods = MoodLog.query.filter(
        MoodLog.user_id == current_user_id,
        MoodLog.log_date >= week_ago
    ).order_by(MoodLog.log_date.desc()).all()
    
    # Get conversation stats
    from backend.models import Conversation
    conversation_count = Conversation.query.filter_by(
        user_id=current_user_id,
        is_active=True
    ).count()
    
    # Get screening stats
    from backend.models import ScreeningResult
    last_screening = ScreeningResult.query.filter_by(
        user_id=current_user_id
    ).order_by(ScreeningResult.completed_at.desc()).first()
    
    return jsonify({
        'user': user.to_dict(),
        'recent_moods': [mood.to_dict() for mood in recent_moods],
        'conversation_count': conversation_count,
        'last_screening': last_screening.to_dict() if last_screening else None,
        'current_risk_level': user.current_risk_level.value if user.current_risk_level else 'low'
    }), 200
