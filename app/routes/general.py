from flask import Blueprint, render_template, redirect, url_for
from app.database import db, Post, User
from app.utils import protectedPage

general = Blueprint("general", __name__)

# phantom route redirects
@general.get("/my/")
@general.get("/user/")
def x():
    return redirect(url_for("general.index")), 301

@general.get("/")
def index():
    return render_template(
        "general/index.html",
        # to do: these need to be paginated
        pinned_posts = db.session.query(Post, User).filter(Post.user_id == User.id, Post.pinned == True, Post.deleted == False).all(),
        posts = db.session.query(Post, User).filter(Post.user_id == User.id, Post.deleted == False).all(), # content reversed via Jinja in template
        )

@general.get("/my/account/")
@protectedPage
def my_account():
    return render_template("general/myaccount.html")

@general.get("/user/<int:user_id>/")
def user_profile(user_id: int):
    return render_template("general/profile.html")