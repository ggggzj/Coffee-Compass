// k6 load test for POST /search.
//
// Produces the latency numbers cited on the resume:
//   - end-to-end p50/p95 (http_req_duration), and
//   - per-stage p50/p95 from the X-*-Ms response headers the API emits
//     (X-Pgvector-Ms = retrieval stage, X-Llm-Ms, X-Embed-Ms, X-Total-Ms).
//
// The retrieval-stage threshold (pgvector_ms p95 < 250) is the honest source for
// the "p95 latency under 250ms ... pgvector ANN + SQL filters" claim. End-to-end
// p95 will be higher because it includes the slot-extractor + embedding OpenAI
// calls — UNLESS the in-process slot cache is warm, in which case repeated
// queries skip both and total latency collapses toward pgvector_ms.
//
// Prereqs: backend running with ingested data, and `brew install k6`.
//
// Run (defaults: 10 VUs, 200 iterations):
//   k6 run backend/loadtest/search.js
// Override:
//   BASE_URL=http://localhost:8000 VUS=20 ITERATIONS=200 k6 run backend/loadtest/search.js
//
// Cache note: the query pool below is small, so after the first pass most
// requests are cache HITS (fast path). To measure the COLD path (every request
// pays the LLM calls), restart the server first and set ITERATIONS<=20, or
// expand UNIQUE_SUFFIX to force distinct cache keys.

import http from 'k6/http';
import { check } from 'k6';
import { Trend } from 'k6/metrics';

const pgvectorMs = new Trend('pgvector_ms', true);
const llmMs = new Trend('llm_ms', true);
const embedMs = new Trend('embed_ms', true);
const serverTotalMs = new Trend('server_total_ms', true);

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';

const QUERIES = [
  'quiet place to study near USC',
  'coffee shop with outlets and wifi for laptop work',
  'cheap latte open now',
  'good first date coffee spot not too loud',
  'cozy reading nook with natural light',
  'open late for finals week',
  'lively cafe to meet friends',
  'best espresso within walking distance of campus',
  'spacious cafe with lots of seating for a group',
  'matcha and pastries somewhere calm',
  '安静的适合学习的咖啡馆', // Chinese: quiet cafe good for studying
  '有插座的便宜咖啡店',     // Chinese: cheap cafe with outlets
  'aesthetic minimalist coffee bar',
  'dog friendly patio coffee',
  'late night study spot with strong wifi',
];

export const options = {
  scenarios: {
    search: {
      executor: 'shared-iterations',
      vus: Number(__ENV.VUS || 10),
      iterations: Number(__ENV.ITERATIONS || 200),
      maxDuration: '3m',
    },
  },
  thresholds: {
    http_req_failed: ['rate<0.01'],
    http_req_duration: ['p(95)<1500'], // end-to-end incl. OpenAI calls (cold)
    pgvector_ms: ['p(95)<250'],        // retrieval-stage target — the resume claim
  },
};

export default function () {
  const q = QUERIES[Math.floor(Math.random() * QUERIES.length)];
  const res = http.post(
    `${BASE_URL}/search`,
    JSON.stringify({ query: q, top_k: 5 }),
    { headers: { 'Content-Type': 'application/json' } },
  );

  check(res, {
    'status is 200': (r) => r.status === 200,
    'has results': (r) => {
      try {
        return Array.isArray(r.json().results);
      } catch (_e) {
        return false;
      }
    },
  });

  // Go canonicalizes header names: X-LLM-Ms -> X-Llm-Ms.
  const h = res.headers;
  if (h['X-Pgvector-Ms']) pgvectorMs.add(parseFloat(h['X-Pgvector-Ms']));
  if (h['X-Llm-Ms']) llmMs.add(parseFloat(h['X-Llm-Ms']));
  if (h['X-Embed-Ms']) embedMs.add(parseFloat(h['X-Embed-Ms']));
  if (h['X-Total-Ms']) serverTotalMs.add(parseFloat(h['X-Total-Ms']));
}
