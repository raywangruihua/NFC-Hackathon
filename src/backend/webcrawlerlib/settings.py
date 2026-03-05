# Scrapy settings
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = "webcrawlerlib"

SPIDER_MODULES = ["backend.webcrawlerlib.spiders"]
NEWSPIDER_MODULE = "backend.webcrawlerlib.spiders"

ADDONS = {}

# Logging: show only high-signal crawl diagnostics by default.
LOG_LEVEL = "WARNING"
LOG_SHORT_NAMES = True


# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = "webcrawlerlib/1.0 (+contact: rwang043@e.ntu.edu.sg)"

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Concurrency and throttling settings
#CONCURRENT_REQUESTS = 16
CONCURRENT_REQUESTS_PER_DOMAIN = 1
DOWNLOAD_DELAY = 1

# GDELT DOC 2.0 defaults (used by gdelt spider)
GDELT_QUERY = '("credit risk" OR "liquidity risk" OR inflation OR "interest rate" OR recession OR volatility)'
GDELT_TIMESPAN = "7days"
GDELT_MAXRECORDS = 10

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
DEFAULT_REQUEST_HEADERS = {
   "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
   "Accept-Language": "en",
}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    "tutorial.middlewares.TutorialSpiderMiddleware": 543,
#}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    "backend.webcrawlerlib.middlewares.QualityDownloaderMiddleware": 543,
}

# Domain policy: keep empty list to disable allowlist filtering
ALLOWED_CRAWL_DOMAINS = []

# Middleware retry controls
CUSTOM_RETRY_HTTP_CODES = [429, 500, 502, 503, 504]
CUSTOM_RETRY_MAX_TIMES = 3
RETRY_ENABLED = False

# Markers for common anti-bot/challenge pages
BLOCK_PAGE_MARKERS = [
    "access denied",
    "temporarily unavailable",
    "verify you are human",
    "captcha",
    "request blocked",
]

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    "scrapy.extensions.telnet.TelnetConsole": None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    "backend.webcrawlerlib.pipelines.RawPayloadStoragePipeline": 300,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = "httpcache"
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

# Set settings whose default value is deprecated to a future-proof value
FEED_EXPORT_ENCODING = "utf-8"
