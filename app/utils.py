import json
import os
import sys
from argon2 import PasswordHasher
from flask import session, abort, request
from functools import wraps

class ApplicationConfigurator():
    # Do not directly modify these values. Set custom properties in resources/config.json (refer to the readme in the same directory for more information)
    DEFAULT_SITENAME = "New Q&A forum"
    DEFAULT_SITETAGLINE = "The site owner has not finished setting up the forum yet. Come back later!"
    DEFAULT_SEODESCRIPTION = "This is where the site's introduction goes."
    DEFAULT_SEOTITLEFORMAT = "%PAGE_TITLE% %SEPARATOR% %SITE_NAME%"
    DEFAULT_SEOTITLESEPARATOR = "-"
    DEFAULT_SEOSITEKEYWORDS = "forum, community, askee"
    DEFAULT_PAGEAUTHOR = "Somebody"
    DEFAULT_CONTENTLIABILITYWARNING = False
    DEFAULT_POSTCATEGORIES = ["uncategorized"]

    def __init__(self) -> None:
        # site config
        self.siteName = self.DEFAULT_SITENAME
        self.siteTagline = self.DEFAULT_SITETAGLINE
        self.seoDescription = self.DEFAULT_SEODESCRIPTION
        self.seoTitleFormat = self.DEFAULT_SEOTITLEFORMAT
        self.seoTitleSeparator = self.DEFAULT_SEOTITLESEPARATOR
        self.seoSiteKeywords = self.DEFAULT_SEOSITEKEYWORDS
        self.pageAuthor = self.DEFAULT_PAGEAUTHOR
        self.contentLiabilityWarning = self.DEFAULT_CONTENTLIABILITYWARNING
        self.postCategories = self.DEFAULT_POSTCATEGORIES

        # system config
        self.releaseVersion = None
        self.displaySystemMessages = False
        self.timeZone = None
        self.language = "en"

        self.loadConfig()
        
    def loadConfig(self) -> None:
        configPath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "resources", "config.json")
        systemConfigPath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "resources", "system.json")
        if os.path.isfile(systemConfigPath):
            systemConfig = None
            with open(systemConfigPath, encoding="utf-8") as sysconfig:
                systemConfig = json.load(sysconfig)

            try:
                self.releaseVersion = systemConfig["version"]
                self.displaySystemMessages = systemConfig["displaySystemMessages"]
                self.timeZone = systemConfig["timeZone"]
                self.language = systemConfig["language"]
            except KeyError:
                print(F"[ASKEE] Invalid system configuration file (resources/system.json). JSON key {sys.exc_info()[1]} is missing from the configuration.")

        else:
            print("[ASKEE] System configuration not found. Attempting application shutdown...")
            # this is from an older implementation, but I'm keeping the error message for future use: 
            # [ASKEE] Failed to shutdown the application, however due to the missing system configuration an exception will occur at some point, most likely leading to data loss. Please stop the process manually.
            # question: should we do this in another way?
            RuntimeError("[ASKEE] Shutdown successful.")

        if os.path.isfile(configPath):
            config = None
            with open(configPath, encoding="utf-8") as config:
                config = json.load(config)
            
            try:
                self.siteName = config["siteName"]
                self.siteTagline = config["siteTagline"]
                self.seoDescription = config["seoDescription"]
                self.seoTitleFormat = config["seoTitleFormat"]
                self.seoTitleSeparator = config["seoTitleSeparator"]
                self.seoSiteKeywords = config["seoSiteKeywords"]
                self.pageAuthor = config["pageAuthor"]
                self.contentLiabilityWarning = config["contentLiabilityWarning"]
                self.postCategories = config["postCategories"]
            except KeyError:
                print(F"[ASKEE] Invalid configuration file (resources/config.json). JSON key {sys.exc_info()[1]} is missing from the configuration. Proceeding with default values.")

            print("[ASKEE] Configuration loaded.")
        else:
            print("[ASKEE] Configuration file (resources/config.json) could not be found, proceeding with default values. This will lead to poor user experience. Please set up the site properly.")

    def reloadConfiguration(self) -> None:
        """
        Reloads the configuration. Basically it calls loadConfig() and prints a log message before.
        """
        print("[ASKEE] Reloading configuration")
        self.loadConfig()

    def resetConfig(self) -> None:
        """
        Resets the configuration to the application's built in defaults values.
        """
        self.siteName = self.DEFAULT_SITENAME
        self.siteTagline = self.DEFAULT_SITETAGLINE
        self.seoDescription = self.DEFAULT_SEODESCRIPTION
        self.seoTitleFormat = self.DEFAULT_SEOTITLEFORMAT
        self.seoTitleSeparator = self.DEFAULT_SEOTITLESEPARATOR
        self.seoSiteKeywords = self.DEFAULT_SEOSITEKEYWORDS
        self.pageAuthor = self.DEFAULT_PAGEAUTHOR
        self.contentLiabilityWarning = self.DEFAULT_CONTENTLIABILITYWARNING
        self.postCategories = self.DEFAULT_POSTCATEGORIES

        print("[ASKEE] Configuration reset done")

class TemplateParser():
    def parseTitle(raw: str, config: dict, pageTitle: str=None) -> str:
        """
        Parses the raw content title and returns a string with the templates
        replaced with the actual values
        """

        if "%PAGE_TITLE%" in raw:
            if pageTitle:
                raw = raw.replace("%PAGE_TITLE%", pageTitle)
            else:
                raise ValueError("%PAGE_TITLE% was found in raw string but pageTitle was not set.")
        if "%SEPARATOR%" in raw:
            raw = raw.replace("%SEPARATOR%", config.seoTitleSeparator)
        if "%SITE_NAME%" in raw:
            raw = raw.replace("%SITE_NAME%", config.siteName)
        if "%SITE_TAGLINE%" in raw:
            raw = raw.replace("%SITE_TAGLINE%", config.siteTagline)
        return raw

    def parseText(raw: str, templates: dict) -> str:
        """
        Parses the raw text and replaces templates based on the
        templates dictionary provided
        """
        raw = str(raw)
        for template, replacement in templates.items():
            if not str(template).startswith("%") or not str(template).endswith("%") or not str(template).isupper():
                raise ValueError(f"Invalid template {template}. Template strings must be upper case and have to start and end with \"%\".")
            if template in raw:
                raw = raw.replace(template, replacement)
        return raw

def protectedPage(f):
    """
    Redirects unauthorized users to the sign in page
    """
    @wraps(f)
    def decoratedFunction(*args, **kwargs):
        if not "user" in session:
            return abort(403), 403
        return f(*args, **kwargs)
    return decoratedFunction

# objects
configurator = ApplicationConfigurator()
ph = PasswordHasher()