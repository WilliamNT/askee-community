from flask import Blueprint, redirect, render_template, request, session, url_for, flash
import app.helpers as helpers
from app.schema import User

security = Blueprint("security", __name__, url_prefix="/sign/")

@security.route("/in/", methods=["GET", "POST"])
def sign_in():
    if "user" in session:
        return redirect(url_for("general.index"))
        
    if request.method == "POST":
        return helpers.signIn(request.form.get("email"), request.form.get("password"))
    
    return render_template("security/signin.html")

@security.route("/up/", methods=["GET", "POST"])
def sign_up():
    if "user" in session:
        return redirect(url_for("general.index"))
    if request.method == "POST":
        user = User()
        user.create(
            username=request.form.get("username"),
            email=request.form.get("email"),
            password=request.form.get("password"),
            is_admin=False # Users cannot become admins via the public sign up form 
        )

    return render_template("security/signup.html")

@security.get("/out/")
def sign_out():
    """
    Handles the sign out process
    """
    if "user" in session:
        session.pop("user", None)
        session.pop("username", None)
        flash("Sign out successful", "success")
    return redirect(url_for("general.index"))