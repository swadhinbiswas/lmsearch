"""Scrapy settings: polite crawling, robots.txt, rate limits."""

BOT_NAME = "lmsearch"
SPIDER_MODULES = ["apps.ingest.spiders"]
ROBOTSTXT_OBEY = True
DOWNLOAD_DELAY = 1.0
CONCURRENT_REQUESTS = 8
CONCURRENT_REQUESTS_PER_DOMAIN = 2
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1.0
USER_AGENT = "lmsearch-bot/1.0 (+https://example.com/bot)"
ITEM_PIPELINES = {"apps.ingest.pipelines.DedupePipeline": 300}
FEED_EXPORT_ENCODING = "utf-8"
