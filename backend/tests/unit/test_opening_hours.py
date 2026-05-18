from datetime import datetime
from zoneinfo import ZoneInfo

from app.search.opening_hours import is_open_at

LA = ZoneInfo("America/Los_Angeles")


def test_open_within_period():
    hours = {
        "periods": [
            {
                "open": {"day": 1, "hour": 7, "minute": 0},
                "close": {"day": 1, "hour": 20, "minute": 0},
            }
        ]
    }
    when = datetime(2026, 5, 11, 10, 0, tzinfo=LA)  # Monday 10am
    assert is_open_at(hours, when) is True


def test_closed_before_open():
    hours = {
        "periods": [
            {
                "open": {"day": 1, "hour": 7, "minute": 0},
                "close": {"day": 1, "hour": 20, "minute": 0},
            }
        ]
    }
    when = datetime(2026, 5, 11, 6, 0, tzinfo=LA)
    assert is_open_at(hours, when) is False


def test_closed_no_period_for_day():
    hours = {
        "periods": [
            {
                "open": {"day": 1, "hour": 7, "minute": 0},
                "close": {"day": 1, "hour": 20, "minute": 0},
            }
        ]
    }
    when = datetime(2026, 5, 10, 10, 0, tzinfo=LA)  # Sunday
    assert is_open_at(hours, when) is False


def test_unknown_hours_returns_false():
    assert is_open_at(None, datetime(2026, 5, 11, 10, 0, tzinfo=LA)) is False
    assert is_open_at({}, datetime(2026, 5, 11, 10, 0, tzinfo=LA)) is False
