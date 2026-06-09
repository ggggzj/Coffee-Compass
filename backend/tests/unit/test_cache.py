import pytest

from app.search.cache import TTLLRUCache


def test_miss_then_hit():
    c: TTLLRUCache[str, int] = TTLLRUCache(maxsize=4, ttl_seconds=100)
    assert c.get("a") is None
    assert c.misses == 1
    c.set("a", 1)
    assert c.get("a") == 1
    assert c.hits == 1


def test_ttl_expiry(monkeypatch):
    clock = {"t": 1000.0}
    monkeypatch.setattr("app.search.cache.time.monotonic", lambda: clock["t"])
    c: TTLLRUCache[str, int] = TTLLRUCache(maxsize=4, ttl_seconds=10)
    c.set("a", 1)
    clock["t"] = 1005.0
    assert c.get("a") == 1  # still within TTL
    clock["t"] = 1011.0
    assert c.get("a") is None  # expired


def test_lru_eviction_orders_by_recency():
    c: TTLLRUCache[str, int] = TTLLRUCache(maxsize=2, ttl_seconds=100)
    c.set("a", 1)
    c.set("b", 2)
    assert c.get("a") == 1  # touch "a" so "b" is now least-recently-used
    c.set("c", 3)  # evicts "b"
    assert c.get("b") is None
    assert c.get("a") == 1
    assert c.get("c") == 3
    assert len(c) == 2


def test_hit_rate_and_clear():
    c: TTLLRUCache[str, int] = TTLLRUCache()
    c.get("x")  # miss
    c.set("x", 1)
    c.get("x")  # hit
    assert c.hit_rate == 0.5
    c.clear()
    assert len(c) == 0
    assert c.hits == 0 and c.misses == 0


def test_maxsize_validated():
    with pytest.raises(ValueError):
        TTLLRUCache(maxsize=0)
