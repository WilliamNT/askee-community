from flask import Blueprint, render_template, redirect, url_for
from app.database import db, Post, User

general = Blueprint("general", __name__)

# phantom route redirects
@general.get("/my/")
def x():
    return redirect(url_for("general.index")), 301

@general.get("/")
def index():
    return render_template(
        "general/index.html",
        # These need to be paginated
        pinned_posts = db.session.query(Post, User).filter(Post.user_id == User.id, Post.pinned == True).all(),
        posts = db.session.query(Post, User).filter(Post.user_id == User.id).all(), # content reversed via Jinja
        )

@general.get("/my/account/")
def my_account():
    return render_template("general/myaccount.html")

@general.get("/user/<user_id>/")
def user_profile(user_id: int):
    return render_template("general/profile.html")