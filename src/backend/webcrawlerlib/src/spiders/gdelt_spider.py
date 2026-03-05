import json
from urllib.parse import quote_plus, urlparse

import scrapy
from ..items import NewsItem


class GdeltSpider(scrapy.Spider):
    name = "gdelt"

    def start_requests(self):
        """
        Returns HTTP requests from GDELT endpoint. Configure query, timespan and maxrecords via settings.py
        """
        query = self.settings.get(
            "GDELT_QUERY",
            '("credit risk" OR "liquidity risk" OR inflation OR "interest rate" OR recession OR volatility)',
        )
        timespan = self.settings.get("GDELT_TIMESPAN", "7days")
        maxrecords = int(self.settings.get("GDELT_MAXRECORDS", 100))

        url = (
            "https://api.gdeltproject.org/api/v2/doc/doc"
            f"?query={quote_plus(query)}"
            "&mode=artlist"
            f"&maxrecords={maxrecords}"
            f"&timespan={timespan}"
            "&format=json"
            "&sort=datedesc"
        )

        yield scrapy.Request(url, callback=self.parse_gdelt_feed)

    def parse_gdelt_feed(self, response):
        if response.status != 200:
            self.logger.warning("GDELT API non-200 response: status=%s url=%s", response.status, response.url)
            return

        content_type = response.headers.get("Content-Type", b"").decode("latin1").lower()
        if "json" not in content_type:
            snippet = (response.text or "").strip().replace("\n", " ")[:300]
            self.logger.warning(
                "GDELT API non-JSON response: content_type=%s url=%s body_snippet=%r",
                content_type,
                response.url,
                snippet,
            )
            return

        try:
            data = json.loads(response.text)
        except json.JSONDecodeError:
            snippet = (response.text or "").strip().replace("\n", " ")[:300]
            self.logger.warning("GDELT API invalid JSON: url=%s body_snippet=%r", response.url, snippet)
            return

        articles = data.get("articles", [])

        if not articles:
            self.logger.warning("No articles returned from GDELT DOC 2.0")
            return

        for article in articles:
            article_url = article.get("url")
            if not article_url:
                continue

            meta = {
                "gdelt": {
                    "title": article.get("title"),
                    "seendate": article.get("seendate"),
                    "socialimage": article.get("socialimage"),
                    "domain": article.get("domain"),
                    "language": article.get("language"),
                    "sourcecountry": article.get("sourcecountry"),
                    "tone": article.get("tone"),
                }
            }
            yield scrapy.Request(
                article_url,
                callback=self.parse_article,
                errback=self.parse_article_error,
                meta=meta,
                dont_filter=True,
            )

    def parse_article(self, response):
        gdelt_meta = response.meta.get("gdelt", {})

        published_at = (
            response.css("meta[property='article:published_time']::attr(content)").get()
            or response.css("meta[name='pubdate']::attr(content)").get()
            or response.css("time::attr(datetime)").get()
        )
        author = (
            response.css("meta[name='author']::attr(content)").get()
            or response.css("[rel='author']::text").get()
            or response.css("[class*='author']::text").get()
        )

        paragraphs = response.css("article p::text, main p::text, p::text").getall()
        body = " ".join(p.strip() for p in paragraphs if p.strip())

        path_parts = [p for p in urlparse(response.url).path.split("/") if p]

        yield NewsItem(
            title=gdelt_meta.get("title"),
            language=gdelt_meta.get("language"),
            sourcecountry=gdelt_meta.get("sourcecountry"),
            source=gdelt_meta.get("domain"),
            url=response.url,
            published_at=published_at if published_at else None,
            author=author.strip() if author else None,
            section=path_parts[0] if path_parts else None,
            body=body,
            tone=gdelt_meta.get("tone"),
            fetch_error=None,
        )

    def parse_article_error(self, failure):
        request = failure.request
        gdelt_meta = request.meta.get("gdelt", {})
        self.logger.warning("Failed to fetch article url=%s err=%s", request.url, failure.value)
        yield NewsItem(
            title=gdelt_meta.get("title"),
            language=gdelt_meta.get("language"),
            sourcecountry=gdelt_meta.get("sourcecountry"),
            source=gdelt_meta.get("domain"),
            url=request.url,
            published_at=None,
            author=None,
            section=None,
            body=None,
            tone=gdelt_meta.get("tone"),
            fetch_error=str(failure.value),
        )
