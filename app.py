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
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')
db = SQLAlchemy(app)
ma = Marshmallow(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
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

@app.route('/notes', methods=['POST'])
def create_note():
    data = {
        "title": request.form["title"],
        "content": request.form["content"]
    }

    note = Note(title=data["title"], content=data["content"])
    db.session.add(note)
    db.session.commit()
    return redirect('/')

@app.route('/')
def get_all_notes():
    notes = Note.query.all()
    return render_template('index.html', notes=notes)

@app.route('/notes/<int:note_id>')
def get_note(note_id):
    note = Note.query.get_or_404(note_id)
    return render_template("note.html", note=note)

@app.route('/notes/<int:note_id>', methods=['POST'])
def update_note(note_id):
    note = Note.query.get_or_404(note_id)
    data = request.form
    note.title = data['title']
    note.content = data['content']
    db.session.commit()
    return redirect('/')

@app.route('/notes/<int:note_id>/delete')
def delete_note(note_id):
    note = Note.query.get_or_404(note_id)
    db.session.delete(note)
    db.session.commit()
    return redirect('/')

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)