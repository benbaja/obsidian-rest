from flask import Flask, render_template, request, redirect, jsonify
from models import db, Note, AudioRecording
import sys
import datetime

app = Flask(__name__)
 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///obsidian-audio-capture.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/note", methods = ['POST', 'GET'])
def note():
    if request.method == 'POST':
        request_json = request.json
        if request_json["text"] :
            # check if sent note is a todo, fallback to false
            todo = request_json.get("todo") or False
            
            note = Note(
                text=request_json["text"], 
                date_added=datetime.datetime.now(), 
                todo=todo
            )
            db.session.add(note)
            db.session.commit()

            # return new note id
            new_note = Note.query.order_by(Note.note_id.desc()).first()

        return {"new_note_id": new_note.note_id}

    elif request.method == 'GET':
        all_notes = Note.query.all()
        all_notes_json = [
            {
                "text": note.text,
                "date_added": note.date_added,
                "todo": note.todo,
                "following": note.following,
                "audio_id": note.audio_id
            } for note in all_notes
        ]
        return all_notes_json

@app.route("/note/<id>", methods = ['GET'])
def note_id(id):
    note = Note.query.filter_by(note_id=id).first()
    note_json = {
        "text": note.text,
        "date_added": note.date_added,
        "todo": note.todo,
        "following": note.following,
        "audio_id": note.audio_id
    }
    return note_json

if __name__ == "__main__" :
    with app.app_context():
        db.create_all()
    app.run(debug="True")