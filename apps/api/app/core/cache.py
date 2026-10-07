"""Cache: Redis when reachable, in-process LRU otherwise (same API)."""

from __future__ import annotations

import hashlib
import json
import time
from collections import OrderedDict

_mem: OrderedDict[str, tuple[float, str]] = OrderedDict()
MAX_MEM = 512


def _key(ns: str, raw: str) -> str:
    return f"{ns}:{hashlib.sha256(raw.encode()).hexdigest()[:32]}"


def cache_get(ns: str, raw: str) -> dict | None:
    # try redis
    try:
        import redis  # type: ignore
        from apps.api.app.core.config import get_settings

        r = redis.Redis.from_url(get_settings().redis_url, socket_connect_timeout=0.3)
        v = r.get(_key(ns, raw))
        if v:
            return json.loads(v)
    except Exception:
        pass
    k = _key(ns, raw)
    if k in _mem:
        exp, val = _mem[k]
        if exp > time.time():
            _mem.move_to_end(k)
            return json.loads(val)
        del _mem[k]
    return None


def cache_set(ns: str, raw: str, value: dict, ttl_s: int = 300) -> None:
    payload = json.dumps(value, default=str)
    try:
        import redis  # type: ignore
        from apps.api.app.core.config import get_settings

        r = redis.Redis.from_url(get_settings().redis_url, socket_connect_timeout=0.3)
        r.setex(_key(ns, raw), ttl_s, payload)
    except Exception:
        pass
    k = _key(ns, raw)
    _mem[k] = (time.time() + ttl_s, payload)
    _mem.move_to_end(k)
    while len(_mem) > MAX_MEM:
        _mem.popitem(last=False)
