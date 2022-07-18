from datetime import datetime
import arrow
from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for, abort, session
from app.database import db, Post, User, Comment
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
            keywords = request.form.get("keywords").lower(),
            category = request.form.get("category").lower()
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
    print(post)
    # don't forget skeleton.html meta author tag in case you update this!
    if post:
        if post.Post.protected:
            return abort(403), 403
        if post.Post.deleted:
            return abort(410), 410
        comments = db.session.query(Comment, User).filter(Comment.post_id == post_id, Comment.user_id == User.id, Comment.deleted == False).all()
        return render_template("forum/post.html", post=post, comments=comments, commentCount=len(comments))
    else:
        return abort(404), 404

@forum.route("/post/<int:post_id>/editor/", methods=["GET", "POST"])
@protectedPage
def editor(post_id: int):
    post = Post.query.filter_by(id=post_id).first()
    if post and post.deleted:
        return abort(404), 404

    if request.method == "POST":
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
    if post and post.deleted:
        return abort(404), 404

    if post:
        if post.user_id == session["user"]:
            post.updated_at = datetime.utcnow()
            post.updated_by = 1 # 1 is the system's user id
            post.sticky = False
            post.protected = False
            post.excerpt = None
            post.locked = False
            post.pinned = False
            post.deleted = True

            flash("Post marked as deleted", "success")
            db.session.commit()

    return redirect(url_for("general.index"))

@forum.get("/categories/<category>/")
def category(category: str, page=1):
    page = request.args.get("p")
    category = category.lower().capitalize()

    if category in configurator.postCategories or category == "Uncategorized":
        posts = db.session.query(Post, User).filter(User.id == Post.user_id, Post.deleted == False, Post.category == category).paginate(page, 10, error_out=False)
        return render_template("forum/category.html", category=category, posts=posts)
    return abort(404), 404

@forum.get("/categories/")
def categories():
    return render_template("forum/categories.html")

@forum.post("/post/<int:post_id>/submit-comment/")
@protectedPage
def new_comment(post_id):
    post = Post.query.filter_by(id=post_id).first()
    if post and post.deleted:
        return abort(404), 404

    # return already handled in the create function
    return Comment.create(request.json["commentBody"], post.id, False)