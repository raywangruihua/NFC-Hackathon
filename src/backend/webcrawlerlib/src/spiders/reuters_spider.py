import json
from urllib.parse import urlparse

from scrapy.spiders import SitemapSpider


class ReutersSpider(SitemapSpider):
    name = "reuters"
    allowed_domains = ["reuters.com"]

    sitemap_urls = [
        "https://www.reuters.com/arc/outboundfeeds/sitemap-index/?outputType=xml",
        "https://www.reuters.com/arc/outboundfeeds/news-sitemap-index/?outputType=xml",
        "https://www.reuters.com/plus/sitemap-index.xml",
        "https://www.reuters.com/arc/outboundfeeds/sitemap-plj-index/?outputType=xml",
        "https://www.reuters.com/graphics/sitemap.xml",
        "https://www.reuters.com/arc/outboundfeeds/sitemap-index/pictures/?outputType=xml",
        "https://www.reuters.com/static/video-sitemap/us/sitemap_video_index.xml",
        "https://www.reuters.com/arc/outboundfeeds/topic-sitemap/?outputType=xml",
        "https://www.reuters.com/arc/outboundfeeds/author-sitemap/?outputType=xml",
        "https://www.reuters.com/arc/outboundfeeds/pressrelease-sitemap/?outputType=xml",
    ]

    sitemap_rules = [(r".*", "parse_article")]

    custom_settings = {
        "ROBOTSTXT_OBEY": True,
        "DOWNLOAD_DELAY": 0.5,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 2,
    }

    def parse_article(self, response):
        title = (
            response.css("meta[property='og:title']::attr(content)").get()
            or response.css("h1::text").get()
        )
        published_at = (
            response.css("meta[property='article:published_time']::attr(content)").get()
            or response.css("time::attr(datetime)").get()
        )

        author = (
            response.css("meta[name='author']::attr(content)").get()
            or response.css("[data-testid='Byline'] *::text").get()
        )

        paragraphs = response.css(
            "[data-testid='paragraph']::text, article p::text, main p::text"
        ).getall()
        body = " ".join(p.strip() for p in paragraphs if p.strip())

        if not title:
            return

        tags = []
        keywords = response.css("meta[name='news_keywords']::attr(content)").get()
        if keywords:
            tags = [k.strip() for k in keywords.split(",") if k.strip()]

        json_ld = response.css("script[type='application/ld+json']::text").get()
        if json_ld:
            try:
                data = json.loads(json_ld)
                if isinstance(data, dict):
                    tags = data.get("keywords", tags) if isinstance(data.get("keywords", tags), list) else tags
            except Exception:
                pass

        path_parts = [p for p in urlparse(response.url).path.split("/") if p]

        yield {
            "source": "Reuters",
            "url": response.url,
            "title": title.strip(),
            "published_at": published_at,
            "author": author.strip() if author else None,
            "section": path_parts[0] if path_parts else None,
            "tags": tags,
            "body": body,
        }
