"""
session_manager.py — Simple, reliable persistent login via a local session file.

How it works:
  - On login   → writes user dict to .session.json in the project root
  - On reload → app.py reads .session.json and auto-restores the session
  - On logout  → .session.json is deleted

This requires NO extra packages and has zero async/component issues.
It is ideal for a single-user local development application.
"""

import json
from pathlib import Path

# Session file lives in the project root (same dir as app.py)
_SESSION_FILE = Path(__file__).parent.parent / ".session.json"


def save_session(user: dict) -> None:
    """Persist the user dict to disk."""
    try:
        _SESSION_FILE.write_text(json.dumps(user), encoding="utf-8")
    except Exception:
        pass


def load_session() -> dict | None:
    """
    Read the session file and return the user dict, or None if not found / invalid.
    """
    try:
        if _SESSION_FILE.exists():
            data = json.loads(_SESSION_FILE.read_text(encoding="utf-8"))
            if isinstance(data, dict) and data.get("user_id"):
                return data
    except Exception:
        pass
    return None


def clear_session() -> None:
    """Delete the session file (called on logout)."""
    try:
        if _SESSION_FILE.exists():
            _SESSION_FILE.unlink()
    except Exception:
        pass


# Keep these for backwards-compat in case anything still imports them
def get_cookie_manager():
    pass
