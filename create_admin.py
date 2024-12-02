import os
import sys
from app import create_app, db
from app.models import User

def create_admin_user(username, email, password):
    """Create or update an admin user"""
    try:
        # Create Flask application context
        app = create_app()
        with app.app_context():
            # Check if user already exists
            user = User.query.filter((User.username == username) | (User.email == email)).first()
            
            if user:
                # Update existing user
                user.username = username
                user.email = email
                user.set_password(password)
                user.is_admin = True
                print(f"Updating existing user: {username}")
            else:
                # Create new user
                user = User(username=username, email=email, is_admin=True)
                user.set_password(password)
                db.session.add(user)
                print(f"Creating new admin user: {username}")
            
            # Commit changes
            db.session.commit()
            print("Admin user created/updated successfully!")
            
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    # Default admin credentials
    admin_username = "admin"
    admin_email = "admin@gmail.com"
    admin_password = "admin"

    # Allow command line arguments to override defaults
    if len(sys.argv) > 1:
        admin_username = sys.argv[1]
    if len(sys.argv) > 2:
        admin_email = sys.argv[2]
    if len(sys.argv) > 3:
        admin_password = sys.argv[3]

    create_admin_user(admin_username, admin_email, admin_password)