from extensions import db

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(500), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    options = db.Column(db.Text, nullable=True)
    correct_options = db.Column(db.Text, nullable=True)
    media_file = db.Column(db.String(200), nullable=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
