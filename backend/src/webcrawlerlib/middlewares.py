from urllib.parse import urlparse

from scrapy.downloadermiddlewares.retry import get_retry_request
from scrapy.exceptions import IgnoreRequest
from twisted.internet.error import (
    ConnectError,
    ConnectionDone,
    ConnectionLost,
    DNSLookupError,
    TCPTimedOutError,
    TimeoutError,
)


class QualityDownloaderMiddleware:
    """
    Implements retry logic. Optional allowlist enforcement.
    - Retry on retryable HTTP statuses.
    - Retry on connection/timeout errors.
    - Retry if body looks like a block/challenge page.
    """

    NETWORK_EXCEPTIONS = (
        TimeoutError,
        TCPTimedOutError,
        DNSLookupError,
        ConnectionRefusedError,
        ConnectionDone,
        ConnectError,
        ConnectionLost,
    )

    @classmethod
    def from_crawler(cls, crawler):
        instance = cls(crawler)
        return instance

    def __init__(self, crawler):
        self.crawler = crawler
        self.settings = crawler.settings

        # allowlist
        self.allowed_domains = {
            d.lower().strip()
            for d in self.settings.getlist("ALLOWED_CRAWL_DOMAINS")
            if d and d.strip()
        }
        self.retry_http_codes = set(self.settings.getlist("CUSTOM_RETRY_HTTP_CODES"))
        self.block_markers = [
            m.lower() for m in self.settings.getlist("BLOCK_PAGE_MARKERS") if m
        ]
        self.retry_max_times = self.settings.getint("CUSTOM_RETRY_MAX_TIMES", 3)

    def process_request(self, request, spider):
        """
        Filter domains based on allowlist
        """
        if not self.allowed_domains:
            return None

        netloc = (urlparse(request.url).hostname or "").lower()
        if netloc and not any(
            netloc == domain or netloc.endswith("." + domain)
            for domain in self.allowed_domains
        ):
            raise IgnoreRequest(
                f"Blocked by ALLOWED_CRAWL_DOMAINS policy: {request.url}"
            )
        return None

    def process_response(self, request, response, spider):

        if response.status in self.retry_http_codes:
            retry_req = self._retry(request, spider, reason=f"http_{response.status}")
            if retry_req:
                return retry_req

        if response.status == 200 and self._looks_blocked(response):
            retry_req = self._retry(request, spider, reason="blocked_page_marker")
            if retry_req:
                return retry_req

        return response

    def process_exception(self, request, exception, spider):
        if isinstance(exception, self.NETWORK_EXCEPTIONS):
            return self._retry(request, spider, reason=exception.__class__.__name__)
        return None

    def _retry(self, request, spider, reason):
        """
        Retry request if max retry times not exceeded.
        """
        retry_req = get_retry_request(
            request=request,
            spider=spider,
            reason=reason,
            max_retry_times=self.retry_max_times,
            priority_adjust=-1,
        )
        if retry_req:
            retry_times = retry_req.meta.get("retry_times", 0)
            spider.logger.warning(
                "Retrying %s (reason=%s, retry_times=%s)",
                request.url,
                reason,
                retry_times,
            )
        return retry_req

    def _looks_blocked(self, response):
        """
        Check for block text.
        """
        if not self.block_markers:
            return False
        body = (response.text or "").lower()
        return any(marker in body for marker in self.block_markers)
