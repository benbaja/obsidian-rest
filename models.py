from flask_sqlalchemy import SQLAlchemy
 
db = SQLAlchemy()

class Note(db.Model):
    __tablename__ = "notes"
    note_id = db.Column("note_id", db.Integer(), autoincrement=True, primary_key=True)
    text = db.Column(db.Text())
    date_added = db.Column(db.DateTime())
    following = db.Column(db.Integer(), nullable=True)
    audio_id = db.Column(db.Integer(), nullable=True)
    todo = db.Column(db.Boolean())
    def __init__(self, text, date_added, following=None, audio_id=None, todo=False):
        self.text = text
        self.date_added = date_added
        self.following = following
        self.audio_id = audio_id
        self.todo = todo

class AudioRecording(db.Model):
    __tablename__ = "audio_recordings"
    audio_id = db.Column("audio_id", db.Integer(), autoincrement=True, primary_key=True)
    file_name = db.Column(db.UnicodeText())
    transcript_id = db.Column(db.UnicodeText())
    date_added = db.Column(db.DateTime())

    def __init__(self, file_name, date_added, transcript_id=None):
        self.transcript_id = transcript_id
        self.file_name = file_name
        self.date_added = date_added

