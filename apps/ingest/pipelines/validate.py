"""Drop items missing title/price; coerce price to float."""


def clean_item(item: dict) -> dict | None:
    title = (item.get("title") or "").strip()
    if not title:
        return None
    price = item.get("price", 0)
    if isinstance(price, str):
        digits = "".join(c for c in price if c.isdigit() or c == ".")
        try:
            price = float(digits) if digits else 0.0
        except ValueError:
            price = 0.0
    item["title"] = title
    item["price"] = float(price or 0)
    return item
