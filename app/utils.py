import json
import os

class ApplicationConfigurator():
    # Do not directly modify these values. Set custom properties in resources/config.json
    DEFAULT_SITENAME = "New Q&A forum"
    DEFAULT_SITETAGLINE = "The site owner has not finished setting up the forum yet. Come back later!"
    DEFAULT_SEODESCRIPTION = "This is where the site's introduction goes."
    DEFAULT_SEOTITLEFORMAT = "%PAGE_TITLE% %SEPARATOR% %SITE_NAME%"
    DEFAULT_SEOTITLESEPARATOR = "-"
    DEFAULT_SEOSITEKEYWORDS = "forum, community, askee"
    DEFAULT_PAGEAUTHOR = "Somebody"

    def __init__(self) -> None:
        # Site about
        self.siteName = self.DEFAULT_SITENAME
        self.siteTagline = self.DEFAULT_SITETAGLINE
        self.seoDescription = self.DEFAULT_SEODESCRIPTION
        self.seoTitleFormat = self.DEFAULT_SEOTITLEFORMAT
        self.seoTitleSeparator = self.DEFAULT_SEOTITLESEPARATOR
        self.seoSiteKeywords = self.DEFAULT_SEOSITEKEYWORDS
        self.pageAuthor = self.DEFAULT_PAGEAUTHOR

        self.loadConfig()
        
    def loadConfig(self) -> None:
        configPath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "resources/config.json")
        if os.path.isfile(configPath):
            config = None
            with open(configPath, encoding="utf-8") as config:
                config = json.load(config)

            self.siteName = config["siteName"]
            self.siteTagline = config["siteTagline"]
            self.seoDescription = config["seoDescription"]
            self.seoTitleFormat = config["seoTitleFormat"]
            self.seoTitleSeparator = config["seoTitleSeparator"]
            self.seoSiteKeywords = config["seoSiteKeywords"]
            self.pageAuthor = config["pageAuthor"]

            print("Configuration loaded.")
        else:
            self.siteName = self.DEFAULT_SITENAME
            self.siteTagline = self.DEFAULT_SITETAGLINE
            self.seoDescription = self.DEFAULT_SEODESCRIPTION
            self.seoTitleFormat = self.DEFAULT_SEOTITLEFORMAT
            self.seoTitleSeparator = self.DEFAULT_SEOTITLESEPARATOR
            self.seoSiteKeywords = self.DEFAULT_SEOSITEKEYWORDS
            self.pageAuthor = self.DEFAULT_PAGEAUTHOR
            print("Configuration file (resources/config.json) could not be found. Proceeding with default values. This will lead to poor user experience. Please set up the site properly.")

    def reloadConfiguration(self) -> None:
        print("Reloading configuration")
        self.loadConfig()

class TemplateParser():
    LEGAL_KEYWORDS = [
        "%PAGE_TITLE%",
        "%SEPARATOR%",
        "%SITE_NAME%",
        "%SITE_TAGLINE%"
    ]


    def titleParser(raw: str, config: dict, pageTitle: str=None) -> str:
        raw = str(raw)

        if "%PAGE_TITLE%" in raw:
            if pageTitle:
                raw.replace("%PAGE_TITLE%", pageTitle)
            else:
                raise ValueError("%PAGE_TITLE% was found in raw string but pageTitle was not set.")
        if "%SEPARATOR%" in raw:
            raw.replace("%SEPARATOR%", config.seoTitleSeparator)
        if "%SITE_NAME%" in raw:
            raw.replace("%SITE_NAME%", config.siteName)
        if "%SITE_TAGLINE%" in raw:
            raw.replace("%SITE_TAGLINE%", config.siteTagline)
        return raw

    def textParser(raw: str, templates: dict) -> str:
        raw = str(raw)
        for template, replacement in templates.items():
            if not str(template).startswith("%") or not str(template).endswith("%") or not str(template).isupper():
                raise ValueError(f"Invalid template {template}. Template strings must be upper case and have to start and end with \"%\".")
            if template in raw:
                raw = raw.replace(template, replacement)
        return raw