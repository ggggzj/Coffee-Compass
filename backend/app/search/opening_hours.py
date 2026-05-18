from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

LA = ZoneInfo("America/Los_Angeles")


def is_open_at(hours: dict | None, when: datetime) -> bool:
    """Google Places day convention: Sunday=0..Saturday=6.

    `when` should be timezone-aware. Periods are compared in LA local time.
    Same-day periods only (overnight windows like a 24h cafe are not common in our
    100-cafe set; revisit in Week 2 if it becomes an issue).
    """
    if not hours or "periods" not in hours:
        return False
    local = when.astimezone(LA)
    weekday = (local.weekday() + 1) % 7  # Mon=0 -> 1, Sun=6 -> 0
    minutes_now = local.hour * 60 + local.minute
    for period in hours.get("periods", []):
        op = period.get("open", {})
        cl = period.get("close", {})
        if op.get("day") != weekday:
            continue
        op_min = op.get("hour", 0) * 60 + op.get("minute", 0)
        cl_min = cl.get("hour", 0) * 60 + cl.get("minute", 0)
        if op_min <= minutes_now < cl_min:
            return True
    return False
