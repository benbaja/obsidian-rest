from flask import Blueprint, redirect, render_template, request, session, url_for
from models import db, Users
from tools import generate_token

settings = Blueprint('settings', __name__, url_prefix='/settings')

@settings.route("/", methods = ['GET'])
def root():
    if session.get("logged_in") :
        user = db.session.query(Users).first()
        return render_template("settings.html", logged_in=True, api_key=user.api_key, swiftink_key=user.swiftink_api, message=session.get("settings_message"))
    else :
        return redirect(url_for("routes.home"))

@settings.route("/change", methods = ['POST'])
def change():
    if session.get("logged_in") :
        user = db.session.query(Users).first()
        message = ""

        if request.form.get('new-password') :
            if request.form.get('new-password') == request.form.get('new-password-confirm') :
                if request.form.get('old-password') == user.password :
                    user.password = request.form.get('new-password')
                    user.api_key = generate_token(request.form.get('new-password'))
                    message += "Successfully changed password. "
                else :
                    message += "Invalid password"
            else :
                message += "Passwords did not match. "

        if request.form.get('api_key') :
            user.api_key = generate_token(user.password)
            message += "Generated new API key. "

        if request.form.get('swiftink_key') :
            user.swiftink_api = request.form.get('swiftink_key')
            message += "Saved Swiftink API key. "

        db.session.commit()
        db.session.flush()

        session["settings_message"] = message
        return redirect("/settings")
    else :
        return redirect(url_for("routes.home"))