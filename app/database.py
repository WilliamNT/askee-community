from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import func
from flask import flash, session, redirect, url_for
import re
from app.utils import ph
from argon2.exceptions import VerifyMismatchError

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    is_admin = db.Column(db.Boolean, default=False)
    is_system = db.Column(db.Boolean, default=False)
    flair = db.Column(db.String(), nullable=True)
    locked = db.Column(db.Boolean, default=True)

    # EMAIL_REGEX = re.compile("^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$", re.IGNORECASE)

    def create(self, username: str, email: str, password: str, is_admin: bool=False) -> object:
        """
        Creates a new user in the database
        """

        # no need to store the email in any other format than lowercase
        email = email.lower()

        if not email:
            return flash("You have to provide an email address", "warning")
        if len(email) <= 3:
            # https://stackoverflow.com/questions/1423195/what-is-the-actual-minimum-length-of-an-email-address-as-defined-by-the-ietf
            return flash("Email address is too short", "warning")
        if len(email) > 255:
            return flash("Email address is too long (max. 120 characters)", "warning")

        if not username:
            return flash("You have to provide a username", "warning")
        if len(username) < 6:
            return flash("Username is too short (min. 6 characters)", "warning")
        if len(username) > 80:
            return flash("Username is too long (max. 80 characters)", "warning")
        if username.lower() == email.lower():
            return flash("Username cannot be the same as email", "warning")
        if not re.match("^[a-zA-Z0-9_]", username):
            return flash("Username can only contain lower and upper case letters (A-Z), numbers (0-9) and _")

        if not password:
            return flash("You have to provide a password", "warning")
        if len(password) < 8:
            return flash("Password is too short (min. 8 characters)", "warning")
        if len(password) > 100:
            return flash("Password is too long (max. 100 characters)", "warning")
        if password == username:
            return flash("Password cannot be the same as username", "warning")
        if password == email:
            return flash("Password cannot be the same as email address", "warning")

        # delaying database queries for performance gain on lower end systems
        if not User.query.filter(func.lower(User.username) == func.lower(username)).first():
            self.username = username
        else:
            return flash("Username already in use", "warning")

        if not User.query.filter(func.lower(User.email) == func.lower(email)).first():
            self.email = str(email).lower()
        else:
            return flash("Email address already in use", "warning")

        self.password = ph.hash(password)
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

        # ensuring that only one user is set as system
        users = User.query.all()
        if len(users) == 0:
            self.is_system = True
            self.is_admin = True
            self.locked = False
        else:
            self.is_system = False
            self.is_admin = is_admin
            if is_admin == True:
                self.locked = False

        db.session.add(self)
        db.session.commit()
        flash("Account created", "success")
        Authentication.signIn(email, password)
        return self

    def update(self, is_admin: bool=None, username: str=None, email: str=None, password: str=None) -> object:
        """
        Update the current user's database record
        """
        if username:
            if not User.query.filter(func.lower(User.username) == func.lower(username)).first():
                self.username = username
            else:
                return flash("Username already in use", "warning")

        if email:
            if not User.query.filter(func.lower(User.email) == func.lower(email)).first():
                self.email = str(email).lower()
            else:
                return flash("Email address already in use", "warning")

        if password:
            self.password = ph.hash(password)
        self.updated_at = datetime.utcnow()

        if session["user"]:
            self.updated_by = session["user"]
        else:
            self.updated_by = 1 # presuming ID 1 is the system

        if is_admin == True:
            self.locked = False

        db.session.commit()
        flash("User update successful", "success")
        return self

    def delete(self) -> None:
        """
        Permanently delete the current user from the database
        """
        db.session.delete(self)
        db.session.commit()
        self.signOut()
        flash("Your account has been deleted successfully", "success")

    def flushContents(self) -> None:
        """
        Permanently delete all user generated content owned by the current user
        """
        Post.query.filter_by(user_id=self.id).delete()
        db.session.commit()

        flash("All user generated content has been deleted", "success")

