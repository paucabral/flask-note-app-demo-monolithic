from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
# Load configuration according to environment
if os.environ.get("FLASK_ENV") == 'production':
    app.config['SECRET_KEY'] = os.environ.get('PROD_SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('PROD_SQLALCHEMY_DATABASE_URI')
elif os.environ.get("FLASK_ENV") == 'staging':
    app.config['SECRET_KEY'] = os.environ.get('STG_SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('STG_SQLALCHEMY_DATABASE_URI')
elif os.environ.get("FLASK_ENV") == 'test':
    app.config['SECRET_KEY'] = os.environ.get('TEST_SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('TEST_SQLALCHEMY_DATABASE_URI')
else:
    app.config['SECRET_KEY'] = os.environ.get('DEV_SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DEV_SQLALCHEMY_DATABASE_URI')
    
db = SQLAlchemy(app)
ma = Marshmallow(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.relationship('Note', backref='user', lazy=True)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class NoteSchema(ma.Schema):
    class Meta:
        fields = ("id", "title", "content")

note_schema = NoteSchema()
notes_schema = NoteSchema(many=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username and password:
            existing_user = User.query.filter_by(username=username).first()
            if not existing_user:
                user = User(username=username)
                user.set_password(password=password)
                db.session.add(user)
                db.session.commit()
            else:
                return "User already exists."
        else:
            return "Please fill out all the fields."
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('get_all_notes'))
        else:
            return 'Invalid username or password'
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/notes', methods=['POST'])
@login_required
def create_note():
    data = {
        "title": request.form["title"],
        "content": request.form["content"],
        "user_id": current_user.id
    }

    note = Note(title=data["title"], content=data["content"], user_id=data["user_id"])
    db.session.add(note)
    db.session.commit()
    return redirect(url_for('get_all_notes'))

@app.route('/notes', methods=['GET'])
@login_required
def get_all_notes():
    notes = Note.query.filter_by(user_id=current_user.id).all()
    return render_template('index.html', notes=notes)

@app.route('/notes/<int:note_id>')
@login_required
def get_note(note_id):
    note = Note.query.get_or_404(note_id)
    if note.user_id != current_user.id:
        return 'Unauthorized', 401
    return render_template("note.html", note=note)

@app.route('/notes/<int:note_id>', methods=['POST'])
@login_required
def update_note(note_id):
    note = Note.query.get_or_404(note_id)
    if note.user_id != current_user.id:
        return 'Unauthorized', 401
    data = request.form
    note.title = data['title']
    note.content = data['content']
    db.session.commit()
    return redirect(url_for('get_all_notes'))

@app.route('/notes/<int:note_id>/delete')
@login_required
def delete_note(note_id):
    note = Note.query.get_or_404(note_id)
    if note.user_id != current_user.id:
        return 'Unauthorized', 401
    db.session.delete(note)
    db.session.commit()
    return redirect(url_for('get_all_notes'))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=bool(os.getenv("DEBUG")), port=int(os.getenv("PORT")), host="0.0.0.0")