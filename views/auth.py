from flask import Blueprint, current_app, redirect, render_template, request, session, url_for
from models import db, Note, AudioRecording, Users
from tools import generate_token

import datetime

auth = Blueprint('auth', __name__, url_prefix='/auth')

@auth.route("/login", methods = ['POST'])
def login():
    if db.session.query(Users).first().password == request.form.get('password') :
        session["logged_in"] = True
    else :
        session["home_message"] = "Wrong password"
    return redirect(url_for("routes.home"))

@auth.route("/logout", methods = ['GET'])
def logout():
    session.clear()
    session["home_message"] = "Logged out"
    return redirect(url_for("routes.home"))

@auth.route("/pwreset", methods = ['POST'])
def pwreset():
    session.clear()
    user = db.session.query(Users).first()
    db.session.delete(user)
    db.session.commit()
    session["home_message"] = "Password reset successful"
    return redirect(url_for("routes.home"))

@auth.route("/register", methods = ['POST'])
def register():
    if request.form.get('password') == request.form.get('password-confirm') :
        print(request.form)
        new_user = Users(
            password = request.form.get('password'),
            api_key = generate_token(request.form.get('password')),
            date_created = datetime.datetime.now())
        db.session.add(new_user)
        db.session.commit()

        session["logged_in"] = True
        session["settings_message"] = "Please copy your API key and input your swiftink key"
        return redirect(url_for("settings.root"))
    else :
        session["home_message"] = "The passwords did not match"
        return redirect(url_for("routes.home"))