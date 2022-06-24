from app import db, ph, configurator
from datetime import datetime
from sqlalchemy import func
from flask import flash, session
import re
import app.helpers as helpers
import markdown

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
        helpers.signIn(email, password)
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
        helpers.signOut()
        flash("Your account has been deleted successfully", "success")

    def flushContents(self) -> None:
        """
        Permanently delete all user generated content owned by the current user
        """
        Post.query.filter_by(user_id=self.id).delete()
        db.session.commit()

        flash("All user generated content has been deleted", "success")

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    content = db.Column(db.Text, nullable=False)
    markdown = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    category = db.Column(db.String, nullable=False)
    sticky = db.Column(db.Boolean, default=False)
    protected = db.Column(db.Boolean, default=False) # only signed in users can see the contents
    like = db.Column(db.Integer, nullable=False)
    excerpt = db.Column(db.Text(200), nullable=True)

    def create(self, title: str, content: str, sticky: bool=False, excerpt: str= None, category: str="uncategorized") -> object:
        """
        Create a new post in the database.
        """
        if not title:
            return flash("Title must be provided. Post has not been created", "warning")
        if len(title) < 3:
            return flash("Title length can't be shorter than 3 characters.")
        if len(title) > 120:
            return flash("Title length can't be longer than 100 characters")

        if not content:
            return flash("Content must be provided. Post has not been created", "warning")
        if len(content) < 100:
            if not helpers.getCurrentAccount().is_admin or not helpers.getCurrentAccount().is_system:
                return flash("Content length can't be shorter than 100 characters", "warning")
        if len(content) > 3000:
            return flash("Content length can't be longer than 1000 characters", "warning")
        
        if not excerpt:
            excerpt = configurator.seoDescription

        return self

    def transferOwnership(self, newOwnerId: int) -> None:
        newOwner = User.query.filter_by(id=newOwnerId)
        if newOwner:
            self.user_id = newOwner.id
        db.session.commit()