from flask import Flask, render_template, request, redirect, jsonify
from flask.logging import default_handler
from models import db, Note, AudioRecording
from swiftink import get_transcript
import sys
from pathlib import Path
import datetime
import logging
import base64

# setup logger to write to file
logger = logging.getLogger('werkzeug')
log_formatter = logging.Formatter("%(asctime)s %(levelname)s:%(message)s")
logger.setLevel(logging.DEBUG)

Path("logs").mkdir(parents=False, exist_ok=True)
log_file_path = "logs/" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + ".log"
log_file_handler = logging.FileHandler(log_file_path)
log_file_handler.setFormatter(log_formatter)
logger.addHandler(log_file_handler)

log_stream_handler = logging.StreamHandler(sys.stdout)
log_stream_handler.setFormatter(log_formatter)
logger.addHandler(log_stream_handler)

app = Flask(__name__)
app.logger.removeHandler(default_handler)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///obsidian-audio-capture.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/capture", methods = ['POST', 'GET'])
def capture():
    if request.method == 'POST':
        request_json = request.json
        capture_type = request_json.get("capture_type")
        capture_data = request.json.get("data")
        if capture_type == "note" :
            # check if sent note is a todo, fallback to false
            todo = capture_data.get("todo") or False

            db.session.add(
                Note(
                    text=capture_data["text"], 
                    date_added=datetime.datetime.now(), 
                    todo=todo
            ))
            db.session.commit()

            # return new note id
            new_note = Note.query.order_by(Note.note_id.desc()).first()

            return {"new_note_id": new_note.note_id}

        elif capture_type == "audio" :
            audio_file = base64.b64decode(capture_data.get("audio"))
            file_path = "audio_captures/" + capture_data.get("file_name")
            # create audio capture folder if it doesn't exist
            Path("audio_captures").mkdir(parents=False, exist_ok=True)

            # download audio file 
            with open(file_path,"wb") as file:
                file.write(audio_file)
            # add audio file to database
            db.session.add(
                AudioRecording(
                    file_name=capture_data.get("file_name"), 
                    date_added=datetime.datetime.now())
            )
            db.session.commit()
            # try to transcript the audio file
            transcription_result = get_transcript(capture_data.get("file_name"), logger)
            if transcription_result :
                # check length of note and split if > 50kb
                # add the transcript to the note database if succeeded
                # update the audio file database
                # return id of note if succeeded
                return "OK", 200
            else :
                # update the audio file database
                # else return id of audio
                return "Not OK", 200

        return "Invalid payload ", 400

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