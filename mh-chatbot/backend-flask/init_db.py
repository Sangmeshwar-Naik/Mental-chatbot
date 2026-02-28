"""
Initialize Database for Mental Health Chatbot
Creates tables and default admin user
"""
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from backend.extensions import db
from backend.models import User
from werkzeug.security import generate_password_hash

def init_database():
    """Initialize database with tables and default data"""
    app = create_app()
    
    with app.app_context():
        print("🗄️  Initializing database...")
        
        # Create all tables
        db.create_all()
        print("✅ Database tables created")
        
        # Check if admin user exists
        admin = User.query.filter_by(email='admin@example.com').first()
        if not admin:
            # Create default admin user
            admin = User(
                email='admin@example.com',
                username='admin',
                password_hash=generate_password_hash('admin123'),
                role='admin',
                is_active=True
            )
            db.session.add(admin)
            db.session.commit()
            print("✅ Default admin user created")
            print("   Email: admin@example.com")
            print("   Password: admin123")
        else:
            print("ℹ️  Admin user already exists")
        
        # Create test user
        test_user = User.query.filter_by(email='user@example.com').first()
        if not test_user:
            test_user = User(
                email='user@example.com',
                username='testuser',
                password_hash=generate_password_hash('user123'),
                role='user',
                is_active=True
            )
            db.session.add(test_user)
            db.session.commit()
            print("✅ Test user created")
            print("   Email: user@example.com")
            print("   Password: user123")
        else:
            print("ℹ️  Test user already exists")
        
        print("\n✅ Database initialization complete!")
        print("\n📝 You can login with:")
        print("   Admin: admin@example.com / admin123")
        print("   User:  user@example.com / user123")

if __name__ == '__main__':
    init_database()
