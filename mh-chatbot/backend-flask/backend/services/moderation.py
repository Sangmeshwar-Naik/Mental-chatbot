"""
Content Moderation and Crisis Detection Service
"""
import re
from typing import Dict, List, Tuple
from flask import current_app
from backend.models import RiskLevel


class ModerationService:
    """Content moderation and crisis keyword detection"""
    
    # Crisis keywords organized by severity
    CRITICAL_KEYWORDS = [
        'suicide', 'kill myself', 'end my life', 'want to die',
        'better off dead', 'take my own life', 'suicidal'
    ]
    
    HIGH_RISK_KEYWORDS = [
        'self-harm', 'cut myself', 'hurt myself', 'overdose',
        'pills', 'jump off', 'hang myself', 'end it all'
    ]
    
    MODERATE_RISK_KEYWORDS = [
        'hopeless', 'no point', 'give up', 'can\'t go on',
        'worthless', 'burden', 'better without me'
    ]
    
    # Positive coping keywords (reduce risk score)
    POSITIVE_KEYWORDS = [
        'therapy', 'counselor', 'better', 'improving', 'hope',
        'support', 'family', 'friends', 'grateful', 'thankful'
    ]
    
    def __init__(self):
        """Initialize moderation service"""
        self.crisis_keywords = current_app.config.get('CRISIS_KEYWORDS', [])
    
    def analyze_message(self, text: str) -> Dict:
        """
        Analyze message for crisis indicators and sentiment
        
        Args:
            text: Message text to analyze
        
        Returns:
            Dict with risk_level, crisis_detected, matched_keywords, sentiment
        """
        text_lower = text.lower()
        
        # Check for crisis keywords
        crisis_matches = []
        risk_score = 0
        
        # Critical keywords
        for keyword in self.CRITICAL_KEYWORDS:
            if keyword in text_lower:
                crisis_matches.append(keyword)
                risk_score += 10
        
        # High risk keywords
        for keyword in self.HIGH_RISK_KEYWORDS:
            if keyword in text_lower:
                crisis_matches.append(keyword)
                risk_score += 7
        
        # Moderate risk keywords
        for keyword in self.MODERATE_RISK_KEYWORDS:
            if keyword in text_lower:
                crisis_matches.append(keyword)
                risk_score += 3
        
        # Reduce score for positive keywords
        for keyword in self.POSITIVE_KEYWORDS:
            if keyword in text_lower:
                risk_score -= 2
        
        # Ensure non-negative
        risk_score = max(0, risk_score)
        
        # Determine risk level
        risk_level = self._calculate_risk_level(risk_score)
        crisis_detected = risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]
        
        # Simple sentiment analysis
        sentiment_score = self._analyze_sentiment(text_lower)
        
        return {
            'risk_level': risk_level,
            'risk_score': risk_score,
            'crisis_detected': crisis_detected,
            'matched_keywords': crisis_matches,
            'sentiment_score': sentiment_score,
            'requires_intervention': crisis_detected
        }
    
    def _calculate_risk_level(self, risk_score: int) -> RiskLevel:
        """Calculate risk level from risk score"""
        if risk_score >= 10:
            return RiskLevel.CRITICAL
        elif risk_score >= 7:
            return RiskLevel.HIGH
        elif risk_score >= 3:
            return RiskLevel.MODERATE
        else:
            return RiskLevel.LOW
    
    def _analyze_sentiment(self, text: str) -> float:
        """
        Simple sentiment analysis
        Returns: float between -1 (negative) and 1 (positive)
        """
        # Negative words
        negative_words = [
            'sad', 'depressed', 'anxious', 'worried', 'scared', 'afraid',
            'terrible', 'awful', 'horrible', 'bad', 'worse', 'hopeless',
            'lonely', 'alone', 'abandoned', 'rejected', 'failed', 'failure'
        ]
        
        # Positive words
        positive_words = [
            'happy', 'good', 'great', 'better', 'wonderful', 'amazing',
            'grateful', 'thankful', 'proud', 'excited', 'hopeful', 'optimistic',
            'love', 'joy', 'peace', 'calm', 'relaxed', 'confident'
        ]
        
        # Count occurrences
        negative_count = sum(1 for word in negative_words if word in text)
        positive_count = sum(1 for word in positive_words if word in text)
        
        # Calculate sentiment score
        total_words = len(text.split())
        if total_words == 0:
            return 0.0
        
        sentiment = (positive_count - negative_count) / max(total_words, 1)
        
        # Normalize to [-1, 1]
        return max(-1.0, min(1.0, sentiment * 10))
    
    def get_crisis_response(self, risk_level: RiskLevel) -> Dict:
        """
        Get appropriate crisis response based on risk level
        
        Args:
            risk_level: Risk level assessment
        
        Returns:
            Dict with message and resources
        """
        if risk_level == RiskLevel.CRITICAL:
            return {
                'message': (
                    "I'm deeply concerned about what you've shared. Your safety is the top priority. "
                    "Please reach out to a crisis counselor immediately. They are available 24/7 and "
                    "want to help you through this."
                ),
                'hotlines': {
                    'US': '988 (Suicide & Crisis Lifeline)',
                    'International': '+1-800-273-8255',
                    'Crisis Text Line': 'Text HOME to 741741'
                },
                'immediate_actions': [
                    'Call 988 or your local emergency number',
                    'Go to the nearest emergency room',
                    'Call a trusted friend or family member',
                    'Remove any means of self-harm from your immediate environment'
                ],
                'notify_admin': True
            }
        
        elif risk_level == RiskLevel.HIGH:
            return {
                'message': (
                    "I hear that you're going through a really difficult time. It's important to "
                    "talk to someone who can provide immediate support. Please consider reaching out "
                    "to a crisis counselor or mental health professional."
                ),
                'hotlines': {
                    'US': '988 (Suicide & Crisis Lifeline)',
                    'International': '+1-800-273-8255'
                },
                'immediate_actions': [
                    'Contact a mental health professional',
                    'Reach out to a trusted friend or family member',
                    'Call a crisis hotline for immediate support'
                ],
                'notify_admin': True
            }
        
        elif risk_level == RiskLevel.MODERATE:
            return {
                'message': (
                    "It sounds like you're dealing with some challenging feelings. I'm here to listen. "
                    "Have you considered talking to a counselor or therapist about what you're experiencing?"
                ),
                'resources': [
                    'Consider scheduling an appointment with a mental health professional',
                    'Practice self-care activities that help you feel grounded',
                    'Reach out to supportive people in your life'
                ],
                'notify_admin': False
            }
        
        else:  # LOW
            return {
                'message': "I'm here to support you. How can I help?",
                'notify_admin': False
            }
    
    def should_notify_admin(self, risk_level: RiskLevel) -> bool:
        """Determine if admin should be notified"""
        return risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]


# Singleton instance
_moderation_service = None


def get_moderation_service() -> ModerationService:
    """Get or create moderation service singleton"""
    global _moderation_service
    if _moderation_service is None:
        _moderation_service = ModerationService()
    return _moderation_service
