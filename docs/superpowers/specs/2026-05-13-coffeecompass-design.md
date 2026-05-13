# CoffeeCompass — 5-Week Design Spec

**Status:** Draft v1 (awaiting user review)
**Date:** 2026-05-13
**Scope:** End-to-end design for a 5-week solo build of a RAG-powered coffee shop finder around USC / LA. Each week is a sub-project with its own implementation plan (created later via the `writing-plans` skill).

---

## 1. Project Overview

CoffeeCompass is a natural-language coffee shop finder for the USC / LA area. A user asks something like "quiet café with outlets, good for studying near campus" and the system returns the top 3-5 cafes with rationale.

**Technical themes to demonstrate (recruiter-readable):**

- RAG: pgvector + embeddings + structured-filter hybrid retrieval
- LLM-as-extractor: turn unstructured reviews into structured attributes
- Eval-driven development: RAGAS golden set, prompt versioning, measurable iteration
- Agentic planning: LangChain ReAct agent with tool calling and memory
- Productionization: Docker, AWS EC2, Vercel, observability, latency budget

**Out of scope (explicitly):**

- User accounts / auth (single-user demo)
- Mobile apps (web only)
- Real-time data freshness (one-shot ingestion; manual refresh OK)
- Payment, booking, social features

---

## 2. Locked-In Architectural Decisions

All decisions below were confirmed during brainstorming and are the source of truth for the per-week plans.

