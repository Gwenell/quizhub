from flask import Blueprint, render_template, redirect, url_for, request

player_bp = Blueprint('player', __name__)

@player_bp.route('/')
def index():
    return render_template('player/index.html')

@player_bp.route('/join_quiz', methods=['POST'])
def join_quiz():
    code = request.form['code']
    # Logique pour rejoindre le quiz
    return redirect(url_for('player.quiz', code=code))

@player_bp.route('/quiz/<code>')
def quiz(code):
    # Logique pour afficher les questions du quiz
    return render_template('player/quiz.html', code=code)

@player_bp.route('/scores')
def scores():
    # Logique pour afficher les scores
    return render_template('player/scores.html')
