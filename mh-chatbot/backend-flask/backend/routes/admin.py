"""
Admin Routes - Dashboard, user moderation, crisis intervention
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta

from backend.extensions import db
from backend.models import User, UserRole, Conversation, Message, AdminNote, RiskLevel

admin_bp = Blueprint('admin', __name__)


def admin_required(fn):
    """Decorator to require admin role"""
    @jwt_required()
    def wrapper(*args, **kwargs):
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role not in [UserRole.ADMIN, UserRole.CLINICIAN]:
            return jsonify({'error': 'Admin access required'}), 403
        
        return fn(*args, **kwargs)
    
    wrapper.__name__ = fn.__name__
    return wrapper


@admin_bp.route('/dashboard', methods=['GET'])
@admin_required
def get_admin_dashboard():
    """Get admin dashboard statistics"""
    
    # Total users
    total_users = User.query.filter_by(role=UserRole.USER).count()
    
    # Active users (logged in last 7 days)
    week_ago = datetime.utcnow() - timedelta(days=7)
    active_users = User.query.filter(
        User.last_login >= week_ago,
        User.role == UserRole.USER
    ).count()
    
    # High-risk users
    high_risk_users = User.query.filter(
        User.current_risk_level.in_([RiskLevel.HIGH, RiskLevel.CRITICAL]),
        User.role == UserRole.USER
    ).count()
    
    # Flagged conversations
    flagged_conversations = Conversation.query.filter_by(is_flagged=True).count()
    
    # Crisis conversations (last 24 hours)
    day_ago = datetime.utcnow() - timedelta(days=1)
    crisis_conversations = Conversation.query.filter(
        Conversation.crisis_detected == True,
        Conversation.created_at >= day_ago
    ).count()
    
    # Total conversations
    total_conversations = Conversation.query.count()
    
    # Total messages
    total_messages = Message.query.count()
    
    return jsonify({
        'statistics': {
            'total_users': total_users,
            'active_users': active_users,
            'high_risk_users': high_risk_users,
            'flagged_conversations': flagged_conversations,
            'crisis_conversations_24h': crisis_conversations,
            'total_conversations': total_conversations,
            'total_messages': total_messages
        }
    }), 200


@admin_bp.route('/flagged-conversations', methods=['GET'])
@admin_required
def get_flagged_conversations():
    """Get all flagged conversations requiring attention"""
    
    flagged = Conversation.query.filter_by(is_flagged=True).order_by(
        Conversation.updated_at.desc()
    ).all()
    
    result = []
    for conv in flagged:
        user = User.query.get(conv.user_id)
        result.append({
            'conversation': conv.to_dict(),
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'current_risk_level': user.current_risk_level.value if user.current_risk_level else None
            }
        })
    
    return jsonify({'flagged_conversations': result}), 200


@admin_bp.route('/high-risk-users', methods=['GET'])
@admin_required
def get_high_risk_users():
    """Get users with high or critical risk levels"""
    
    high_risk_users = User.query.filter(
        User.current_risk_level.in_([RiskLevel.HIGH, RiskLevel.CRITICAL]),
        User.role == UserRole.USER
    ).order_by(User.last_risk_assessment.desc()).all()
    
    result = []
    for user in high_risk_users:
        # Get latest conversation
        latest_conv = Conversation.query.filter_by(
            user_id=user.id
        ).order_by(Conversation.updated_at.desc()).first()
        
        result.append({
            'user': user.to_dict(),
            'latest_conversation_id': latest_conv.id if latest_conv else None,
            'last_assessment': user.last_risk_assessment.isoformat() if user.last_risk_assessment else None
        })
    
    return jsonify({'high_risk_users': result}), 200


@admin_bp.route('/user/<int:user_id>/conversations', methods=['GET'])
@admin_required
def get_user_conversations(user_id):
    """Get all conversations for a specific user"""
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    conversations = Conversation.query.filter_by(user_id=user_id).order_by(
        Conversation.updated_at.desc()
    ).all()
    
    return jsonify({
        'user': user.to_dict(),
        'conversations': [conv.to_dict() for conv in conversations]
    }), 200


@admin_bp.route('/conversation/<int:conversation_id>/messages', methods=['GET'])
@admin_required
def get_conversation_messages(conversation_id):
    """Get all messages in a conversation (admin review)"""
    
    conversation = Conversation.query.get(conversation_id)
    if not conversation:
        return jsonify({'error': 'Conversation not found'}), 404
    
    messages = Message.query.filter_by(conversation_id=conversation_id).order_by(
        Message.created_at
    ).all()
    
    user = User.query.get(conversation.user_id)
    
    return jsonify({
        'conversation': conversation.to_dict(),
        'user': user.to_dict(),
        'messages': [msg.to_dict() for msg in messages]
    }), 200


@admin_bp.route('/note', methods=['POST'])
@admin_required
def add_admin_note():
    """Add admin note about a user"""
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    user_id = data.get('user_id')
    note_text = data.get('note')
    note_type = data.get('note_type', 'observation')
    is_critical = data.get('is_critical', False)
    
    if not user_id or not note_text:
        return jsonify({'error': 'User ID and note required'}), 400
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    admin_note = AdminNote(
        user_id=user_id,
        admin_id=current_user_id,
        note=note_text,
        note_type=note_type,
        is_critical=is_critical
    )
    
    db.session.add(admin_note)
    db.session.commit()
    
    return jsonify({
        'message': 'Admin note added successfully',
        'note': admin_note.to_dict()
    }), 201


@admin_bp.route('/user/<int:user_id>/notes', methods=['GET'])
@admin_required
def get_user_notes(user_id):
    """Get all admin notes for a user"""
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    notes = AdminNote.query.filter_by(user_id=user_id).order_by(
        AdminNote.created_at.desc()
    ).all()
    
    return jsonify({
        'user': user.to_dict(),
        'notes': [note.to_dict() for note in notes]
    }), 200


@admin_bp.route('/user/<int:user_id>/status', methods=['PUT'])
@admin_required
def update_user_status(user_id):
    """Update user account status (activate/deactivate)"""
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    
    if 'is_active' in data:
        user.is_active = data['is_active']
    
    db.session.commit()
    
    return jsonify({
        'message': 'User status updated',
        'user': user.to_dict()
    }), 200
