"""
Shared helper utilities used across the application.
"""

import uuid
import hashlib
from datetime import datetime, timedelta


def generate_uuid() -> str:
    """Generate a new UUID4 string."""
    return str(uuid.uuid4())


def format_date(dt: datetime | str, fmt: str = "%b %d, %Y") -> str:
    """Format a datetime object or ISO string for display."""
    if isinstance(dt, str):
        dt = datetime.fromisoformat(dt.replace("Z", "+00:00"))
    return dt.strftime(fmt)


def days_until(target_date: str | datetime) -> int:
    """Return the number of days from today until *target_date*."""
    if isinstance(target_date, str):
        target_date = datetime.fromisoformat(target_date)
    delta = target_date.date() - datetime.now().date()
    return delta.days


def percentage(part: int | float, total: int | float) -> float:
    """Safely compute a percentage (returns 0 when total is 0)."""
    return round((part / total) * 100, 1) if total else 0.0


def truncate(text: str, max_len: int = 120) -> str:
    """Truncate long text with an ellipsis."""
    return text[:max_len] + "…" if len(text) > max_len else text


def week_date_range():
    """Return (start, end) dates for the current week (Mon–Sun)."""
    today = datetime.now().date()
    start = today - timedelta(days=today.weekday())
    end = start + timedelta(days=6)
    return start, end


def parse_markdown_list(text: str) -> list[str]:
    """Parse a markdown-style numbered or bulleted list into items."""
    lines = text.strip().split("\n")
    items = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # Strip leading bullet/number markers
        for prefix in ["- ", "• ", "* "]:
            if line.startswith(prefix):
                line = line[len(prefix):]
                break
        # Strip numbered prefix like "1. " or "1) "
        if len(line) > 2 and line[0].isdigit():
            for sep in [". ", ") "]:
                idx = line.find(sep)
                if idx != -1 and idx < 4:
                    line = line[idx + len(sep):]
                    break
        items.append(line.strip())
    return items
