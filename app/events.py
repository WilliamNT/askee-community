from flask import session
from app.schema import User
from app import app

@app.before_request
def refreshSessionUserDetails() -> None:
    """
    Ensures that all user data stored in the session is up to date
    """
    if "user" in session:
        user = User.query.filter_by(id=session["id"])
        session["user"] = user.id
        session["username"] = user.username

@app.before_first_request
def configureSession() -> None:
    """
    Configures the session
    """
    session.permanent = True