"""Eval: parser spec-accuracy + Precision@10 / nDCG@10. CI fails if parser < 90%."""

from __future__ import annotations

import json
import math
import sys

sys.path.insert(0, ".")
sys.path.insert(0, "apps/api")

from apps.api.app.services.catalog import load_catalog  # noqa: E402
from apps.api.app.services.hybrid import hybrid_search  # noqa: E402
from apps.api.app.services.query_parser_bn import parse_query_multilingual  # noqa: E402


def parser_correct(item: dict, parsed: dict) -> bool:
    exp = item.get("expected", {})
    if exp.get("category") and parsed.get("category") != exp["category"]:
        return False
    must = parsed.get("must", {}) or {}
    for k in ("ram_gb_min", "refresh_hz_min", "battery_mah_min", "storage_gb_min"):
        if exp.get(k) is not None and must.get(k) != exp[k]:
            return False
    if exp.get("cpu_series"):
        have = [c.lower() for c in (must.get("cpu_series") or [])]
        if not any(e.lower() in have for e in exp["cpu_series"]):
            return False
    if exp.get("brands"):
        have = [b.lower() for b in (parsed.get("brands") or [])]
        if not any(e.lower() in have for e in exp["brands"]):
            return False
    for pk, ek in (("max", "price_max_usd"), ("min", "price_min_usd")):
        if exp.get(ek) is not None:
            got = (parsed.get("price") or {}).get(pk)
            if got is None or abs(float(got) - float(exp[ek])) > max(1.0, float(exp[ek]) * 0.05):
                return False
    return True


def relevance(item: dict, product: dict) -> int:
    rel = item.get("relevant_specs", {}) or {}
    score = 0
    specs = product.get("specs", {})
    if rel.get("ram_gb_min") is not None and (specs.get("ram_gb", 0) or 0) >= rel["ram_gb_min"]:
        score += 2
    if (
        rel.get("battery_mah_min") is not None
        and (specs.get("battery_mah", 0) or 0) >= rel["battery_mah_min"]
    ):
        score += 2
    if (
        rel.get("refresh_hz_min") is not None
        and (specs.get("refresh_hz", 0) or 0) >= rel["refresh_hz_min"]
    ):
        score += 1
    exp = item.get("expected", {})
    if exp.get("category") and product.get("category") == exp["category"]:
        score += 1
    return min(score, 3)


def dcg(gains: list[int]) -> float:
    return sum(g / math.log2(i + 2) for i, g in enumerate(gains))


def main() -> None:
    with open("ml/eval/dataset.json") as f:
        dataset = json.load(f)
    catalog = load_catalog()
    by_id = {p["id"]: p for p in catalog}
    correct = 0
    p10_sum = ndcg_sum = 0.0
    for item in dataset:
        q = item["query"]
        parsed = parse_query_multilingual(q)
        if parser_correct(item, parsed):
            correct += 1
        ranked = hybrid_search(parsed.get("semantic_query") or q, docs=catalog, limit=10)
        gains = [relevance(item, by_id[pid]) for pid, _ in ranked[:10] if pid in by_id]
        hits = sum(1 for g in gains if g > 0)
        p10_sum += hits / 10.0
        ideal = sorted(gains, reverse=True)
        ndcg_sum += (dcg(gains) / dcg(ideal)) if dcg(ideal) > 0 else 0.0
    n = len(dataset)
    acc, p10, ndcg = correct / n, p10_sum / n, ndcg_sum / n
    print(f"parser spec-accuracy: {acc:.3f} ({correct}/{n})")
    print(f"Precision@10: {p10:.3f}")
    print(f"nDCG@10: {ndcg:.3f}")
    if acc < 0.90:
        print("FAIL: parser accuracy < 90%")
        raise SystemExit(1)
    print("PASS")


if __name__ == "__main__":
    main()
