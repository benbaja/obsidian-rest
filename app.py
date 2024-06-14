from flask import Flask, render_template, request, redirect
from models import db, Note, AudioRecording

app = Flask(__name__)
 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///obsidian-audio-capture.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

if __name__ == "__main__" :
    with app.app_context():
        db.create_all()
    app.run(debug="True")