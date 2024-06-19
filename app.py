from flask import Flask, render_template, request, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
import random
import string
import logging

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'
db = SQLAlchemy(app)
socketio = SocketIO(app)

logging.basicConfig(level=logging.DEBUG)


class TemporaryKey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    page_id = db.Column(db.String(50), unique=True, nullable=False)
    key = db.Column(db.String(10), unique=True, nullable=False)
    notification = db.Column(db.String(50), nullable=True)


class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    page_id = db.Column(db.String(50), nullable=False)
    pseudo = db.Column(db.String(50), unique=True, nullable=False)


@app.before_request
def create_tables():
    if not hasattr(app, 'tables_created'):
        db.create_all()
        app.tables_created = True


@app.route('/reinitialize_db')
def reinitialize_db():
    db.drop_all()
    db.create_all()
    return "Database reinitialized"


def generate_key(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))


@app.route('/')
def home():
    return "Welcome to QuizHub! Please go to /admin or /player"


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        page_id = "ADMIN_PAGE_ID"
        session['page_id'] = page_id

        existing_key = TemporaryKey.query.filter_by(page_id=page_id).first()
        if existing_key:
            db.session.delete(existing_key)
            db.session.commit()

        new_key = TemporaryKey(page_id=page_id, key=generate_key())
        db.session.add(new_key)
        db.session.commit()

        return render_template('admin.html', key=new_key.key, page_id=page_id)

    key_entry = TemporaryKey.query.filter_by(page_id="ADMIN_PAGE_ID").first()
    key = key_entry.key if key_entry else None
    return render_template('admin.html', key=key, page_id="ADMIN_PAGE_ID")


@app.route('/player', methods=['GET', 'POST'])
def player():
    if request.method == 'POST':
        key = request.form['key']
        pseudo = request.form['pseudo']
        temp_key = TemporaryKey.query.filter_by(key=key, page_id="ADMIN_PAGE_ID").first()
        if temp_key:
            try:
                new_player = Player(page_id=temp_key.page_id, pseudo=pseudo)
                db.session.add(new_player)
                db.session.commit()
                session['page_id'] = new_player.page_id
                return render_template('player.html', connected=True, pseudo=pseudo, page_id=new_player.page_id)
            except Exception as e:
                logging.error(f"Error adding player: {e}")
                return render_template('player.html', error="Pseudo already in use or other database error")
        else:
            return render_template('player.html', error="Invalid key")

    return render_template('player.html')


@app.route('/notify', methods=['POST'])
def notify():
    try:
        players = Player.query.all()
        for player in players:
            notification = f"Notification for {player.pseudo}"
            socketio.emit('notification', {'page_id': player.page_id, 'notification': notification}, namespace='/', broadcast=True)
        temp_key = TemporaryKey.query.filter_by(page_id="ADMIN_PAGE_ID").first()
        temp_key.notification = "Notification sent to all players"
        db.session.commit()
        return "Notification sent to all players", 200
    except Exception as e:
        logging.error(f"Error sending notifications: {e}")
        return "Error sending notifications", 500


@app.route('/notifications/<page_id>', methods=['GET'])
def get_notifications(page_id):
    temp_key = TemporaryKey.query.filter_by(page_id=page_id).first()
    if temp_key:
        return jsonify(notification=temp_key.notification), 200
    return jsonify(notification="No notifications"), 404


@app.route('/connected_users', methods=['GET'])
def connected_users():
    players = Player.query.all()
    users_list = [{"pseudo": player.pseudo, "page_id": player.page_id} for player in players]
    return jsonify(users=users_list), 200


if __name__ == '__main__':
    socketio.run(app, debug=True)
