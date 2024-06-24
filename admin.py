from flask import Blueprint, render_template, redirect, url_for, request, session, flash
from extensions import db
from models import Admin, Quiz
from question_models import Question
from forms import LoginForm, QuizForm, QuestionForm
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
from utils import create_quiz_directory_and_db
import os

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        admin = Admin.query.filter_by(username=form.username.data).first()
        if admin and check_password_hash(admin.password, form.password.data):
            session['admin_logged_in'] = True
            session['username'] = admin.username
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Invalid credentials')
    return render_template('admin/login.html', form=form)

@admin_bp.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    session.pop('username', None)
    return redirect(url_for('admin.login'))

@admin_bp.route('/dashboard')
def dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))
    quizzes = Quiz.query.all()
    return render_template('admin/dashboard.html', quizzes=quizzes)

@admin_bp.route('/create_quiz', methods=['GET', 'POST'])
def create_quiz():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))
    form = QuizForm()
    if form.validate_on_submit():
        new_quiz = Quiz(title=form.title.data, description=form.description.data, code='123456')
        db.session.add(new_quiz)
        db.session.commit()

        create_quiz_directory_and_db(new_quiz.title)

        return redirect(url_for('admin.dashboard'))
    return render_template('admin/create_quiz.html', form=form)

@admin_bp.route('/manage_quiz')
def manage_quiz():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))
    quizzes = Quiz.query.all()
    return render_template('admin/manage_quiz.html', quizzes=quizzes)

@admin_bp.route('/quiz/<int:quiz_id>')
def view_quiz(quiz_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))
    quiz = Quiz.query.get_or_404(quiz_id)
    quiz_db_path = os.path.join('quizzes', secure_filename(quiz.title), 'questions.db')
    db.create_all(bind=quiz_db_path)
    questions = Question.query.all(bind=quiz_db_path)
    return render_template('admin/view_quiz.html', quiz=quiz, questions=questions)

@admin_bp.route('/quiz/<int:quiz_id>/edit', methods=['GET', 'POST'])
def edit_quiz(quiz_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))
    quiz = Quiz.query.get_or_404(quiz_id)
    form = QuizForm(obj=quiz)
    question_form = QuestionForm()
    if form.validate_on_submit():
        quiz.title = form.title.data
        quiz.description = form.description.data
        db.session.commit()
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/edit_quiz.html', form=form, quiz=quiz, question_form=question_form)

@admin_bp.route('/quiz/<int:quiz_id>/add_question', methods=['POST'])
def add_question(quiz_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))
    quiz = Quiz.query.get_or_404(quiz_id)
    form = QuestionForm()
    if form.validate_on_submit():
        quiz_dir = os.path.join('quizzes', secure_filename(quiz.title))
        quiz_db_path = os.path.join(quiz_dir, 'questions.db')
        db.create_all(bind=quiz_db_path)

        media_file = None
        if form.media_file.data:
            filename = secure_filename(form.media_file.data.filename)
            media_path = os.path.join(quiz_dir, filename)
            form.media_file.data.save(media_path)
            media_file = filename

        correct_options = ','.join(str(index) for index, answer in enumerate(form.answers) if answer.correct.data)

        new_question = Question(
            text=form.text.data,
            type=form.type.data,
            options=','.join([answer.answer.data for answer in form.answers]),
            correct_options=correct_options,
            media_file=media_file
        )
        db.session.add(new_question)
        db.session.commit(bind=quiz_db_path)
        return redirect(url_for('admin.edit_quiz', quiz_id=quiz_id))
    return render_template('admin/edit_quiz.html', form=QuizForm(obj=quiz), quiz=quiz, question_form=form)

@admin_bp.route('/quiz/<int:quiz_id>/delete', methods=['POST'])
def delete_quiz(quiz_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))
    quiz = Quiz.query.get_or_404(quiz_id)
    quiz_dir = os.path.join('quizzes', secure_filename(quiz.title))
    if os.path.exists(quiz_dir):
        import shutil
        shutil.rmtree(quiz_dir)
    db.session.delete(quiz)
    db.session.commit()
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/question/<int:question_id>/edit', methods=['GET', 'POST'])
def edit_question(question_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))
    question = Question.query.get_or_404(question_id)
    form = QuestionForm(obj=question)
    if form.validate_on_submit():
        question.text = form.text.data
        question.type = form.type.data
        question.options = ','.join([answer.answer.data for answer in form.answers])
        question.correct_options = ','.join(str(index) for index, answer in enumerate(form.answers) if answer.correct.data)
        if form.media_file.data:
            quiz_dir = os.path.join('quizzes', secure_filename(question.quiz.title))
            filename = secure_filename(form.media_file.data.filename)
            media_path = os.path.join(quiz_dir, filename)
            form.media_file.data.save(media_path)
            question.media_file = filename
        db.session.commit()
        return redirect(url_for('admin.view_quiz', quiz_id=question.quiz_id))
    return render_template('admin/edit_question.html', form=form, question=question)

@admin_bp.route('/question/<int:question_id>/delete', methods=['POST'])
def delete_question(question_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))
    question = Question.query.get_or_404(question_id)
    quiz_id = question.quiz_id
    db.session.delete(question)
    db.session.commit()
    return redirect(url_for('admin.view_quiz', quiz_id=quiz_id))

@admin_bp.route('/quiz/<int:quiz_id>/play')
def play_quiz(quiz_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))
    quiz = Quiz.query.get_or_404(quiz_id)
    quiz_db_path = os.path.join('quizzes', secure_filename(quiz.title), 'questions.db')
    db.create_all(bind=quiz_db_path)
    questions = Question.query.all(bind=quiz_db_path)
    return render_template('admin/play_quiz.html', quiz=quiz, questions=questions)
