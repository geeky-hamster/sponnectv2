# create_admin.py
from app import app, Config
from models import db, User

if __name__ == '__main__':
    admin_username = Config.ADMIN_USERNAME
    admin_password = Config.ADMIN_PASSWORD
    
    with app.app_context():
        if not admin_username or not admin_password:
            print("Error: ADMIN_USERNAME/PASSWORD missing in .env")
        elif User.query.filter_by(username=admin_username, role='admin').first():
            print(f"Admin '{admin_username}' already exists.")
        else:
            admin_user = User(username=admin_username, role='admin', is_active=True, sponsor_approved=True)
            admin_user.set_password(admin_password)
            db.session.add(admin_user)
            db.session.commit()
            print(f"Admin user '{admin_username}' created.") 