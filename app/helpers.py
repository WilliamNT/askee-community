from flask import session, redirect, url_for, flash
from app.schema import User
from app import ph
from functools import wraps
import argon2

def signIn(email: str, password: str) -> None:
    """
    Handles the sign in process
    """
    if not email:
        return flash("Please provide an email address", "warning")
    if not password:
        return flash("Please provide a password", "warning")
    user = User.query.filter_by(email=email).first()
    
    if user:
        try:
            ph.verify(user.password, password)
            session["user"] = user.id
            session["username"] = user.username

            flash("Sign in successful", "success")
            return redirect(url_for("general.index"))
        except argon2.exceptions.VerifyMismatchError:
            flash("Incorrect password", "warning")
            return redirect(url_for("security.sign_in"))
    else:
        return flash(f"No account uses \"{email}\"", "warning")

def getCurrentAccount() -> User:
    """
    Automatically queries the user currently signed in
    """
    if "user" in session:
        return User.query.filter_by(id=session["id"])
    else:
        raise RuntimeError("Inappropriate method call. Method getCurrentAccount() shouldn't be called when no user is present in the session.")

def protectedPage(f):
    """
    Redirects unauthorized users to the sign in page
    """
    @wraps(f)
    def decoratedFunction(*args, **kwargs):
        if not "user" in session:
            return redirect(url_for("security.sign_in"))
        return f(*args, **kwargs)
    return decoratedFunction