from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from forms import PlayerForm
from models import Quiz, QuizSession, Player
from extensions import db
from flask_babelex import _

player_bp = Blueprint('player', __name__)

@player_bp.route('/')
def index():
    form = PlayerForm()
    return render_template('player/index.html', form=form)

@player_bp.route('/join_quiz', methods=['POST'])
def join_quiz():
    form = PlayerForm()
    if form.validate_on_submit():
        code = request.form['code']
        pseudonym = form.pseudonym.data
        session = QuizSession.query.filter_by(code=code).first()
        if session:
            new_player = Player(name=pseudonym, quiz_session_id=session.id, quiz_id=session.quiz_id)
            db.session.add(new_player)
            db.session.commit()
            return redirect(url_for('player.quiz', code=code))
        else:
            flash(_('Invalid code'))
            return redirect(url_for('player.index'))
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error in {field}: {error}")
    return redirect(url_for('player.index'))

@player_bp.route('/quiz/<code>')
def quiz(code):
    session = QuizSession.query.filter_by(code=code).first()
    if session:
        quiz = Quiz.query.get(session.quiz_id)
        return render_template('player/quiz.html', quiz=quiz)
    else:
        flash(_('Invalid quiz code'))
        return redirect(url_for('player.index'))

@player_bp.route('/scores')
def scores():
    # Logic to display scores
    return render_template('player/scores.html')
