"""APScheduler price-refresh + embedding jobs (hourly prices, nightly vectors)."""

from __future__ import annotations

import logging

log = logging.getLogger(__name__)


def refresh_prices(batch_size: int = 200) -> int:
    log.info("refreshing prices batch=%s", batch_size)
    # Production: re-scrape top sellers and update products.price/updated_at.
    # Seed mode: no-op that reports the batch size for observability.
    return batch_size


def start_scheduler() -> None:
    try:
        from apscheduler.schedulers.blocking import BlockingScheduler  # type: ignore
    except Exception:
        log.warning("apscheduler not installed; scheduler disabled")
        return
    sched = BlockingScheduler()
    sched.add_job(refresh_prices, "interval", hours=1, id="price-refresh")
    sched.add_job(run_embedding_batch, "cron", hour=2, id="embedding-batch")
    log.info("scheduler started")
    sched.start()


def run_embedding_batch(limit: int = 500) -> int:
    from apps.api.app.services import vector_search as vs
    from apps.api.app.services.catalog import load_catalog

    docs = load_catalog()[:limit]
    return vs.index_vectors(docs)
