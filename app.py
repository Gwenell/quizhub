from flask import Flask, render_template, session, redirect, url_for, request, flash, jsonify
from flask_babelex import Babel, _
from extensions import db
from models import Admin, Quiz, Player, QuizSession, Question
from config import Config
from admin import admin_bp
from player import player_bp
from werkzeug.security import generate_password_hash
from datetime import timedelta
import os
import random
from flask_migrate import Migrate

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize Babel for localization
babel = Babel(app)

# Initialize database
db.init_app(app)

# Initialize Flask-Migrate
migrate = Migrate(app, db)

# Register blueprints
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(player_bp, url_prefix='/')

# Set session to be permanent
@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(days=7)

# Error handler for 404
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# Function to create initial database tables and admin user
def create_tables():
    with app.app_context():
        db.create_all()
        if not Admin.query.first():
            hashed_password = generate_password_hash('admin', method='pbkdf2:sha256')
            admin = Admin(username='admin', password=hashed_password)
            db.session.add(admin)
            db.session.commit()

# Route to generate a unique quiz code
@app.route('/generate_code', methods=['POST'])
def generate_code():
    while True:
        code = random.randint(100000, 999999)
        if not QuizSession.query.filter_by(code=code).first():
            break
    quiz_id = request.form['quiz_id']
    new_session = QuizSession(quiz_id=quiz_id, code=code)
    db.session.add(new_session)
    db.session.commit()
    return jsonify({'code': code})

# Route to join a quiz using the quiz code
@app.route('/join_quiz', methods=['POST'])
def join_quiz():
    code = request.form['code']
    session = QuizSession.query.filter_by(code=code).first()
    if session:
        return jsonify({'status': 'success'})
    else:
        return jsonify({'status': 'failed', 'message': _('Invalid code')}), 404

# Route to submit the player's pseudonym
@app.route('/submit_pseudonym', methods=['POST'])
def submit_pseudonym():
    pseudonym = request.form['pseudonym']
    code = request.form['code']
    session = QuizSession.query.filter_by(code=code).first()
    if session:
        new_player = Player(name=pseudonym, quiz_session_id=session.id)
        db.session.add(new_player)
        db.session.commit()
        return jsonify({'status': 'success'})
    else:
        return jsonify({'status': 'failed', 'message': _('Invalid code')}), 404

# Language selection
@app.route('/set_language/<language>')
def set_language(language):
    session['language'] = language
    return redirect(request.referrer)

# Select the locale based on the user's preference
@babel.localeselector
def get_locale():
    return session.get('language', 'en')

# Make get_locale available in Jinja2 templates
app.jinja_env.globals['get_locale'] = get_locale

if __name__ == '__main__':
    create_tables()
    app.run(debug=True)
