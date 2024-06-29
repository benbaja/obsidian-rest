from flask import Flask, render_template, request, redirect, jsonify, session, url_for
from flask.logging import default_handler
from flask_cors import CORS
from flask_bootstrap import Bootstrap5
from pathlib import Path
from models import db, Note, AudioRecording, Users
from swiftink import Swiftink
import os
import sys
import jwt
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

bootstrap = Bootstrap5(app)

# authorize cross-origin AJAX for Obsidian
CORS(app)

app.secret_key = os.environ.get("FLASK_SECRET_KEY")

@app.route("/")
def hello_world():
    if session.get('logged_in') == True :
        return render_template("home.html", bootstrap=bootstrap, logged_in=True)
    else :
        if db.session.query(Users).first() :
            return render_template("home.html", bootstrap=bootstrap, logged_in=False, registered=True, message="Please enter your admin password")
        else :
            return render_template("home.html", bootstrap=bootstrap, logged_in=False, registered=False, message="Please set up your admin password")

@app.route("/login", methods = ['POST'])
def login():
    if db.session.query(Users).first().password == request.form.get('password') :
        session["logged_in"] = True
        return redirect('/')
    else :
        return render_template("home.html", bootstrap=bootstrap, logged_in=False, registered=True, message="Wrong password")

@app.route("/logout", methods = ['GET'])
def logout():
    session.clear()
    return redirect('/')

@app.route("/pwreset", methods = ['POST'])
def pwreset():
    session.clear()
    user = db.session.query(Users).first()
    db.session.delete(user)
    db.session.commit()
    return redirect('/')

@app.route("/register", methods = ['POST'])
def register():
    if request.form.get('password') == request.form.get('password-confirm') :
        api_key = jwt.encode({'password': request.form.get('password')}, app.secret_key)
        new_user = Users(
            password = request.form.get('password'),
            api_key = api_key,
            date_created = datetime.datetime.now())
        db.session.add(new_user)
        db.session.commit()

        session["logged_in"] = True
        return redirect('/')
    else :
        return render_template("home.html", bootstrap=bootstrap, logged_in=False, registered=False, message="The passwords did not match")

@app.route("/capture/create", methods = ['POST'])
def capture_create():
    request_json = request.json
    capture_type = request_json.get("capture_type")
    capture_data = request.json.get("data")
    if capture_type == "note" :
        # check if sent note is a todo, fallback to false
        todo = request_json.get("todo") or False
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
        new_audio = AudioRecording(
                file_name=capture_data.get("file_name"), 
                date_added=datetime.datetime.now()
        )
        db.session.add(new_audio)
        db.session.flush()
        db.session.refresh(new_audio)

        # try to transcript the audio file
        transcription_result = Swiftink(file_path, logger)
        if transcription_result.text :
            # check length of note and split if > 50kb
            # add the transcript to the note database if succeeded
            db.session.add(
                Note(
                    text=transcription_result.text, 
                    date_added=datetime.datetime.now(), 
                    audio_id=new_audio.audio_id
            ))
            # update the audio file database
            new_audio.transcript_id = transcription_result.id
            db.session.add(new_audio)
            db.session.commit()
            # return id of note if succeeded
            new_note = Note.query.order_by(Note.note_id.desc()).first()
            return {"new_note_id": new_note.note_id}

        else :
            # return id of audio
            return {"new_audio_id": new_audio.audio_id}

    return "Invalid payload ", 400

@app.route("/capture/update", methods = ['POST'])
def capture_update():
    to_update_list = request.json['captureIDs']
    
    db.session.query(Note).filter(Note.note_id.in_(to_update_list)).update({'fetched': True})
    db.session.commit()

    return to_update_list

@app.route("/capture", methods = ['GET'])
def capture_fetch():
    all_notes = db.session.query(Note).filter_by(fetched=False)
    all_notes_json = [
        {
            "text": note.text,
            "date_added": note.date_added,
            "todo": note.todo,
            "following": note.following,
            "audio_id": note.audio_id,
            "capture_id": note.note_id
        } for note in all_notes
    ]
    return all_notes_json

@app.route("/capture/<id>", methods = ['GET'])
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