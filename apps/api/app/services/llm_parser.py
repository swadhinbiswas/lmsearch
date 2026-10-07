"""LLM structured query parser with pluggable providers + rule fallback.

Providers: openai (gpt-4o-mini), ollama (llama3). JSON-schema output, 2s timeout,
then deterministic rule parser. Results cached by normalized query upstream.
"""

from __future__ import annotations

import json
import re
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FuturesTimeout

from apps.api.app.services import query_parser as rule

SYSTEM_PROMPT = (
    "Extract a product search intent as JSON with keys: category (laptop|phone|null), "
    "brands[], must{ram_gb_min, storage_gb_min, cpu_series[], refresh_hz_min, battery_mah_min}, "
    "price{min,max,currency}, use_case[], soft_preferences[], exclude[], semantic_query. "
    "must=hard filters, soft_preferences=ranking boosts. Return ONLY JSON."
)


class LLMProvider:
    name = "base"

    def complete_json(self, query: str, timeout_s: float = 2.0) -> dict | None:
        raise NotImplementedError


class OpenAIProvider(LLMProvider):
    name = "openai"

    def complete_json(self, query: str, timeout_s: float = 2.0) -> dict | None:
        try:
            from apps.api.app.core.config import get_settings
            from openai import OpenAI  # type: ignore

            s = get_settings()
            if not s.openai_api_key:
                return None
            client = OpenAI(api_key=s.openai_api_key, timeout=timeout_s)

            def _call():
                return client.chat.completions.create(
                    model=s.llm_model,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": query},
                    ],
                    response_format={"type": "json_object"},
                    max_tokens=400,
                )

            with ThreadPoolExecutor(max_workers=1) as ex:
                fut = ex.submit(_call)
                resp = fut.result(timeout=timeout_s)
            text = resp.choices[0].message.content or "{}"
            return json.loads(text)
        except (FuturesTimeout, Exception):
            return None


class OllamaProvider(LLMProvider):
    name = "ollama"

    def complete_json(self, query: str, timeout_s: float = 2.0) -> dict | None:
        try:
            import httpx

            def _call():
                return httpx.post(
                    "http://localhost:11434/api/chat",
                    json={
                        "model": "llama3",
                        "messages": [
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": query},
                        ],
                        "stream": False,
                        "format": "json",
                    },
                    timeout=timeout_s,
                )

            with ThreadPoolExecutor(max_workers=1) as ex:
                r = ex.submit(_call).result(timeout=timeout_s)
            if r.status_code == 200:
                return json.loads(r.json()["message"]["content"])
            return None
        except (FuturesTimeout, Exception):
            return None


def get_provider(name: str) -> LLMProvider:
    if name == "ollama":
        return OllamaProvider()
    return OpenAIProvider()


def repair_llm_output(data: dict, raw_query: str) -> dict:
    """Validate + repair LLM JSON with the rule layer (regex wins on conflicts)."""
    base = rule.parse_query_rule(raw_query)
    if not isinstance(data, dict):
        return base
    out = dict(base)
    for k in ("category", "brands", "use_case", "soft_preferences", "exclude", "semantic_query"):
        if k in data and data[k] not in (None, [], ""):
            out[k] = data[k]
    # merge must: rule minimums dominate (deterministic repair e.g. "32gb" -> 32)
    must = dict(base.get("must", {}))
    if isinstance(data.get("must"), dict):
        for kk, vv in data["must"].items():
            if kk not in must and vv is not None:
                must[kk] = vv
    out["must"] = must
    if data.get("price"):
        out["price"] = data["price"] if isinstance(data["price"], dict) else base["price"]
    out.setdefault("semantic_query", raw_query.strip())
    return out


def normalize_query(q: str) -> str:
    q = (q or "").strip().lower()
    q = re.sub(r"\s+", " ", q)
    return q


def parse_query(query: str, timeout_s: float = 2.0) -> dict:
    from apps.api.app.core.config import get_settings

    s = get_settings()
    provider = get_provider(s.llm_provider)
    llm_data = provider.complete_json(query, timeout_s=timeout_s)
    if llm_data:
        try:
            return repair_llm_output(llm_data, query)
        except Exception:
            pass
    return rule.parse_query_rule(query)
