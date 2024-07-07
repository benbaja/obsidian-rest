from flask import Blueprint, current_app, redirect, render_template, request, session, url_for
from models import db, Note, AudioRecording, Users
from tools import generate_api_key

import datetime

auth = Blueprint('auth', __name__, url_prefix='/auth')

@auth.route("/login", methods = ['POST'])
def login():
    if db.session.query(Users).first().password == request.form.get('password') :
        session["logged_in"] = True
    else :
        session["home_message"] = "Wrong password"
    return redirect('/')

@auth.route("/logout", methods = ['GET'])
def logout():
    session.clear()
    session["home_message"] = "Logged out"
    return redirect('/')

@auth.route("/pwreset", methods = ['POST'])
def pwreset():
    session.clear()
    user = db.session.query(Users).first()
    db.session.delete(user)
    db.session.commit()
    session["home_message"] = "Password reset successful"
    return redirect('/')

@auth.route("/register", methods = ['POST'])
def register():
    if request.form.get('password') == request.form.get('password-confirm') :
        new_user = Users(
            password = request.form.get(request.form.get('password')),
            api_key = generate_api_key(request.form.get('password')),
            date_created = datetime.datetime.now())
        db.session.add(new_user)
        db.session.commit()

        session["logged_in"] = True
        session["settings_message"] = "Please copy your API key and input your swiftink key"
        return redirect('/settings')
    else :
        session["home_message"] = "The passwords did not match"
        return redirect('/')