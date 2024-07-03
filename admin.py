from flask import Blueprint, render_template, redirect, url_for, request, session, flash, jsonify
from extensions import db
from models import Admin, Quiz, QuizSession, Question
from forms import LoginForm, QuizForm, QuestionForm
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
from flask_babelex import _
import os
import random
import logging

# Setup logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Blueprint for admin routes
admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        logger.debug("Form submitted and validated")
        admin = Admin.query.filter_by(username=form.username.data).first()
        if admin:
            logger.debug("Admin found")
            if check_password_hash(admin.password, form.password.data):
                logger.debug("Password verified")
                session['admin_logged_in'] = True
                session['username'] = admin.username
                return redirect(url_for('admin.dashboard'))
            else:
                logger.debug(f"Password verification failed for user {form.username.data}")
        else:
            logger.debug(f"Admin with username {form.username.data} not found")
        flash(_('Invalid credentials'))
    else:
        if request.method == 'POST':
            logger.debug("Form submitted but not validated")
            for field, errors in form.errors.items():
                for error in errors:
                    logger.debug(f"Error in {field}: {error}")
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
        new_quiz = Quiz(title=form.title.data, description=form.description.data, code=str(random.randint(100000, 999999)))
        db.session.add(new_quiz)
        db.session.commit()
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
    return render_template('admin/view_quiz.html', quiz=quiz)

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
    form = QuestionForm()

    if form.validate_on_submit():
        quiz = Quiz.query.get_or_404(quiz_id)
        if form.type.data == 'multiple_choice':
            options = [answer_form.answer.data for answer_form in form.answers]
            correct_options = [i for i, answer_form in enumerate(form.answers) if answer_form.correct.data]
        else:  # True/False
            options = ['True', 'False']
            correct_options = [0] if request.form.get('true_false_answer') == 'True' else [1]

        new_question = Question(
            text=form.text.data,
            type=form.type.data,
            options=','.join(options),
            correct_options=','.join(map(str, correct_options)),
            media_file=form.media_file.data.filename if form.media_file.data else None,
            quiz_id=quiz.id
        )
        db.session.add(new_question)
        db.session.commit()
        return redirect(url_for('admin.view_quiz', quiz_id=quiz.id))
    return redirect(url_for('admin.edit_quiz', quiz_id=quiz_id))


@admin_bp.route('/quiz/<int:quiz_id>/delete', methods=['POST'])
def delete_quiz(quiz_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))
    quiz = Quiz.query.get_or_404(quiz_id)
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
        question.correct_options = ','.join(str(index) for index, answer in form.answers if answer.correct.data)
        if form.media_file.data:
            question.media_file = form.media_file.data.filename
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
    questions = Question.query.filter_by(quiz_id=quiz.id).all()
    return render_template('admin/play_quiz.html', quiz=quiz, questions=questions)
