from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from argon2 import PasswordHasher
from app.routes import forum
from app.utils import ApplicationConfigurator

app = Flask(__name__)
ph = PasswordHasher()

# dev secret key & database
app.config["SECRET_KEY"] = "KejF9nHarBUHnofa2rVMtKyR8Z7yapsrxTxh6EmN2eQgugkeL5UcdsYsW5K6CJGUuB8mXaJS9a8o4YuF5TzYtD64LqJpyQGwz4ETCj6YJzdcQG49H3nnD7vN9M2VPoiu"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///devdb.sqlite"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

configurator = ApplicationConfigurator()
configurator.loadConfig()
app.config["AC_SITE_TITLE"] = configurator.siteName
app.config["AC_SITE_TAGLINE"] = configurator.siteTagline
app.config["AC_SEO_DESCRIPTION"] = configurator.seoDescription
app.config["AC_SEO_TITLE_FORMAT"] = configurator.seoTitleFormat
app.config["AC_SEO_TITLE_SEPARATOR"] = configurator.seoTitleSeparator
app.config["AC_SEO_SITE_KEYWORDS"] = configurator.seoSiteKeywords
app.config["AC_PAGE_AUTHOR"] = configurator.pageAuthor

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