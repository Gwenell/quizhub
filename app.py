from flask import Flask, render_template, redirect, url_for, flash, request, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_socketio import SocketIO, emit
from flask_wtf import FlaskForm
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
import random
import string
from config import Config
from models import db, User, Quiz, Question, Option
from forms import LoginForm, QuizForm, QuestionForm

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
migrate = Migrate(app, db)
socketio = SocketIO(app)
login_manager = LoginManager(app)
login_manager.login_view = 'admin_login'

admin_created = False

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.before_request
def create_admin():
    global admin_created
    if not admin_created:
        if not User.query.filter_by(username='Admin').first():
            admin = User(username='Admin', password=generate_password_hash('admin'))
            db.session.add(admin)
            db.session.commit()
        admin_created = True

@app.route('/')
def home():
    return render_template('player/home.html')

@app.route('/join', methods=['POST'])
def join():
    session['quiz_code'] = request.form['quiz_code']
    session['username'] = request.form['username']
    return redirect(url_for('player'))

@app.route('/player')
def player():
    if 'quiz_code' not in session or 'username' not in session:
        return redirect(url_for('home'))
    return render_template('player/quiz.html', username=session['username'])

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated:
        return redirect(url_for('manage_quizzes'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('manage_quizzes'))
        else:
            flash('Invalid username or password')
    return render_template('admin/admin_login.html', form=form)

@app.route('/admin_logout')
def admin_logout():
    logout_user()
    return redirect(url_for('admin_login'))

@app.route('/manage_quizzes')
@login_required
def manage_quizzes():
    quizzes = Quiz.query.all()
    return render_template('admin/manage_quizzes.html', quizzes=quizzes)

@app.route('/create_quiz', methods=['GET', 'POST'])
@login_required
def create_quiz():
    form = QuizForm()
    if form.validate_on_submit():
        quiz = Quiz(title=form.title.data, description=form.description.data)
        db.session.add(quiz)
        db.session.commit()
        return redirect(url_for('manage_quizzes'))
    return render_template('admin/create_quiz.html', form=form)

@app.route('/edit_quiz/<int:quiz_id>', methods=['GET', 'POST'])
@login_required
def edit_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    form = QuizForm(obj=quiz)
    if form.validate_on_submit():
        quiz.title = form.title.data
        quiz.description = form.description.data
        db.session.commit()
        return redirect(url_for('manage_quizzes'))
    return render_template('admin/edit_quiz.html', form=form, quiz=quiz)

@app.route('/delete_question/<int:question_id>', methods=['POST'])
@login_required
def delete_question(question_id):
    question = Question.query.get_or_404(question_id)
    db.session.delete(question)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/delete_quiz/<int:quiz_id>', methods=['POST'])
@login_required
def delete_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    db.session.delete(quiz)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/add_question/<int:quiz_id>', methods=['GET', 'POST'])
@login_required
def add_question(quiz_id):
    form = QuestionForm()
    if form.validate_on_submit():
        question = Question(text=form.text.data, quiz_id=quiz_id)
        db.session.add(question)
        db.session.commit()
        for i in range(1, 5):
            option_text = getattr(form, f'option{i}').data
            option = Option(text=option_text, question_id=question.id)
            db.session.add(option)
            if i == int(form.correct_option.data):
                question.correct_option_id = option.id
        db.session.commit()
        return redirect(url_for('edit_quiz', quiz_id=quiz_id))
    return render_template('admin/add_question.html', form=form)

@app.route('/start_quiz/<int:quiz_id>')
@login_required
def start_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    socketio.emit('start_quiz', {'quiz_id': quiz_id}, broadcast=True)
    return redirect(url_for('manage_quizzes'))

@app.route('/scoreboard')
def scoreboard():
    return render_template('player/scoreboard.html')

if __name__ == '__main__':
    socketio.run(app, debug=True)