| ID | Decision | Choice | Rationale |
|----|----------|--------|-----------|
| Q1 | Query parsing pipeline | **B: Backend LLM slot extraction** — natural-language query in, `gpt-4o-mini` extracts `{semantic_query, filters}`, then embed + pgvector + SQL filter | Single-string UX, RAG-native, easy to extend in Week 3 with the agent |
| Q2 | Postgres + pgvector deployment | **Docker Compose with `pgvector/pgvector:pg16` image** | Reproducible, isolated, identical image works in deployment |
| Q3 | Google + Yelp data merge | **Google primary, Yelp reconciled by `(name, lat, lng)` fuzzy match, stored as one `cafes` row** | DB matches the "100 cafes" goal; queries hit one table |
| Q4 | WiFi / outlet / ambience tags | **LLM extraction from reviews (`gpt-4o-mini`)** — same call also produces the ambience_text used for embedding | The standard RAG-builder skill; tags + ambience_text in one call |
| Q5 | LLM slot extractor output schema (Q1's B) | **Minimal: `semantic_query` + `{has_outlet, open_now, price_max}`**; other Q4-derived tags (noise_level, good_for_studying, has_wifi) go into `ambience_text` and are matched via vector retrieval, not SQL | Avoids fighting the vector retriever; SQL filters stay narrow and reliable |
| C2 | Repository layout | **`backend/` + `frontend/` + `infra/` + `docs/`** top-level | Reserves slots for Week 3 (Next.js) and Week 5 (deploy artifacts) on Day 1 |
| C3 | Package managers | **`uv` (Python), `pnpm` (Node)** | Fast lockfiles; both supported by mainstream deploy targets |
| C4 | Week 3 agent LLM | **`gpt-4o-mini` default, env switch for `gpt-4o`** | Cheap, ReAct-capable; swap to GPT-4o for the demo recording if needed |
| C5 | Zep memory deployment | **Zep Cloud free tier** | No extra container; free tier sufficient for personal demo |
| C6 | RAGAS evaluator LLM | **`gpt-4o-mini`** | Eval cost across 30 queries × 4 metrics × 4 prompt versions is a few dollars |
| C7 | Week 5 backend host | **AWS EC2 t3.small + nginx + systemd** | Spec requirement; recruiter-visible; deploy artifacts also runnable locally via Compose |

---

## 3. Prerequisites — Action Required Before Week 1

You said you have **none** of the API keys yet. Here is the application path. **Start C1.a and C1.b in parallel today** because Yelp can take 1-3 business days.

### C1.a Google Places API

1. Go to <https://console.cloud.google.com> and create a new project, e.g. `coffeecompass-dev`.
2. Enable APIs & Services → enable **Places API (New)**. (Use the "New" version, not the legacy one.)
3. Billing → link a credit card. Google gives a **$200 monthly credit** for Maps Platform, more than enough for 100 cafes.
4. APIs & Services → Credentials → Create API key. Restrict it to the Places API.
5. Save the key as `GOOGLE_PLACES_API_KEY` in `backend/.env` (file added later; never commit it).

**Expected cost for Week 1:** $0 (under $200 free credit).

### C1.b Yelp Fusion API

1. Sign up at <https://www.yelp.com/developers>.
2. Manage App → Create New App → fill in app name and description (one paragraph).
3. Yelp may approve instantly or take **1-3 business days**. There is nothing to do but wait.
4. Once approved, copy the API key as `YELP_API_KEY`.

**Expected cost for Week 1:** $0 (free tier: 5,000 calls/day).

### C1.c OpenAI API

1. Sign up at <https://platform.openai.com>.
2. Billing → add a payment method → top up **$10** (lasts the whole 5-week project).
3. API keys → create a new secret key. Save as `OPENAI_API_KEY`.

**Expected cost for entire 5 weeks:** $5-10 (see budget in §10).

### C1.d Docker Desktop

Install <https://www.docker.com/products/docker-desktop> for macOS. Verify with `docker --version` and `docker compose version`.

### Later-week prerequisites (no action this week)

- **Zep Cloud** (Week 3): <https://www.getzep.com> — free tier signup before Week 3.
- **AWS account** (Week 5): free-tier signup; t3.small ≈ $15/month, plan to keep it on only 3-5 days.
- **Vercel account** (Week 5): hobby tier free.
- **Medium account** (Week 5).

---

## 4. Repository Layout

```text
CoffeeCompass/
├── backend/
│   ├── pyproject.toml              # uv-managed, Python 3.12
│   ├── uv.lock
│   ├── .env.example
│   ├── alembic.ini
│   ├── alembic/
│   │   └── versions/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI entry
│   │   ├── config.py               # pydantic-settings
│   │   ├── db.py                   # async SQLAlchemy engine
│   │   ├── models.py               # ORM models
│   │   ├── schemas.py              # pydantic request/response
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── search.py           # /search endpoint (Week 1)
│   │   │   └── agent.py            # /agent/chat endpoint (Week 3)
│   │   ├── ingestion/
│   │   │   ├── google_places.py
│   │   │   ├── yelp.py
│   │   │   ├── reconcile.py        # merge logic
│   │   │   ├── reviews.py          # pull + LLM extraction
│   │   │   └── pipeline.py         # orchestrator CLI
│   │   ├── search/
│   │   │   ├── slot_extractor.py   # Q1.B LLM parser
│   │   │   ├── embedder.py         # OpenAI embedding wrapper
│   │   │   └── retriever.py        # pgvector + SQL filter
│   │   ├── agent/                  # Week 3
│   │   │   ├── tools.py
│   │   │   ├── react_agent.py
│   │   │   └── memory.py           # Zep wrapper
│   │   └── eval/                   # Week 2 / 4
│   │       ├── golden_set.json
│   │       ├── ragas_runner.py
│   │       └── prompt_versions/
│   └── tests/
│       ├── unit/
│       └── integration/
├── frontend/                       # Week 3
│   ├── package.json                # pnpm
│   ├── next.config.mjs
│   ├── app/
│   │   ├── page.tsx
│   │   └── api/
│   └── components/
├── infra/
│   ├── docker-compose.yml          # postgres + backend (Week 1), + frontend (Week 5)
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend         # Week 5
│   └── ec2/
│       ├── nginx.conf
│       └── deploy.sh
├── docs/
│   ├── superpowers/
│   │   ├── specs/
│   │   │   └── 2026-05-13-coffeecompass-design.md   # this file
│   │   └── plans/
│   │       └── 2026-05-13-week1-plan.md             # written next
│   └── eval-results/               # Week 4 metric dumps
└── README.md
```

---

## 5. Data Model

### 5.1 `cafes` (primary table)

```sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE cafes (
    id              SERIAL PRIMARY KEY,
    google_place_id TEXT UNIQUE NOT NULL,
    yelp_business_id TEXT UNIQUE,
    name            TEXT NOT NULL,
    address         TEXT NOT NULL,
    lat             DOUBLE PRECISION NOT NULL,
    lng             DOUBLE PRECISION NOT NULL,
    rating          REAL,                 -- preferred: Yelp; fallback: Google
    review_count    INT,
    price_level     SMALLINT,             -- 1..4 (mapped from Yelp $/$$/$$$/$$$$)
    categories      TEXT[],
    opening_hours   JSONB,                -- structured, see §5.3
    -- LLM-extracted attributes (Q4)
    has_wifi        BOOLEAN,
    has_outlet      BOOLEAN,
    noise_level     TEXT,                 -- 'quiet' | 'moderate' | 'lively' | NULL
    good_for_studying BOOLEAN,
    -- RAG fields
    ambience_text   TEXT NOT NULL,        -- LLM-generated natural-language summary
    embedding       VECTOR(1536),         -- text-embedding-3-small
    -- metadata
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX cafes_embedding_idx ON cafes
    USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

CREATE INDEX cafes_has_outlet_idx ON cafes (has_outlet);
CREATE INDEX cafes_price_level_idx ON cafes (price_level);
```

### 5.2 `prompt_versions` (Week 2)

Used for the "JSON prompt versioning" feature.

```sql
CREATE TABLE prompt_versions (
    id              SERIAL PRIMARY KEY,
    name            TEXT NOT NULL,        -- e.g. 'slot_extractor', 'review_tagger'
    version         INT NOT NULL,
    body            TEXT NOT NULL,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (name, version)
);
```

A backup JSON file `backend/app/eval/prompt_versions/<name>.json` mirrors this table for git-tracked history.

### 5.3 `opening_hours` JSONB shape

Stored verbatim from Google Places `regularOpeningHours.periods`:

```json
{
  "periods": [
    { "open": { "day": 1, "hour": 7, "minute": 0 },
      "close": { "day": 1, "hour": 20, "minute": 0 } }
  ],
  "timezone": "America/Los_Angeles"
}
```

`open_now` is computed at query time by evaluating the current LA local time against `periods`. No cron job needed.

### 5.4 Eval tables (Week 2)

Golden set lives as a versioned file `backend/app/eval/golden_set.json` (30 entries), each:

```json
{
  "id": "g001",
  "query": "quiet place to read near USC",
  "expected_cafe_ids": [12, 47, 89],
  "tags": ["quiet", "study"]
}
```

RAGAS run results are dumped to `docs/eval-results/YYYY-MM-DD-vX.json`.

---

## 6. Per-Week Design

### Week 1 — Data Ingestion + RAG Core

**Deliverables:**

- `cafes` table populated with ~100 USC-area shops (within 3 mi of USC main campus).
- One-shot ingestion CLI: `uv run python -m app.ingestion.pipeline --radius 3mi --limit 100`.
- `/search` endpoint returning Top 5 cafes by hybrid retrieval.

**Ingestion pipeline (one CLI, 4 phases):**

1. **Google Places fetch** — Nearby Search around USC `(34.0224, -118.2851)`, radius up to 5 km, paginated, filter by `type=cafe`, stop at 100 unique `google_place_id`s. For each, fetch Place Details to get hours, rating, lat/lng, address, categories.
2. **Yelp reconcile** — For each Google record, call Yelp Business Search with `term=name, latitude, longitude, radius=80m`. Match if name Jaro-Winkler similarity > 0.8 AND distance < 50m. Merge fields: Yelp `rating` overrides Google, Yelp `price` is the source of `price_level`, save `yelp_business_id`.
3. **Review pull (minimal in Week 1)** — Yelp `/businesses/{id}/reviews` returns up to 3 latest reviews per shop (Yelp free tier limit). Fetch all available. Cache raw JSON to `backend/data/reviews_raw/<yelp_id>.json` so Week 2 can re-process without re-paying API.
4. **LLM extraction + embedding** — One `gpt-4o-mini` call per cafe (input: name, categories, available reviews) produces a structured JSON:

   ```json
   {
     "has_wifi": true,
     "has_outlet": null,
     "noise_level": "quiet",
     "good_for_studying": true,
     "ambience_text": "A small specialty café two blocks from campus, prized by students for its calm atmosphere, latte art, and abundant table space..."
   }
   ```

   Then embed `ambience_text` with `text-embedding-3-small` and `UPSERT` the cafe row.

All four phases are idempotent (UPSERT on `google_place_id`).

**`/search` endpoint contract:**

```text
POST /search
Content-Type: application/json

Request:
{
  "query": "quiet place to study with outlets",
  "top_k": 5            // optional, default 5
}

Response 200:
{
  "parsed": {
    "semantic_query": "quiet place to study",
    "filters": { "has_outlet": true, "open_now": null, "price_max": null }
  },
  "results": [
    {
      "id": 12,
      "name": "Bricks & Scones",
      "address": "...",
      "rating": 4.6,
      "price_level": 2,
      "has_outlet": true,
      "has_wifi": true,
      "noise_level": "quiet",
      "good_for_studying": true,
      "open_now": true,
      "similarity": 0.81,
      "ambience_text": "..."
    }
  ]
}
```

(`distance_m` deferred to Week 3 when the frontend introduces a "user location" reference point. Adding it now would require an arbitrary anchor.)

**Retrieval algorithm:**

1. Call `slot_extractor(query)` → `gpt-4o-mini` with a function-calling JSON schema → `parsed`.
2. Embed `parsed.semantic_query` with `text-embedding-3-small`.
3. SQL: `SELECT ... FROM cafes WHERE (filters applied) ORDER BY embedding <=> :q LIMIT 50` (candidate set).
4. Compute `open_now` in Python from `opening_hours` if filter requires it.
5. Return top `top_k`.

**Verification path (Postman):**

- `POST /search { "query": "安静适合读书有插座" }` returns 5 cafes, all with `has_outlet=true`, sorted by relevance.
- `POST /search { "query": "cheap latte close to campus", "top_k": 3 }` returns 3 cafes with `price_level <= 2`.

---

### Week 2 — Review Analysis + Eval Baseline

**Deliverables:**

- Full review pull, **realistic cap: 8 reviews per cafe** (Yelp Fusion `/businesses/{id}/reviews` returns 3 snippets max; Google Place Details returns up to 5). The original "50 per cafe" goal in the user's Week 2 spec is not achievable from public Yelp + Google APIs without scraping (which we will not do). This is documented honestly in the blog post; the LLM extractor is tuned to extract reliable tags from ~8 reviews.
- Re-run the LLM extractor with the full review corpus → richer `ambience_text` + sharper tags.
- 30-entry golden set in `backend/app/eval/golden_set.json` (you hand-author the queries; you label expected cafe IDs after Week 1 data is in).
- RAGAS baseline run committed to `docs/eval-results/2026-05-20-v1.json`. Metrics: `context_precision`, `faithfulness`, `answer_relevancy`.
- JSON prompt-versioning system: each prompt edit writes a new file under `backend/app/eval/prompt_versions/<name>/v<n>.json` and a row in `prompt_versions` table.

**Key design choice:** the LLM extractor is rewritten as `review_tagger_v2` with a longer prompt that handles the full review corpus. `slot_extractor` stays untouched in Week 2.

**Eval methodology:**

For each golden query, the retriever returns its top 5. RAGAS computes:

- `context_precision`: fraction of returned cafes that overlap `expected_cafe_ids`.
- `answer_relevancy`: semantic similarity between the generated `ambience_text` of returned cafes and the query.
- `faithfulness`: degree to which `ambience_text` is supported by the underlying reviews (uses original reviews as the context corpus).

This week we just establish the baseline number; iteration happens in Week 4.

---

### Week 3 — Planning Agent + Multi-turn UI

**Deliverables:**

- LangChain ReAct agent in `backend/app/agent/react_agent.py` exposed at `POST /agent/chat`.
- Three tools, all thin wrappers over Week 1 code:
  - `search_shops(query, has_outlet?, price_max?, top_k)` → calls the same retriever.
  - `filter_by_hours(cafe_ids, day_of_week, time)` → re-checks `opening_hours`.
  - `get_shop_detail(cafe_id)` → returns the full row.
- Multi-turn: agent endpoint accepts `session_id`; previous turns and tool outputs become the LLM's scratchpad.
- Zep Memory: per `user_id`, the agent's last 10 turns and a "preferences" summary (e.g. "prefers quiet, $$, near downtown") are stored in Zep Cloud and prepended to the system prompt on each new chat.
- Next.js front-end:
  - Chat panel (streaming via Server-Sent Events from `/agent/chat`).
  - Map panel using a TBD provider (decided at Week 3 brainstorm; candidates: Mapbox GL JS, Google Maps JS API, MapLibre + OSM tiles). Recommended cafes appear as pins; clicking a pin highlights the chat bubble.
  - Agent reasoning streamed: each ReAct `Thought` / `Action` / `Observation` step is rendered as a collapsible sub-block.

**`/agent/chat` contract:**

```text
POST /agent/chat   (Server-Sent Events)
{
  "session_id": "uuid",
  "user_id": "demo-user",
  "message": "找下周五约会用的咖啡店，停车方便不太吵"
}

Stream:
event: thought
data: "User wants a date-night cafe with parking and low noise..."

event: action
data: { "tool": "search_shops", "args": { "query": "...", "price_max": 3 } }

event: observation
data: { "results": [...] }

event: final
data: { "recommendations": [...], "rationale": "..." }
```

**Frontend pages:**

- `/` — chat + map (the demo flow).
- `/cafe/:id` — detail card (used by `get_shop_detail` deep-links).

---

### Week 4 — Eval Iteration + Latency Optimization

**Deliverables:**

- Four prompt iterations on `review_tagger` and `slot_extractor`, each with a RAGAS run. Target: `context_precision ≥ 0.84` (start point honestly recorded from Week 2 baseline).
- Embedding comparison: dump a second `embedding_large` column populated with `text-embedding-3-large`; rerun the golden set and compare. Record cost delta.
- Latency tracking middleware: log `embed_ms`, `pgvector_ms`, `llm_ms`, `total_ms` to a `request_latency` table. Run a 200-request load test (locust or k6), report p50/p95.
- Optimization passes (apply one at a time, measure between):
  - Replace `ivfflat` with `hnsw` index — measure recall and latency.
  - Cache common `slot_extractor` outputs for 10 minutes (in-process LRU).
  - Batch embedding calls in the agent's `search_shops` tool when it's used twice in one turn.
- Final eval doc: `docs/eval-results/2026-06-03-final.md` with all numbers, charts (matplotlib script in `backend/scripts/plot_eval.py`), and one paragraph of recruiter-readable summary.

**Honesty rule:** every number in the final doc is auto-generated from a script that reads `docs/eval-results/*.json`. No hand-typed metrics.

---

### Week 5 — Deploy + Demo + Blog

**Deliverables:**

- Production `docker-compose.prod.yml` (no bind mounts, env from EC2 instance metadata or `.env.prod`).
- Multi-stage `Dockerfile.backend` (final image ~150 MB on `python:3.12-slim`).
- EC2 t3.small in `us-west-2`. Setup script `infra/ec2/deploy.sh` clones, sets up nginx reverse proxy, registers systemd service.
- Vercel deployment of `frontend/`, points `NEXT_PUBLIC_API_BASE` at the EC2 public DNS (HTTPS via nginx + Let's Encrypt).
- S3 bucket for the demo video and screenshots (`coffeecompass-assets`).
- **2-minute demo video** script in §11.
- Medium blog draft `docs/blog/draft-coffeecompass.md` — I write the structure and prose, you fill in real metric numbers and your reflections.
- Public README with badges, demo GIF, architecture diagram, and live URL.

---

## 7. Cross-Cutting Concerns

### 7.1 Configuration & Secrets

- All secrets in `backend/.env`, never committed. `.env.example` lists every required var.
- Pydantic `Settings` class loads them on startup with `SettingsConfigDict(env_file=".env")`.
- For EC2: `.env.prod` placed via `scp` once; permissions `chmod 600`.

### 7.2 Testing Strategy

- **Unit tests** (pytest) for: slot extractor JSON shape, opening-hours `open_now` logic, retriever SQL builder, Yelp reconcile fuzzy matcher.
- **Integration tests**: spin up a test container via `testcontainers-python` with pgvector, seed 3 cafes, hit `/search`.
- **Golden-set eval** (Week 2+): the eval IS the integration test for retrieval quality.
- **No API mocking gymnastics** — external APIs are mocked at the `httpx.AsyncClient` level using `respx`.

### 7.3 Logging & Observability

- `structlog` JSON logs to stdout.
- Every `/search` and `/agent/chat` request gets a `request_id`; latency components logged.
- Week 4 adds `request_latency` table (write-behind, async). Optional `/metrics` Prometheus endpoint — out of scope unless time permits.

### 7.4 Cost Ceiling

Total budget across 5 weeks: **≤ $30 hard cap**.

| Bucket | Estimate | Notes |
|--------|----------|-------|
| Google Places | $0 | within $200/mo credit |
| Yelp Fusion | $0 | free tier |
| OpenAI (Week 1 ingest) | $0.50 | 100 cafes × few hundred tokens |
| OpenAI (Week 2 reviews) | $3-5 | 100 × 50 reviews × one extract call |
| OpenAI (Week 2 RAGAS baseline) | $1-2 | 30 queries × 3 metrics |
| OpenAI (Week 4 iteration) | $5-10 | 4 prompt versions × full eval |
| OpenAI (`text-embedding-3-large` compare) | $0.02 | embeddings are cheap |
| AWS EC2 (Week 5) | $5-15 | t3.small, 3-7 days |
| Vercel | $0 | hobby tier |
| Zep Cloud | $0 | free tier |
| **Total** | **$15-32** | |

### 7.5 Performance Targets (for Week 4)

- `/search` p95 ≤ 250 ms (excluding cold OpenAI calls)
- `/agent/chat` p95 first token ≤ 800 ms
- Ingestion: complete 100 cafes in ≤ 10 minutes wall-clock

---

## 8. Risks & Mitigations

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Yelp Fusion approval takes > 3 days | Medium | Start Week 1 with Google-only; reconcile is a no-op until key arrives. |
| LLM-extracted `has_outlet` is unreliable | High | Explicitly allow `null`; surface a confidence field; do not lie about coverage in the blog post. |
| RAGAS scores are noisy on 30-query set | Medium | Acceptable for a learning project; mention in blog as a known limitation. |
| EC2 deployment eats a weekend day | Medium | Have a fallback `Fly.io` deploy script ready in `infra/fly/` (a few hours of work, not implemented unless EC2 path fails). |
| Map provider lock-in (decision deferred to Week 3) | Low | The frontend abstracts pin rendering behind a `MapAdapter` interface; switching providers later is ~50 lines. |
| Public map token leak | Low | Only the publishable token is shipped to the browser; restricted by allowed domains in the provider dashboard. |

---

## 9. Open Questions (to revisit before each week)

- **Week 2:** Do you want the LLM extractor to output text in English, Chinese, or both? Default plan: English (training data is mostly English reviews). Revisit when we see real data.
- **Week 3:** Map provider — Mapbox vs Google Maps JS vs MapLibre + OSM. Default plan: Mapbox (free tier sufficient, cleanest Next.js SDK). Decide at Week 3 brainstorm.
- **Week 3:** Do we surface the `Thought` step to end users, or only `Action`/`Observation`? Default plan: show all, but allow a "Simple mode" toggle.
- **Week 5:** Demo video voice — your voiceover or text-only captions? Default plan: text captions + screen recording.

---

## 10. Success Criteria (per week)

| Week | Hard pass criteria |
|------|-------------------|
| 1 | `/search` returns 5 plausible cafes for `"quiet place with outlets near USC"` in Postman. 100 rows in `cafes`, all with non-null `ambience_text` and `embedding`. |
| 2 | `docs/eval-results/2026-05-20-v1.json` exists with three numeric RAGAS metrics. Re-running the script reproduces them. |
| 3 | Live demo of multi-turn conversation: "find a quiet study spot" → "anything cheaper?" → "open now?", agent stays on context. |
| 4 | `context_precision` improved by ≥ 0.1 absolute from baseline; latency p95 reduced by ≥ 30%. All numbers generated by script. |
| 5 | Public HTTPS URL serves the live demo. README, blog draft, and demo video committed. |

---

## 11. Demo Video Outline (2 minutes)

1. **00:00–00:10** title card, "CoffeeCompass — a RAG coffee finder built in 5 weeks"
2. **00:10–00:40** open the live URL, type "quiet café with outlets near USC", show streaming agent + map pins
3. **00:40–01:10** ask follow-up: "anything cheaper and open right now?" — agent re-queries, map updates
4. **01:10–01:35** quick cut to terminal: run `python scripts/plot_eval.py`, show context_precision 0.71 → 0.84 chart
5. **01:35–01:55** architecture diagram with one-sentence callouts (FastAPI + pgvector + LangChain + Zep + Vercel)
6. **01:55–02:00** GitHub URL + your contact

---

## 12. Next Step

After your review of this spec, the next action is to invoke the `writing-plans` skill to produce **`docs/superpowers/plans/2026-05-13-week1-plan.md`** — a step-by-step implementation plan for Week 1 only. Subsequent weeks get their own plans at the start of each week.
