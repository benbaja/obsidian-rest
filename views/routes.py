from flask import Blueprint, render_template, session
from models import db, Users

routes = Blueprint('routes', __name__)

@routes.route("/")
def home():
    if session.get("home_message") :
        message = session.pop("home_message")
    else :
        message = None

    if session.get('logged_in') == True :
        user = db.session.query(Users).first()
        return render_template("home.html", logged_in=True, user_info=user)
    else :
        if db.session.query(Users).first() :
            return render_template("auth.html", logged_in=False, registered=True, message=message or "Please enter your admin password")
        else :
            return render_template("auth.html", logged_in=False, registered=False, message=message or "Please set up your admin password")
