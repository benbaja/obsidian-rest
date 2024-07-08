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
import logging.config
import datetime
#import whisper
from tools import WerkzeugFilter
from views.auth import auth
from views.settings import settings
from views.capture import capture
from views.routes import routes

def create_app(config_file): 
    config_json = json.load(open(config_file))
    instance_path = os.path.abspath(config_json["INSTANCE_PATH"])
    app = Flask(__name__, instance_path=instance_path)

    Path(config_json["LOGS_PATH"]).mkdir(parents=False, exist_ok=True)
    logging.config.dictConfig(config_json["LOGGER_CONFIG"])

    app.config.from_file(config_file, load=json.load)
    app.config.from_prefixed_env()
    
    db.init_app(app)
    bootstrap = Bootstrap5(app)
    flask_cors.CORS(app) # authorize cross-origin AJAX for Obsidian

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
