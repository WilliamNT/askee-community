from flask import Blueprint, redirect, render_template, request, url_for

forum = Blueprint("forum", __name__)

# phantom route redirects
@forum.get("/post/")
def x():
    return redirect(url_for("general.index"))

@forum.route("/composer/", methods=["GET", "POST"])
def composer():
    return render_template("forum/composer.html")

@forum.get("/pinned/")
def pinned_posts():
    return render_template("forum/pinned.html")

@forum.get("/post/<post_id>/")
def post(post_id):
    # don't forget skeleton meta author tag in case you update this!
    return render_template("forum/post.html")