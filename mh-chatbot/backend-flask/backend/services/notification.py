"""
Notification Service - Email and SMS alerts
"""
from flask import current_app
from flask_mail import Message
from backend.extensions import mail


class NotificationService:
    """Handle email and SMS notifications"""
    
    def send_email(self, to: str, subject: str, body: str, html: str = None):
        """Send email notification"""
        try:
            msg = Message(
                subject=subject,
                recipients=[to],
                body=body,
                html=html or body
            )
            mail.send(msg)
            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
    
    def send_crisis_alert(self, user_email: str, user_id: int, risk_level: str):
        """Send crisis alert to admin"""
        admin_email = current_app.config.get('ADMIN_ALERT_EMAIL')
        
        subject = f"URGENT: Crisis Alert - User ID {user_id}"
        body = f"""
        CRISIS ALERT
        
        User ID: {user_id}
        User Email: {user_email}
        Risk Level: {risk_level}
        Timestamp: {datetime.utcnow().isoformat()}
        
        Immediate review required.
        Please check the admin dashboard for details.
        """
        
        self.send_email(admin_email, subject, body)
        
        # Optional: Send SMS via Twilio
        if current_app.config.get('TWILIO_ACCOUNT_SID'):
            self.send_sms_alert(user_id, risk_level)
    
    def send_sms_alert(self, user_id: int, risk_level: str):
        """Send SMS alert via Twilio"""
        try:
            from twilio.rest import Client
            
            account_sid = current_app.config.get('TWILIO_ACCOUNT_SID')
            auth_token = current_app.config.get('TWILIO_AUTH_TOKEN')
            from_number = current_app.config.get('TWILIO_PHONE_NUMBER')
            
            client = Client(account_sid, auth_token)
            
            message = client.messages.create(
                body=f"CRISIS ALERT: User {user_id} - Risk Level: {risk_level}. Check dashboard.",
                from_=from_number,
                to=current_app.config.get('ADMIN_PHONE_NUMBER')  # Need to add this config
            )
            
            return True
        except Exception as e:
            print(f"Error sending SMS: {e}")
            return False
    
    def send_mood_reminder(self, user_email: str, username: str):
        """Send daily mood logging reminder"""
        subject = "Daily Mood Check-in Reminder"
        body = f"""
        Hi {username},
        
        This is your friendly reminder to log your mood for today.
        
        Taking a moment to check in with yourself is an important part of self-care.
        
        Log in to track your mood: [Your App URL]
        
        Take care,
        Mental Health Support Team
        """
        
        return self.send_email(user_email, subject, body)
    
    def send_screening_reminder(self, user_email: str, username: str):
        """Send screening reminder"""
        subject = "Mental Health Screening Reminder"
        body = f"""
        Hi {username},
        
        It's been a while since your last mental health screening.
        
        Regular check-ins help track your progress and identify areas where you might need support.
        
        Complete a quick screening: [Your App URL]
        
        Best regards,
        Mental Health Support Team
        """
        
        return self.send_email(user_email, subject, body)


from datetime import datetime

# Singleton instance
_notification_service = None


def get_notification_service() -> NotificationService:
    """Get or create notification service singleton"""
    global _notification_service
    if _notification_service is None:
        _notification_service = NotificationService()
    return _notification_service
