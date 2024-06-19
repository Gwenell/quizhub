from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class TemporaryKey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    page_id = db.Column(db.String(50), unique=True, nullable=False)
    key = db.Column(db.String(10), unique=True, nullable=False)
    pseudo = db.Column(db.String(50), nullable=True)
