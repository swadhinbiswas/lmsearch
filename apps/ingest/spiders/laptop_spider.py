"""First spider: laptop listings (static demo + Playwright hook for JS pages)."""

from apps.ingest.spiders.base import PoliteSpider


class LaptopSpider(PoliteSpider):
    name = "laptops"
    allowed_domains = ["example.com"]
    start_urls = ["https://example.com/laptops"]

    def parse(self, response):
        for card in response.css(".product-card"):
            yield {
                "source": "example",
                "source_id": card.attrib.get("data-id", ""),
                "title": (card.css(".title::text").get() or "").strip(),
                "brand": (card.css(".brand::text").get() or "").strip(),
                "category": "laptop",
                "price": (card.css(".price::text").get() or "").strip(),
                "currency": "USD",
                "url": response.urljoin(card.css("a::attr(href)").get() or ""),
                "image_urls": card.css("img::attr(src)").getall(),
                "description": (card.css(".desc::text").get() or "").strip(),
            }
