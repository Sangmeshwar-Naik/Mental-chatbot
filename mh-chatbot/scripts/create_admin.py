"""
Create Admin User Script
Usage: python create_admin.py
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend-flask')))

from app import create_app
from backend.extensions import db
from backend.models import User, UserRole

def create_admin():
    """Create an admin user"""
    app = create_app()
    
    with app.app_context():
        print("=== Create Admin User ===\n")
        
        email = input("Admin email: ").strip()
        username = input("Admin username: ").strip()
        password = input("Admin password: ").strip()
        
        # Check if user already exists
        if User.query.filter_by(email=email).first():
            print(f"\n❌ Error: User with email '{email}' already exists!")
            return
        
        if User.query.filter_by(username=username).first():
            print(f"\n❌ Error: User with username '{username}' already exists!")
            return
        
        # Create admin user
        admin = User(
            email=email,
            username=username,
            role=UserRole.ADMIN,
            is_active=True,
            is_verified=True
        )
        admin.set_password(password)
        
        try:
            db.session.add(admin)
            db.session.commit()
            print(f"\n✅ Admin user created successfully!")
            print(f"Email: {email}")
            print(f"Username: {username}")
            print(f"Role: {admin.role.value}")
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error creating admin user: {e}")


if __name__ == '__main__':
    create_admin()
