from __future__ import annotations

import time
from collections import OrderedDict
from collections.abc import Hashable


class TTLLRUCache[K: Hashable, V]:
    """A small in-process cache with per-entry TTL and LRU eviction.

    Used to short-circuit the slot-extractor + embedding LLM calls for repeated
    queries. On a cache hit a /search request skips both OpenAI round-trips, so
    its latency collapses to the pgvector retrieval stage. Single-process only
    (no cross-worker sharing) — that is intentional for a single-node demo.
    """

    def __init__(self, *, maxsize: int = 512, ttl_seconds: float = 600.0) -> None:
        if maxsize < 1:
            raise ValueError("maxsize must be >= 1")
        self._maxsize = maxsize
        self._ttl = ttl_seconds
        self._store: OrderedDict[K, tuple[float, V]] = OrderedDict()
        self.hits = 0
        self.misses = 0

    def get(self, key: K) -> V | None:
        item = self._store.get(key)
        if item is None:
            self.misses += 1
            return None
        expires_at, value = item
        if expires_at <= time.monotonic():
            del self._store[key]
            self.misses += 1
            return None
        self._store.move_to_end(key)
        self.hits += 1
        return value

    def set(self, key: K, value: V) -> None:
        if key in self._store:
            self._store.move_to_end(key)
        self._store[key] = (time.monotonic() + self._ttl, value)
        while len(self._store) > self._maxsize:
            self._store.popitem(last=False)

    def clear(self) -> None:
        self._store.clear()
        self.hits = 0
        self.misses = 0

    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return self.hits / total if total else 0.0

    def __len__(self) -> int:
        return len(self._store)