class Authentication():
    def signIn(email: str, password: str) -> None:
        """
        Handles the sign in process, is independent of the user object
        """
        if not email:
            flash("Please provide an email address", "warning")
            return redirect(url_for("security.sign_in"))
        if not password:
            flash("Please provide a password", "warning")
            return redirect(url_for("security.sign_in"))

        user = User.query.filter_by(email=email.lower()).first()
        if user:
            try:
                ph.verify(user.password, password)
                session["user"] = user.id
                session["username"] = user.username

                flash("Sign in successful", "success")
                return redirect(url_for("general.index"))
            except VerifyMismatchError:
                flash("Incorrect password", "warning")
                return redirect(url_for("security.sign_in"))
        else:
            flash(f"No account uses \"{email}\"", "warning")
            return redirect(url_for("security.sign_in"))

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    markdown = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    category = db.Column(db.String, nullable=False)
    sticky = db.Column(db.Boolean, default=False) # first item shown in the post's category
    protected = db.Column(db.Boolean, default=False) # only signed in users can see the contents
    like = db.Column(db.Integer, nullable=False, default=0)
    dislike = db.Column(db.Integer, nullable=False, default=0)
    excerpt = db.Column(db.Text(200), nullable=True)
    locked = db.Column(db.Boolean, default=False) # nobody can reply or edit the post
    keywords = db.Column(db.String, nullable=False)
    pinned = db.Column(db.Boolean, default=False) # shown in the pinned posts section
    deleted = db.Column(db.Boolean, default=False) # the idea is that we can display a message saying the content was deleted

    @classmethod
    def create(cls, title: str, raw: str, sticky: bool=False, excerpt: str= None, category: str="uncategorized", protected: bool=False, locked: bool=False, keywords: str=None) -> object:
        """
        Create a new post in the database.
        """
        if not title:
            flash("Title must be provided. Post has not been created", "warning")
            return None
        if len(title) < 3:
            flash("Title length can't be shorter than 3 characters.")
            return None
        if len(title) > 120:
            flash("Title length can't be longer than 100 characters")
            return None
        if not raw:
            flash("Content must be provided. Post has not been created", "warning")
            return None
        if len(raw) < 10:
            flash("Content length can't be shorter than 10 characters", "warning")
            return None
        if len(raw) > 3000:
            flash("Content length can't be longer than 1000 characters", "warning")
            return None

        post = cls()
        post.title = title
        post.markdown = raw
        post.updated_by = session["user"]
        post.user_id = session["user"]
        post.category = category
        post.sticky = sticky
        post.protected = protected
        post.locked = locked
        post.keywords = keywords

        db.session.add(post)
        db.session.commit()
        flash("Post published", "success")
        return post

    def update(self, raw: str, sticky: bool=False, excerpt: str= None, category: str="uncategorized", protected: bool=False, locked: bool=False, keywords: str=None) -> object:
        """
        Updates the current post in the database.
        """

        if raw and self.markdown != raw:
            self.markdown = raw
        if len(raw) < 10:
            return flash("Content length can't be shorter than 10 characters", "warning")
        if len(raw) > 3000:
            return flash("Content length can't be longer than 1000 characters", "warning")

        if category != self.category:
            self.category = category
        if self.sticky and self.sticky != sticky:
            self.sticky = sticky
        if self.protected and self.protected != protected:
            self.protected = protected
        if self.locked and self.locked != locked:
            self.locked = locked


        self.updated_by = session["user"]
        self.updated_at = datetime.utcnow()

        db.session.commit()
        flash(f"Changes saved", "success")
        return self

    def transferOwnership(self, newOwnerId: int) -> None:
        newOwner = User.query.filter_by(id=newOwnerId)
        if newOwner:
            self.user_id = newOwner.id
        db.session.commit()
