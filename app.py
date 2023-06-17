from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///notes.db'
db = SQLAlchemy(app)
ma = Marshmallow(app)

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)

class NoteSchema(ma.Schema):
    class Meta:
        fields = ("title", "content")

note_schema = NoteSchema()
notes_schema = NoteSchema(many=True)

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

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)