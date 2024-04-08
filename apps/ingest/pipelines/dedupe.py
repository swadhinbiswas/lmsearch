"""Scrapy pipeline wrapper around dedupe_items (process-local seen-set)."""

from apps.ingest.dedupe import is_duplicate


class DedupePipeline:
    def __init__(self):
        self.seen_titles: list[str] = []

    def process_item(self, item, spider):
        from scrapy.exceptions import DropItem

        title = item.get("title", "")
        if any(is_duplicate(title, s) for s in self.seen_titles):
            raise DropItem(f"duplicate: {title}")
        self.seen_titles.append(title)
        return item
