.PHONY: up down logs api web ingest seed reindex eval test lint format
up:
	docker compose up --build
down:
	docker compose down -v
logs:
	docker compose logs -f
test:
	pytest -q
lint:
	ruff check apps/api apps/ingest ml scripts
format:
	black apps/api apps/ingest ml scripts
seed:
	python scripts/seed_data.py
reindex:
	python scripts/reindex.py
eval:
	python ml/evaluate.py
build:
	docker compose build
config:
	docker compose config
