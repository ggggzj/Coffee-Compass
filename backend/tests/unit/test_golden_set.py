from pathlib import Path

from app.eval.golden_set import load_golden_set


def test_golden_set_loads_and_has_thirty_items():
    g = load_golden_set()
    assert g.version == 2
    assert len(g.items) == 30
    assert g.items[0].id == "g001"
    assert len(g.items[0].expected_cafe_ids) >= 1
    # every expected id must be a real cafe id we labelled against (4..58 range)
    assert all(cid >= 4 for item in g.items for cid in item.expected_cafe_ids)


def test_golden_set_from_path(tmp_path: Path):
    p = tmp_path / "g.json"
    p.write_text(
        '{"version": 1, "items": [{"id": "x", "query": "q", "expected_cafe_ids": [1]}]}',
        encoding="utf-8",
    )
    g = load_golden_set(p)
    assert len(g.items) == 1
