from flask import Flask, render_template, request, redirect, jsonify, session, url_for
from flask.logging import default_handler
from flask_cors import CORS
from flask_bootstrap import Bootstrap5
from pathlib import Path
from models import db, Users
import os
import sys
import logging
import datetime
#import whisper
from views.auth import auth
from views.settings import settings
from views.capture import capture

# setup logger to write to file
logger = logging.getLogger('werkzeug')
log_formatter = logging.Formatter("%(asctime)s %(levelname)s:%(message)s")
logger.setLevel(logging.DEBUG)

Path("logs").mkdir(parents=False, exist_ok=True)
log_file_path = "var/logs/" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + ".log"
log_file_handler = logging.FileHandler(log_file_path)
log_file_handler.setFormatter(log_formatter)
logger.addHandler(log_file_handler)

log_stream_handler = logging.StreamHandler(sys.stdout)
log_stream_handler.setFormatter(log_formatter)
logger.addHandler(log_stream_handler)

app = Flask(__name__, instance_path=os.path.abspath('var/instance'))
app.logger.removeHandler(default_handler)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///obsidian-audio-capture.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

bootstrap = Bootstrap5(app)

# authorize cross-origin AJAX for Obsidian
CORS(app)

app.secret_key = os.environ.get("FLASK_SECRET_KEY")

app.register_blueprint(auth)
app.register_blueprint(settings)
app.register_blueprint(capture)

@app.route("/")
def home():
    if session.get("home_message") :
        message = session.pop("home_message")
    else :
        message = None

    if session.get('logged_in') == True :
        user = db.session.query(Users).first()
        return render_template("home.html", bootstrap=bootstrap, logged_in=True, user_info=user)
    else :
        if db.session.query(Users).first() :
            return render_template("auth.html", bootstrap=bootstrap, logged_in=False, registered=True, message=message or "Please enter your admin password")
        else :
            return render_template("auth.html", bootstrap=bootstrap, logged_in=False, registered=False, message=message or "Please set up your admin password")

if __name__ == "__main__" :
    with app.app_context():
        db.create_all()
    app.run(debug="True")