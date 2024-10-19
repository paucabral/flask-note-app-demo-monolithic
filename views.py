from flask import Flask, render_template, request, redirect, url_for
from flask_migrate import Migrate
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

from models import db, User, Note
from schemas import ma

app = Flask(__name__)
app.config.from_object('config.Config')

db.init_app(app)
ma.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

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
    if current_user.is_authenticated:
        return redirect(url_for('get_all_notes'))

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
    note = db.session.get(Note, note_id)
    if note.user_id != current_user.id:
        return 'Unauthorized', 401
    return render_template("note.html", note=note)

@app.route('/notes/<int:note_id>', methods=['POST'])
@login_required
def update_note(note_id):
    note = db.session.get(Note, note_id)
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
    note = db.session.get(Note, note_id)
    if note.user_id != current_user.id:
        return 'Unauthorized', 401
    db.session.delete(note)
    db.session.commit()
    return redirect(url_for('get_all_notes'))
