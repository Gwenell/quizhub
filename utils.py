import os
from werkzeug.utils import secure_filename
from extensions import db
from flask import current_app as app

def create_quiz_directory_and_db(quiz_title):
    quiz_dir = os.path.join('quizzes', secure_filename(quiz_title))
    os.makedirs(quiz_dir, exist_ok=True)
    quiz_db_path = os.path.join(quiz_dir, 'questions.db')
    if not os.path.exists(quiz_db_path):
        with app.app_context():
            db.create_all(bind=quiz_db_path)
