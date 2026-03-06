import json
from urllib.parse import quote_plus, urlparse

import scrapy
from ..items import NewsItem


class GdeltSpider(scrapy.Spider):
    name = "gdelt"

    def start_requests(self):
        """
        Start crawling by sending a request to GDELT endpoint, which returns a list of articles related to the query.
        Default values for query, timespan and maxrecords are used if not founding in crawler settings.
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
        self.logger.warning(
            "Starting GDELT crawl: query=%r timespan=%s maxrecords=%s",
            query,
            timespan,
            maxrecords,
        )

        yield scrapy.Request(url, callback=self.parse_gdelt_feed) # get gdelt response

    def parse_gdelt_feed(self, response):
        """
        Iterate, crawl and scrape articles returned by GDELT endpoint.
        """
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

        self.logger.warning("GDELT returned %s candidate articles", len(articles))

        for article in articles:
            article_url = article.get("url")
            if not article_url:
                continue

            lang = (article.get("language") or "").lower()
            if lang and lang != "english":
                self.logger.info("Skipping non-English article lang=%s url=%s", lang, article_url)
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
        """
        Return metadata and raw article HTML as JSON.
        """
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

        paragraph_text_nodes = response.xpath("//p//text()").getall()
        text = " ".join(t.strip() for t in paragraph_text_nodes if t and t.strip())

        yield NewsItem(
            title=gdelt_meta.get("title"),
            language=gdelt_meta.get("language"),
            sourcecountry=gdelt_meta.get("sourcecountry"),
            source=gdelt_meta.get("domain"),
            url=response.url,
            published_at=published_at if published_at else None,
            author=author.strip() if author else None,
            text=text,
            tone=gdelt_meta.get("tone"),
            fetch_error=None,
        )

    def parse_article_error(self, failure):
        """
        Tries to return as much information as possible as JSON during failure.
        """
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
            text=None,
            tone=gdelt_meta.get("tone"),
            fetch_error=str(failure.value),
        )
