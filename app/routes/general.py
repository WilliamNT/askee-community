from flask import Blueprint, render_template
from app import db
from app.schema import Post, User

general = Blueprint("general", __name__)

@general.get("/")
def index():
    return render_template(
        "general/index.html",
        pinned_posts=db.session.query(Post, User).filter(Post.user_id == User.id).all(),
        posts=""
        )

@general.get("/my/account/")
def my_account():
    return render_template("general/myaccount.html")