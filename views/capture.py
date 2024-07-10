from flask import Blueprint, current_app, request, session, jsonify
from models import db, Note, AudioRecording
from tools import Swiftink
import base64
import datetime
from pathlib import Path
from tools import token_required

capture = Blueprint('capture', __name__, url_prefix='/capture')

@capture.route("/create", methods = ['POST'])
@token_required
def create():
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
        if "," in capture_data.get("audio") :
            audio_header, audio_data = capture_data.get("audio").split(",")
        else :
            audio_data = capture_data.get("audio")
        audio_file = base64.b64decode(audio_data)
        file_path = "var/audio_captures/" + capture_data.get("file_name")
        # create audio capture folder if it doesn't exist
        Path("var/audio_captures/").mkdir(parents=False, exist_ok=True)

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
        transcription_result = Swiftink(file_path)
        if transcription_result.text :
            # todo : check length of note and split if > 50kb
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
            return jsonify({'message': 'Server error', "new_audio_id": new_audio.audio_id}), 500

    return "Invalid payload ", 400

@capture.route("/update", methods = ['POST'])
@token_required
def update():
    to_update_list = request.json['captureIDs']
    
    db.session.query(Note).filter(Note.note_id.in_(to_update_list)).update({'fetched': True})
    db.session.commit()

    return to_update_list

@capture.route("/", methods = ['GET'])
@token_required
def fetch():
    all_captures = db.session.query(Note).filter_by(fetched=False)
    all_captures_json = [
        {
            "text": note.text,
            "date_added": note.date_added,
            "todo": note.todo,
            "following": note.following,
            "audio_id": note.audio_id,
            "capture_id": note.note_id
        } for note in all_captures
    ]
    return all_captures_json

@capture.route("/<id>", methods = ['GET'])
@token_required
def capture_id(id):
    note = Note.query.filter_by(note_id=id).first()
    capture_json = {
        "text": note.text,
        "date_added": note.date_added,
        "todo": note.todo,
        "following": note.following,
        "audio_id": note.audio_id
    }
    return capture_json