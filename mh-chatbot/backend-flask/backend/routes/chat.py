"""
Chat Routes - Message sending, conversation management
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

from backend.extensions import db, limiter
from backend.models import User, Conversation, Message, RiskLevel
from backend.services.ai_connector import get_ai_connector
from backend.services.moderation import get_moderation_service

chat_bp = Blueprint('chat', __name__)


@chat_bp.route('/message', methods=['POST'])
@jwt_required()
@limiter.limit("30 per minute")
def send_message():
    """Send a message and get AI response"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    message_content = data.get('message', '').strip()
    conversation_id = data.get('conversation_id')
    
    if not message_content:
        return jsonify({'error': 'Message content required'}), 400
    
    # Get or create conversation
    if conversation_id:
        conversation = Conversation.query.filter_by(
            id=conversation_id,
            user_id=current_user_id
        ).first()
        if not conversation:
            return jsonify({'error': 'Conversation not found'}), 404
    else:
        # Create new conversation
        conversation = Conversation(
            user_id=current_user_id,
            title=message_content[:100]  # Use first message as title
        )
        db.session.add(conversation)
        db.session.flush()  # Get conversation ID
    
    # Analyze user message for crisis indicators
    moderation_service = get_moderation_service()
    moderation_result = moderation_service.analyze_message(message_content)
    
    # Create user message
    user_message = Message(
        conversation_id=conversation.id,
        role='user',
        content=message_content,
        sentiment_score=moderation_result['sentiment_score'],
        risk_level=moderation_result['risk_level'],
        contains_crisis_keywords=moderation_result['crisis_detected']
    )
    db.session.add(user_message)
    
    # Update conversation risk level
    if moderation_result['risk_level'].value > (conversation.max_risk_level or RiskLevel.LOW).value:
        conversation.max_risk_level = moderation_result['risk_level']
        conversation.is_flagged = moderation_result['crisis_detected']
        conversation.crisis_detected = moderation_result['crisis_detected']
    
    # Update user risk level
    if moderation_result['risk_level'].value > (user.current_risk_level or RiskLevel.LOW).value:
        user.current_risk_level = moderation_result['risk_level']
        user.last_risk_assessment = datetime.utcnow()
    
    # Build conversation history for AI
    messages = Message.query.filter_by(conversation_id=conversation.id).order_by(Message.created_at).all()
    conversation_history = [
        {'role': msg.role, 'content': msg.content}
        for msg in messages
    ]
    conversation_history.append({'role': 'user', 'content': message_content})
    
    # Get AI response
    try:
        ai_connector = get_ai_connector()
        
        # Check if crisis response is needed
        if moderation_result['crisis_detected']:
            crisis_response = moderation_service.get_crisis_response(moderation_result['risk_level'])
            ai_response_content = crisis_response['message']
            
            # Add crisis resources to response
            if 'hotlines' in crisis_response:
                ai_response_content += "\n\n**Crisis Resources:**\n"
                for name, number in crisis_response['hotlines'].items():
                    ai_response_content += f"- {name}: {number}\n"
            
            # Flag for admin notification
            if crisis_response.get('notify_admin'):
                # TODO: Implement admin notification (email/SMS)
                pass
            
            ai_response = {
                'content': ai_response_content,
                'model': 'crisis_intervention',
                'tokens_used': 0
            }
        else:
            # Normal AI response
            system_prompt = ai_connector.get_empathetic_system_prompt()
            ai_response = ai_connector.generate_response(
                messages=conversation_history,
                system_prompt=system_prompt
            )
        
        # Create assistant message
        assistant_message = Message(
            conversation_id=conversation.id,
            role='assistant',
            content=ai_response['content'],
            model_used=ai_response['model'],
            tokens_used=ai_response.get('tokens_used', 0)
        )
        db.session.add(assistant_message)
        
        # Commit all changes
        db.session.commit()
        
        return jsonify({
            'conversation_id': conversation.id,
            'user_message': user_message.to_dict(),
            'assistant_message': assistant_message.to_dict(),
            'crisis_detected': moderation_result['crisis_detected'],
            'risk_level': moderation_result['risk_level'].value
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to generate response', 'details': str(e)}), 500


@chat_bp.route('/conversations', methods=['GET'])
@jwt_required()
def get_conversations():
    """Get all conversations for current user"""
    current_user_id = get_jwt_identity()
    
    conversations = Conversation.query.filter_by(
        user_id=current_user_id,
        is_active=True
    ).order_by(Conversation.updated_at.desc()).all()
    
    return jsonify({
        'conversations': [conv.to_dict() for conv in conversations]
    }), 200


@chat_bp.route('/conversation/<int:conversation_id>', methods=['GET'])
@jwt_required()
def get_conversation(conversation_id):
    """Get a specific conversation with all messages"""
    current_user_id = get_jwt_identity()
    
    conversation = Conversation.query.filter_by(
        id=conversation_id,
        user_id=current_user_id
    ).first()
    
    if not conversation:
        return jsonify({'error': 'Conversation not found'}), 404
    
    messages = Message.query.filter_by(
        conversation_id=conversation_id
    ).order_by(Message.created_at).all()
    
    return jsonify({
        'conversation': conversation.to_dict(),
        'messages': [msg.to_dict() for msg in messages]
    }), 200


@chat_bp.route('/conversation/<int:conversation_id>', methods=['DELETE'])
@jwt_required()
def delete_conversation(conversation_id):
    """Delete a conversation"""
    current_user_id = get_jwt_identity()
    
    conversation = Conversation.query.filter_by(
        id=conversation_id,
        user_id=current_user_id
    ).first()
    
    if not conversation:
        return jsonify({'error': 'Conversation not found'}), 404
    
    conversation.is_active = False
    db.session.commit()
    
    return jsonify({'message': 'Conversation deleted successfully'}), 200


@chat_bp.route('/feedback', methods=['POST'])
@jwt_required()
def submit_feedback():
    """Submit feedback for an AI response"""
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    message_id = data.get('message_id')
    rating = data.get('rating')  # 1-5
    comment = data.get('comment')
    
    if not message_id or not rating:
        return jsonify({'error': 'Message ID and rating required'}), 400
    
    message = Message.query.filter_by(id=message_id, role='assistant').first()
    
    if not message:
        return jsonify({'error': 'Message not found'}), 404
    
    # Verify ownership
    conversation = Conversation.query.filter_by(
        id=message.conversation_id,
        user_id=current_user_id
    ).first()
    
    if not conversation:
        return jsonify({'error': 'Unauthorized'}), 403
    
    message.user_feedback = rating
    message.feedback_comment = comment
    db.session.commit()
    
    return jsonify({'message': 'Feedback submitted successfully'}), 200
