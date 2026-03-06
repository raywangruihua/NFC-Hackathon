import json

from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
from ..databaselib.db import ingest_raw_article


class RawPayloadStoragePipeline:
    """
    Upload each scraped NewsItem as an immutable raw JSON payload.
    """

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        payload = adapter.asdict()
        raw_payload = json.dumps(payload, ensure_ascii=False)
        source = str(payload.get("source") or "unknown")

        try:
            ingest_raw_article(raw_payload, source)
        except Exception as exc:
            spider.logger.exception(
                "Failed to store NewsItem for %s: %s", payload.get("url"), exc
            )
            raise DropItem(f"Storage pipeline failed: {exc}") from exc

        spider.logger.info(
            "Stored raw payload for %s via ingest_raw_article (source=%s)",
            payload.get("url"),
            source,
        )
        return item
