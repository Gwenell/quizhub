from werkzeug.security import generate_password_hash
from extensions import db
from models import Admin
from app import app

with app.app_context():
    if not Admin.query.first():
        hashed_password = generate_password_hash('admin', method='pbkdf2:sha256')
        admin = Admin(username='admin', password=hashed_password)
        db.session.add(admin)
        db.session.commit()
        print("Admin user created.")
    else:
        print("Admin user already exists.")
