from flask import Flask, render_template, session
from models import db, Admin
from config import Config
from admin import admin_bp
from player import player_bp
from werkzeug.security import generate_password_hash
from datetime import timedelta

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(player_bp, url_prefix='/')

@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(days=7)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

def create_tables():
    with app.app_context():
        db.create_all()
        if not Admin.query.first():
            hashed_password = generate_password_hash('admin', method='pbkdf2:sha256')
            admin = Admin(username='admin', password=hashed_password)
            db.session.add(admin)
            db.session.commit()

if __name__ == '__main__':
    create_tables()
    app.run(debug=True)
