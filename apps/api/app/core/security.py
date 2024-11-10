"""API-key auth + per-IP rate limiting (Redis-backed, memory fallback)."""
from __future__ import annotations

import time
from collections import defaultdict

from fastapi import Header, HTTPException

from apps.api.app.core.config import get_settings

_hits: dict[str, list[float]] = defaultdict(list)
LIMIT_PER_MIN = 60


def check_rate_limit(ip: str) -> None:
    now = time.time()
    window = [t for t in _hits[ip] if now - t < 60]
    _hits[ip] = window
    if len(window) >= LIMIT_PER_MIN:
        raise HTTPException(status_code=429, detail="rate limit exceeded")
    _hits[ip].append(now)
    try:
        import redis  # type: ignore

        r = redis.Redis.from_url(get_settings().redis_url, socket_connect_timeout=0.2)
        key = f"rl:{ip}:{int(now // 60)}"
        if r.incr(key) == 1:
            r.expire(key, 61)
        if int(r.get(key) or 0) > LIMIT_PER_MIN:
            raise HTTPException(status_code=429, detail="rate limit exceeded")
    except HTTPException:
        raise
    except Exception:
        pass


def require_admin(x_api_key: str | None = Header(default=None, alias="X-API-Key")) -> None:
    if x_api_key != get_settings().admin_api_key:
        raise HTTPException(status_code=401, detail="invalid admin key")
