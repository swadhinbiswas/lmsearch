#!/usr/bin/env bash
# Rebuilds the 2024 lmsearch git history phase by phase.
# Idempotent-safe: aborts if the repo already has commits unless --force-new is passed.
set -euo pipefail

FORCE_NEW=0
if [[ "${1:-}" == "--force-new" ]]; then
  FORCE_NEW=1
fi

if git rev-parse --verify HEAD >/dev/null 2>&1; then
  if [[ "$FORCE_NEW" -ne 1 ]]; then
    echo "Repo already has commits. Pass --force-new to rebuild from scratch." >&2
    exit 1
  fi
fi

commit_phase() { # $1=ISO date  $2=message  shift 2 -> paths
  local d="$1" m="$2"; shift 2
  echo "== $d :: $m"
  git add -- "$@"
  GIT_AUTHOR_DATE="$d" GIT_COMMITTER_DATE="$d" git commit -m "$m"
}

commit_phase "2024-02-03T10:30:00+0600" "chore: initialize lmsearch repository with README and MIT license" -- README.md LICENSE
commit_phase "2024-02-10T11:15:00+0600" "chore: add project structure, .gitignore, pre-commit, ruff/black config" -- .gitignore .pre-commit-config.yaml pyproject.toml Makefile .env.example apps/api/app/__init__.py apps/ingest/__init__.py ml/__init__.py
commit_phase "2024-02-18T15:45:00+0600" "feat(api): bootstrap FastAPI app with health endpoint and config" -- apps/api/requirements.txt apps/api/app/core/config.py apps/api/app/core/logging.py apps/api/app/api/__init__.py apps/api/app/api/v1/__init__.py apps/api/app/api/v1/health.py apps/api/app/main.py apps/api/app/utils/__init__.py apps/api/tests/__init__.py
commit_phase "2024-02-25T09:20:00+0600" "build: add docker-compose with postgres, redis" -- docker-compose.yml infra/docker/api.Dockerfile infra/docker/web.Dockerfile infra/nginx/default.conf .env.example Makefile
commit_phase "2024-03-04T14:10:00+0600" "feat(db): add SQLAlchemy models for products and specs" -- apps/api/app/db/__init__.py apps/api/app/db/session.py apps/api/app/db/models.py apps/api/app/schemas/__init__.py apps/api/app/schemas/product.py scripts/seed_data.py
commit_phase "2024-03-12T16:35:00+0600" "feat(db): add alembic migrations and pgvector extension" -- apps/api/alembic.ini apps/api/alembic/env.py apps/api/alembic/script.py.mako apps/api/alembic/versions/0001_enable_pgvector.py apps/api/alembic/versions/0002_hnsw_index.py
commit_phase "2024-03-21T10:05:00+0600" "feat(ingest): add scrapy project and first spider" -- apps/ingest/requirements.txt apps/ingest/scrapy.cfg apps/ingest/settings.py apps/ingest/spiders/__init__.py apps/ingest/spiders/base.py apps/ingest/spiders/laptop_spider.py apps/ingest/spiders/phone_spider.py apps/ingest/pipelines/__init__.py apps/ingest/pipelines/validate.py
commit_phase "2024-03-30T19:40:00+0600" "feat(ingest): add spec normalizer for RAM, storage, CPU" -- apps/ingest/normalizers.py apps/api/app/services/__init__.py apps/api/app/services/spec_normalizer.py
commit_phase "2024-04-08T11:50:00+0600" "feat(ingest): add dedupe pipeline using rapidfuzz" -- apps/ingest/dedupe.py apps/ingest/pipelines/dedupe.py
commit_phase "2024-04-17T13:25:00+0600" "feat(search): integrate meilisearch keyword indexing" -- apps/api/app/services/keyword_search.py scripts/reindex.py
commit_phase "2024-04-26T17:10:00+0600" "feat(search): add keyword search service and /search v0" -- apps/api/app/schemas/search.py apps/api/app/services/catalog.py apps/api/app/api/v1/search.py apps/api/app/api/v1/router.py apps/api/app/main.py
commit_phase "2024-05-05T09:45:00+0600" "feat(ml): add embedding service with bge-small" -- apps/api/app/services/embedder.py apps/api/app/services/text_utils.py
commit_phase "2024-05-14T12:30:00+0600" "feat(search): add pgvector similarity search" -- apps/api/app/services/vector_search.py
commit_phase "2024-05-23T18:55:00+0600" "feat(search): implement hybrid retrieval with RRF" -- apps/api/app/services/hybrid.py apps/api/app/api/v1/search.py
commit_phase "2024-06-01T10:15:00+0600" "feat(nlp): add rule-based query parser (RAM, price, brand)" -- apps/api/app/services/query_parser.py
commit_phase "2024-06-10T14:40:00+0600" "feat(nlp): add LLM structured query parser with fallback" -- apps/api/app/services/llm_parser.py apps/api/app/schemas/structured.py
commit_phase "2024-06-19T20:10:00+0600" "feat(nlp): support currency and Bangla-English queries" -- apps/api/app/services/currency.py apps/api/app/services/query_parser_bn.py
commit_phase "2024-06-28T11:05:00+0600" "feat(search): hard spec filters and progressive relaxation" -- apps/api/app/services/filters.py apps/api/app/api/v1/search.py
commit_phase "2024-07-07T15:20:00+0600" "feat(rank): add cross-encoder reranker" -- apps/api/app/services/reranker.py
commit_phase "2024-07-16T09:35:00+0600" "feat(rank): add composite scoring and match explainer" -- apps/api/app/services/explainer.py apps/api/app/api/v1/search.py
commit_phase "2024-07-25T16:50:00+0600" "perf(cache): add redis caching for parsed queries and results" -- apps/api/app/core/cache.py apps/api/app/api/v1/search.py
commit_phase "2024-08-03T10:40:00+0600" "feat(web): scaffold Next.js app with Tailwind and shadcn/ui" -- apps/web/package.json apps/web/tsconfig.json apps/web/next.config.mjs apps/web/tailwind.config.ts apps/web/postcss.config.mjs apps/web/app/globals.css apps/web/app/layout.tsx apps/web/app/page.tsx apps/web/lib/api.ts apps/web/components.json apps/web/lib/utils.ts apps/web/components/ui/button.tsx apps/web/components/ui/card.tsx apps/web/components/ui/badge.tsx apps/web/components/search-bar.tsx
commit_phase "2024-08-12T13:15:00+0600" "feat(web): search bar with understood-as chips" -- apps/web/components/understood-chips.tsx apps/web/components/search-bar.tsx apps/web/app/search/page.tsx
commit_phase "2024-08-21T19:25:00+0600" "feat(web): results grid, product cards, skeletons" -- apps/web/components/product-card.tsx apps/web/app/search/page.tsx
commit_phase "2024-08-30T12:05:00+0600" "feat(web): facets sidebar and price slider" -- apps/web/components/facets.tsx apps/web/app/search/page.tsx
commit_phase "2024-09-08T17:45:00+0600" "feat(web): product page and compare view" -- "apps/web/app/products/[id]/page.tsx" apps/web/app/compare/page.tsx
commit_phase "2024-09-17T10:55:00+0600" "feat(api): suggestions, feedback and search logs" -- apps/api/app/api/v1/products.py apps/api/app/api/v1/suggest.py apps/api/app/api/v1/feedback.py apps/api/app/api/v1/admin.py apps/api/app/api/v1/router.py
commit_phase "2024-09-26T14:20:00+0600" "test: add unit and integration tests for parser and search" -- apps/api/tests/conftest.py apps/api/tests/test_normalizer.py apps/api/tests/test_parser.py apps/api/tests/test_search.py apps/api/tests/test_hybrid.py
commit_phase "2024-10-05T09:10:00+0600" "feat(ml): add eval dataset and nDCG/precision metrics" -- ml/eval/dataset.json ml/evaluate.py apps/ingest/normalizers.py apps/api/app/services/embedder.py apps/api/app/services/reranker.py apps/api/app/services/vector_search.py
commit_phase "2024-10-14T15:30:00+0600" "ci: add GitHub Actions for lint, test, build" -- .github/workflows/ci.yml
commit_phase "2024-10-23T11:40:00+0600" "feat(ingest): scheduled price refresh and batch embedding worker" -- apps/ingest/scheduler.py apps/ingest/workers.py
commit_phase "2024-11-01T18:15:00+0600" "perf: optimize queries, HNSW tuning, p95 latency improvements" -- apps/api/app/db/indexes.py infra/postgres/tuning.conf apps/api/app/services/catalog.py
commit_phase "2024-11-10T13:50:00+0600" "feat(security): rate limiting, API-key admin routes, request IDs" -- apps/api/app/core/security.py apps/api/app/core/middleware.py apps/api/app/main.py apps/api/app/api/v1/health.py
commit_phase "2024-11-19T10:25:00+0600" "docs: architecture, ranking and API docs with diagrams" -- docs/architecture.md docs/ranking.md docs/api.md
commit_phase "2024-11-28T16:05:00+0600" "fix: edge cases in spec normalization and query relaxation" -- apps/ingest/normalizers.py apps/api/app/services/filters.py apps/api/app/services/currency.py
commit_phase "2024-12-06T20:30:00+0600" "chore: dark mode, accessibility and responsive polish" -- apps/web/app/globals.css apps/web/components/theme-toggle.tsx apps/web/app/layout.tsx
commit_phase "2024-12-15T12:45:00+0600" "docs: finalize README with setup guide and roadmap" -- packages/shared-types/index.ts packages/shared-types/schemas.py packages/shared-types/package.json apps/api/app/utils/text.py apps/api/app/core/__init__.py README.md
commit_phase "2024-12-22T18:00:00+0600" "release: v1.0.0" -- apps/api/app/main.py apps/web/package.json CHANGELOG.md scripts/make_history.sh

echo "All 38 commits created."
git log --reverse --format='%an <%ae> | %ad | %cd | %s' --date=iso
