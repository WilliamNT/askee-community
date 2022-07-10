from flask import Blueprint, flash, redirect, render_template, request, url_for, abort, session
from app.database import db, Post, User
from app.utils import TemplateParser, configurator, protectedPage

forum = Blueprint("forum", __name__)

# phantom route redirects
@forum.get("/post/")
def x():
    return redirect(url_for("general.index")), 301

@forum.route("/composer/", methods=["GET", "POST"])
@protectedPage
def composer():
    if request.method == "POST":
        post = Post.create(
            title = request.form.get("title"),
            raw = request.form.get("content"),
            excerpt = request.form.get("excerpt"),
            keywords = request.form.get("keywords")
        )
        if not post:
            return render_template("forum/composer.html")
        return redirect(url_for("forum.post", post_id=post.id))
    return render_template("forum/composer.html")

@forum.get("/pinned/")
def pinned_posts():
    return render_template("forum/pinned.html")

@forum.get("/post/<int:post_id>/")
def post(post_id: int):
    post = db.session.query(Post, User).filter(Post.user_id == User.id, Post.id == post_id).first()
    # don't forget skeleton.html meta author tag in case you update this!
    if post:
        title = TemplateParser.parseTitle(configurator.seoTitleFormat, configurator, post.Post.title)
        return render_template("forum/post.html", post=post, title=title)
    else:
        abort(404), 404

@forum.route("/post/<int:post_id>/editor/", methods=["GET", "POST"])
@protectedPage
def editor(post_id: int):
    if request.method == "POST":
        post = Post.query.filter_by(id=post_id).first()
        if post:
            post.update(
                raw = request.form.get("content"),
                excerpt = request.form.get("excerpt")
            )
        else:
            return abort(404), 404

    # joining queries for nicer look on the client side
    post = db.session.query(Post, User).filter(Post.user_id == User.id, Post.id == post_id).first()
    if post:
        return render_template("forum/editor.html", post=post)
    else:
        return abort(404), 404

@forum.post("/post/<int:post_id>/editor/delete/")
@protectedPage
def delete_post(post_id):
    post = Post.query.filter_by(id=post_id).first()
    if post:
        if post.user_id == session["user"]:
            db.session.delete(post)
            db.session.commit()
            flash("Post deleted", "success")

    return redirect(url_for("general.index"))

@forum.get("/category/<category>/")
def category(category: str):
    return render_template("forum/category.html")
