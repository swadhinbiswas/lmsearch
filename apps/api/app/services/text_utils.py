"""Shared text helpers for search services."""

import hashlib


def text_hash(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:32]


def product_text(p: dict) -> str:
    specs = p.get("specs", {})
    spec_str = " ".join(f"{k} {v}" for k, v in specs.items())
    return (
        f"{p.get('title', '')} {p.get('brand', '')} "
        f"{p.get('category', '')} {p.get('description', '')} {spec_str}"
    )
