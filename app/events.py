from flask import redirect, session, flash, url_for
from app import app
from app.database import User

@app.before_request
def refreshSessionUserDetails() -> None:
    """
    Ensures that all user data stored in the session is up to date
    """
    if "user" in session:
        user = User.query.filter_by(id=session["id"]).first()
        if user:
            session["user"] = user.id
            session["username"] = user.username
        else:
            flash("There was an error with your session, please sign in again", "warning")
            return redirect(url_for("security.sign_in"))

@app.before_first_request
def configureSession() -> None:
    """
    Configures the session
    """
    session.permanent = True