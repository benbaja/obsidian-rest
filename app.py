from flask import Flask, render_template, request, redirect, jsonify, session, url_for
from flask.logging import default_handler
from flask_bootstrap import Bootstrap5
from pathlib import Path
from models import db, Users
import flask_cors
import json
import os
import sys
import logging
import datetime
#import whisper
from views.auth import auth
from views.settings import settings
from views.capture import capture
from views.routes import routes

def create_app(config_file): 
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

    app.config.from_file(config_file, load=json.load)
    app.config.from_prefixed_env()
    
    db.init_app(app)
    bootstrap = Bootstrap5(app)
    # authorize cross-origin AJAX for Obsidian
    flask_cors.CORS(app)

    app.register_blueprint(auth)
    app.register_blueprint(settings)
    app.register_blueprint(capture)
    app.register_blueprint(routes)

    return app

if __name__ == "__main__" :
    app = create_app("config.json")
    with app.app_context():
        db.create_all()
    app.run()
