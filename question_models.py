from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(200), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    options = db.Column(db.String(200), nullable=True)
    correct_option = db.Column(db.String(50), nullable=False)
    media_file = db.Column(db.String(100), nullable=True)
