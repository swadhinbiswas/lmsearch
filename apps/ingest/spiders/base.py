"""Polite base spider with rate limiting."""

import scrapy


class PoliteSpider(scrapy.Spider):
    custom_settings = {"DOWNLOAD_DELAY": 1.0, "ROBOTSTXT_OBEY": True}

    def polite_request(self, url: str, callback):
        return scrapy.Request(url, callback=callback, errback=self.on_error)

    def on_error(self, failure):
        self.logger.warning("request failed: %s", failure)
