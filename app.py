from flask import Flask, render_template, request, redirect, url_for, session
from models import db, TemporaryKey
import random
import string

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'
db.init_app(app)


@app.before_first_request
def create_tables():
    db.create_all()


def generate_key(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        page_id = session.get('page_id', generate_key())
        session['page_id'] = page_id

        existing_key = TemporaryKey.query.filter_by(page_id=page_id).first()
        if existing_key:
            db.session.delete(existing_key)
            db.session.commit()

        new_key = TemporaryKey(page_id=page_id, key=generate_key())
        db.session.add(new_key)
        db.session.commit()

        return render_template('admin.html', key=new_key.key, page_id=page_id)

    return render_template('admin.html')


@app.route('/player', methods=['GET', 'POST'])
def player():
    if request.method == 'POST':
        key = request.form['key']
        pseudo = request.form['pseudo']
        temp_key = TemporaryKey.query.filter_by(key=key).first()
        if temp_key:
            temp_key.pseudo = pseudo
            db.session.commit()
            return render_template('player.html', connected=True, pseudo=pseudo)
        return render_template('player.html', error="Invalid key")

    return render_template('player.html')


@app.route('/notify/<page_id>', methods=['POST'])
def notify(page_id):
    temp_key = TemporaryKey.query.filter_by(page_id=page_id).first()
    if temp_key:
        # Logic to send notification can be added here
        return f"Notification sent to {temp_key.pseudo}", 200
    return "Page ID not found", 404


if __name__ == '__main__':
    app.run(debug=True)
