from flask_sqlalchemy import SQLAlchemy
 
db = SQLAlchemy()

class Note(db.Model):
    __tablename__ = "notes"
    id = db.Column("notes_id", db.Integer(), autoincrement=True, primary_key=True)
    def __init__(self):
        self.content = db.Column(db.Text())
        self.date_added = db.Column(db.DateTime())
        self.following = db.Column(db.Integer())
        self.audio_id = db.Column(db.Integer())
        self.todo = db.Column(db.Boolean())

class AudioRecording(db.Model):
    __tablename__ = "audio_recordings"
    id = db.Column("audio_id", db.Integer(), autoincrement=True, primary_key=True)

    def __init__(self):
        self.file_url = db.Column(db.UnicodeText())
        self.transcribed = db.Column(db.Boolean())

