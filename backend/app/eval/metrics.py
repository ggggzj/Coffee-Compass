"""Week 2 eval metrics (RAGAS-aligned; embedding-based proxies)."""

from __future__ import annotations


def cosine_similarity(a: list[float], b: list[float]) -> float:
    if len(a) != len(b) or not a:
        return 0.0
    dot = sum(x * y for x, y in zip(a, b, strict=True))
    na = sum(x * x for x in a) ** 0.5
    nb = sum(x * x for x in b) ** 0.5
    if na == 0 or nb == 0:
        return 0.0
    # clamp for FP drift
    s = dot / (na * nb)
    return max(-1.0, min(1.0, s))


def context_precision_score(expected: set[int], retrieved_ids: list[int]) -> float:
    """Fraction of retrieved results that are in the expected set (spec Week 2)."""
    if not retrieved_ids:
        return 0.0
    hits = sum(1 for i in retrieved_ids if i in expected)
    return hits / len(retrieved_ids)


def mean(xs: list[float]) -> float:
    return sum(xs) / len(xs) if xs else 0.0
