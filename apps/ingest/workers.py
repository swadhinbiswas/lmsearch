"""Batch embedding worker (queue-less cron entrypoint)."""

from apps.ingest.scheduler import run_embedding_batch


def main(limit: int = 500) -> None:
    n = run_embedding_batch(limit)
    print(f"embedded {n} products")


if __name__ == "__main__":
    main()
