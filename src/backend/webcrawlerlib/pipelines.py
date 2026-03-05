import json
import uuid
from datetime import datetime, timezone

from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
from ..databaselib.db import Event, insert_event, insert_storage


class RawPayloadStoragePipeline:
    """
    Upload each scraped NewsItem as an immutable raw JSON payload.
    """

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        payload = adapter.asdict()

        event_id = str(uuid.uuid4())
        storage_path = f"{event_id}.json"
        raw_payload = json.dumps(payload, ensure_ascii=False)
        try:
            insert_storage(storage_path, raw_payload) # upload to storage first

            event = Event(
                event_id=event_id,
                event_type="news",
                source=str(payload.get("source") or "unknown"),
                published_at=str(
                    payload.get("published_at")
                    or datetime.now(timezone.utc).isoformat()
                ),
                region=str(payload.get("sourcecountry") or "global"),
                asset_classes=[],
                content=str(payload.get("raw") or payload.get("title") or ""),
                importance_score=0.0,
                entities={
                    "url": payload.get("url"),
                    "author": payload.get("author"),
                    "language": payload.get("language"),
                    "sourcecountry": payload.get("sourcecountry"),
                    "fetch_error": payload.get("fetch_error"),
                },
                topic="news",
                sentiment=self._sentiment_from_tone(payload.get("tone")),
                raw_payload_ref=storage_path,
            )
            insert_event(event)
        except Exception as exc:
            spider.logger.exception(
                "Failed to store NewsItem for %s: %s", payload.get("url"), exc
            )
            raise DropItem(f"Storage pipeline failed: {exc}") from exc

        spider.logger.info(
            "Stored raw payload and event for %s at %s", payload.get("url"), storage_path
        )
        return item

    @staticmethod
    def _sentiment_from_tone(tone: object) -> str:
        if tone is None:
            return "neutral"
        if isinstance(tone, (int, float)):
            if tone > 0:
                return "risk-on"
            if tone < 0:
                return "risk-off"
            return "neutral"

        text = str(tone).strip().lower()
        if "positive" in text:
            return "risk-on"
        if "negative" in text:
            return "risk-off"
        return "neutral"
