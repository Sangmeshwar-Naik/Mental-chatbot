"""
Mental Health Screening Routes - PHQ-9, GAD-7, etc.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

from backend.extensions import db
from backend.models import User, ScreeningResult

screenings_bp = Blueprint('screenings', __name__)


# PHQ-9 Depression Screening
PHQ9_QUESTIONS = [
    "Little interest or pleasure in doing things",
    "Feeling down, depressed, or hopeless",
    "Trouble falling or staying asleep, or sleeping too much",
    "Feeling tired or having little energy",
    "Poor appetite or overeating",
    "Feeling bad about yourself or that you are a failure",
    "Trouble concentrating on things",
    "Moving or speaking slowly, or being fidgety/restless",
    "Thoughts that you would be better off dead or of hurting yourself"
]

GAD7_QUESTIONS = [
    "Feeling nervous, anxious, or on edge",
    "Not being able to stop or control worrying",
    "Worrying too much about different things",
    "Trouble relaxing",
    "Being so restless that it is hard to sit still",
    "Becoming easily annoyed or irritable",
    "Feeling afraid as if something awful might happen"
]


def interpret_phq9(score):
    """Interpret PHQ-9 score"""
    if score >= 20:
        return "Severe depression", "Immediate professional help strongly recommended"
    elif score >= 15:
        return "Moderately severe depression", "Professional treatment recommended"
    elif score >= 10:
        return "Moderate depression", "Consider professional counseling or therapy"
    elif score >= 5:
        return "Mild depression", "Monitor symptoms, consider self-care strategies"
    else:
        return "Minimal depression", "No treatment indicated, maintain healthy habits"


def interpret_gad7(score):
    """Interpret GAD-7 score"""
    if score >= 15:
        return "Severe anxiety", "Professional treatment strongly recommended"
    elif score >= 10:
        return "Moderate anxiety", "Consider professional counseling"
    elif score >= 5:
        return "Mild anxiety", "Monitor symptoms, practice relaxation techniques"
    else:
        return "Minimal anxiety", "No treatment indicated"


@screenings_bp.route('/phq9', methods=['POST'])
@jwt_required()
def submit_phq9():
    """Submit PHQ-9 depression screening"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    responses = data.get('responses', [])
    
    if len(responses) != 9:
        return jsonify({'error': 'PHQ-9 requires 9 responses (0-3 each)'}), 400
    
    # Validate responses (0-3 scale)
    if not all(isinstance(r, int) and 0 <= r <= 3 for r in responses):
        return jsonify({'error': 'Each response must be 0-3'}), 400
    
    # Calculate total score
    total_score = sum(responses)
    severity, recommendation = interpret_phq9(total_score)
    
    # Create screening result
    screening = ScreeningResult(
        user_id=current_user_id,
        screening_type='PHQ-9',
        total_score=total_score,
        severity_level=severity,
        responses={'answers': responses},
        interpretation=f"Score: {total_score}/27 - {severity}",
        recommendations=recommendation
    )
    
    db.session.add(screening)
    
    # Update user risk level based on severity
    from backend.models import RiskLevel
    if total_score >= 20:
        user.current_risk_level = RiskLevel.HIGH
    elif total_score >= 15:
        user.current_risk_level = RiskLevel.MODERATE
    else:
        user.current_risk_level = RiskLevel.LOW
    
    user.last_risk_assessment = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({
        'message': 'PHQ-9 screening completed',
        'result': screening.to_dict(),
        'questions': PHQ9_QUESTIONS
    }), 201


@screenings_bp.route('/gad7', methods=['POST'])
@jwt_required()
def submit_gad7():
    """Submit GAD-7 anxiety screening"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    responses = data.get('responses', [])
    
    if len(responses) != 7:
        return jsonify({'error': 'GAD-7 requires 7 responses (0-3 each)'}), 400
    
    # Validate responses
    if not all(isinstance(r, int) and 0 <= r <= 3 for r in responses):
        return jsonify({'error': 'Each response must be 0-3'}), 400
    
    # Calculate total score
    total_score = sum(responses)
    severity, recommendation = interpret_gad7(total_score)
    
    # Create screening result
    screening = ScreeningResult(
        user_id=current_user_id,
        screening_type='GAD-7',
        total_score=total_score,
        severity_level=severity,
        responses={'answers': responses},
        interpretation=f"Score: {total_score}/21 - {severity}",
        recommendations=recommendation
    )
    
    db.session.add(screening)
    db.session.commit()
    
    return jsonify({
        'message': 'GAD-7 screening completed',
        'result': screening.to_dict(),
        'questions': GAD7_QUESTIONS
    }), 201


@screenings_bp.route('/history', methods=['GET'])
@jwt_required()
def get_screening_history():
    """Get all screening results for user"""
    current_user_id = get_jwt_identity()
    
    screenings = ScreeningResult.query.filter_by(
        user_id=current_user_id
    ).order_by(ScreeningResult.completed_at.desc()).all()
    
    return jsonify({
        'screenings': [s.to_dict() for s in screenings],
        'total_count': len(screenings)
    }), 200


@screenings_bp.route('/questions', methods=['GET'])
@jwt_required()
def get_screening_questions():
    """Get screening questions for a specific type"""
    screening_type = request.args.get('type', 'phq9').lower()
    
    if screening_type == 'phq9':
        return jsonify({
            'type': 'PHQ-9',
            'name': 'Patient Health Questionnaire-9',
            'description': 'Depression screening tool',
            'questions': PHQ9_QUESTIONS,
            'scale': {
                '0': 'Not at all',
                '1': 'Several days',
                '2': 'More than half the days',
                '3': 'Nearly every day'
            }
        }), 200
    elif screening_type == 'gad7':
        return jsonify({
            'type': 'GAD-7',
            'name': 'Generalized Anxiety Disorder-7',
            'description': 'Anxiety screening tool',
            'questions': GAD7_QUESTIONS,
            'scale': {
                '0': 'Not at all',
                '1': 'Several days',
                '2': 'More than half the days',
                '3': 'Nearly every day'
            }
        }), 200
    else:
        return jsonify({'error': 'Invalid screening type'}), 400
