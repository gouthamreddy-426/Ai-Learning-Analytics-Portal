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
from datetime import datetime, timedelta

_SESSION_FILE = Path(__file__).parent.parent / ".session.json"

SESSION_EXPIRY_DAYS = 1


def save_session(user: dict) -> None:
    try:
        session_data = {
            "user": user,
            "login_time": datetime.now().isoformat()
        }

        _SESSION_FILE.write_text(
            json.dumps(session_data),
            encoding="utf-8"
        )
    except Exception:
        pass


def load_session():
    try:
        if not _SESSION_FILE.exists():
            return None

        data = json.loads(
            _SESSION_FILE.read_text(encoding="utf-8")
        )

        login_time = datetime.fromisoformat(
            data["login_time"]
        )

        if datetime.now() - login_time > timedelta(days=1):
            clear_session()
            return None

        return data["user"]

    except Exception:
        return None


def clear_session():
    try:
        if _SESSION_FILE.exists():
            _SESSION_FILE.unlink()
    except Exception:
        pass
