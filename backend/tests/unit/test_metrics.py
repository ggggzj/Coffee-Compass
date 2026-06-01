import pytest

from app.eval.metrics import context_precision_score, cosine_similarity, mean


def test_context_precision():
    assert context_precision_score({1, 2, 3}, [1, 99, 2]) == 2 / 3
    assert context_precision_score({1}, []) == 0.0


def test_cosine_similarity():
    assert cosine_similarity([1.0, 0.0], [1.0, 0.0]) == 1.0
    assert cosine_similarity([1.0, 0.0], [0.0, 1.0]) == 0.0


def test_mean():
    assert mean([0.2, 0.4]) == pytest.approx(0.3)
    assert mean([]) == 0.0
