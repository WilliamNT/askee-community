from flask import Flask, jsonify, redirect, render_template, session, url_for, flash
from app.utils import configurator, TemplateParser
from flaskext.markdown import Markdown
import arrow

app = Flask(__name__)

# dev secret key & database
app.config["SECRET_KEY"] = "KejF9nHarBUHnofa2rVMtKyR8Z7yapsrxTxh6EmN2eQgugkeL5UcdsYsW5K6CJGUuB8mXaJS9a8o4YuF5TzYtD64LqJpyQGwz4ETCj6YJzdcQG49H3nnD7vN9M2VPoiu"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///devdb.sqlite"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

from app.database import User, db
db.init_app(app)
Markdown(app)

# ApplicationConfigurator
# site config
app.config["AC_SITE_TITLE"] = configurator.siteName
app.config["AC_SITE_TAGLINE"] = configurator.siteTagline
app.config["AC_SEO_DESCRIPTION"] = configurator.seoDescription
app.config["AC_SEO_TITLE_FORMAT"] = configurator.seoTitleFormat
app.config["AC_SEO_TITLE_SEPARATOR"] = configurator.seoTitleSeparator
app.config["AC_SEO_SITE_KEYWORDS"] = configurator.seoSiteKeywords
app.config["AC_PAGE_AUTHOR"] = configurator.pageAuthor
app.config["AC_CONTENT_LIABILITYWARNING"] = configurator.contentLiabilityWarning
app.config["AC_POST_CATEGORIES"] = configurator.postCategories
# system config
app.config["AC_SYSTEM_VERSION"] = configurator.releaseVersion
app.config["AC_SYSTEM_MESSAGES"] = configurator.displaySystemMessages
app.config["AC_SYSTEM_TIMEZONE"] = configurator.timeZone
app.config["AC_SYSTEM_LANGUAGE"] = configurator.language

# routes
from app.routes.general import general
app.register_blueprint(general)

from app.routes.security import security
app.register_blueprint(security)

from app.routes.admin import admin
app.register_blueprint(admin)

from app.routes.forum import forum
app.register_blueprint(forum)

from app.routes.info import info
app.register_blueprint(info)

# error pages
@app.errorhandler(404)
def notFound(e) -> None:
    return render_template("errorpages/404.html"), 404
app.register_error_handler(404, notFound)

@app.errorhandler(403)
def forbidden(e) -> None:
    return render_template("errorpages/403.html"), 403
app.register_error_handler(403, forbidden)

@app.errorhandler(410)
def forbidden(e) -> None:
    return render_template("errorpages/410.html"), 410
app.register_error_handler(410, forbidden)

@app.errorhandler(500)
def forbidden(e) -> None:
    return render_template("errorpages/500.html"), 500
app.register_error_handler(500, forbidden)

# events
@app.before_request
def refreshSessionUserDetails() -> None:
    """
    Ensures that all user data stored in the session is up to date
    """
    if "user" in session:
        user = User.query.filter_by(id=session["user"]).first()
        if user:
            # if the user is not found, the account was most likely deleted
            session["user"] = user.id
            session["username"] = user.username
            session["isAdmin"] = user.is_admin
            session["isSystem"] = user.is_system
        else:
            session.clear()
            flash("There was an error with your session, please sign in again", "warning")
            return redirect(url_for("security.sign_in"))

@app.before_first_request
def configureSession() -> None:
    """
    Configures the session
    """
    session.permanent = True

@app.template_filter()
def localizeDateTime(utcStamp: str):
    """
    Retrieves the timezone of the system using the AC_SYSTEM_TIMEZONE variable and localizes the UTC time stamp.
    """
    stamp = arrow.get(utcStamp)
    stamp = stamp.to(app.config["AC_SYSTEM_TIMEZONE"])
    stamp = stamp.format("YYYY.MM.DD. HH:mm") # ISO-8601 format
    #stamp = stamp.humanize()
    return f"{stamp} ({app.config['AC_SYSTEM_TIMEZONE']})"

@app.template_filter()
def prettifyDateTime(utcStamp: str):
    """
    Retrieves the timezone of the system using the AC_SYSTEM_TIMEZONE variable and turns the UTC time stamp into a human friendly format.
    """
    stamp = arrow.get(utcStamp)
    stamp = stamp.to(app.config["AC_SYSTEM_TIMEZONE"])
    return stamp.humanize()

@app.context_processor
def createTitleUtility():
    """
    Returns the title for the page like defined in the site title template.
    """
    def createTitle(pageTitle: str):
        return TemplateParser.parseTitle(app.config["AC_SEO_TITLE_FORMAT"], configurator, pageTitle)
    return dict(createTitle=createTitle)