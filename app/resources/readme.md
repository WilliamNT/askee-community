# Application resources
This directory stores mandatory configuration files and other resources
required to run the site.

## Credit
languages.json: https://gist.github.com/piraveen/fafd0d984b2236e809d03a0e306c8a4d

## Configuration help
If config.json does not exist, the system will use the built in default values.
This will heavily impact SEO and will result in poor user experience so you
should configure the site before launching it to the masses. It's not even hard!

Social media optimization like Facebook's Open Graph markup is automatically handled
based on the configuration and each page's content.

config.json:
 - siteName: Appears on the navbar, home page title and several other places. Example: William's Tech community
 - siteTagline: Appears on the navbar. This should be a short, max. 35 character long tagline. Example: Your favorite tech community
 - seoDescription: Appears on search engine results and on some places (like sidebar) on the site.
 - seoTitleFormat: How search engines will show your page titles.
  - Templates: `%PAGE_TITLE%` `%SEPARATOR%` `%SITE_NAME%` `%SITE_TAGLINE%` and any other custom text. The templates are case sensitive
  and should have spaces between them as they are not spaced automatically.
  - `%SEPARATOR%` can be set in seoTitleSeparator.
  - Default seoTitleFormat: `%PAGE_TITLE% %SEPARATOR% %SITE_NAME%`. Example result: "Do you find turtles interesting? - MyCoolCommunity"
  - seoSiteKeywords: These are the default keywords for the site. The recommended number of keywords is between 4-6. Seperate them with a comma.
  - pageAuthor: Fallback author name if for some reason the actual page has no author information available. It's also used in some cases where
  the content can't be connected to a specific author. It's recommended to set this to the site's name or the team maintaining it.

### config.json example
config.json should be placed in the resources folder.
`{
    "siteName": "",
    "siteTagline": "",
    "seoDescription": "",
    "seoTitleFormat": "",
    "seoTitleSeparator": "",
    "seoSiteKeywords": "",
    "pageAuthor": ""
}`