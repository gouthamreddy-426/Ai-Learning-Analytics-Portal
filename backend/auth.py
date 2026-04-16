"""
Authentication backend — signup, login, session helpers.
Passwords are hashed with bcrypt before storage.
"""

import bcrypt
from database.db_connection import get_supabase_client


# ── Password Utilities ────────────────────────────────────────

def hash_password(password: str) -> str:
    """Return a bcrypt hash of *password*."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    """Verify *password* against a bcrypt *hashed* value."""
    try:
        return bcrypt.checkpw(password.encode(), hashed.encode())
    except Exception:
        return False


# ── Signup ────────────────────────────────────────────────────

def signup(name: str, email: str, password: str) -> dict:
    """
    Create a new user account.
    Returns {"success": True, "user": {...}} or {"success": False, "error": "..."}.
    """
    try:
        db = get_supabase_client()

        # Check if email already registered
        existing = db.table("users").select("user_id").eq("email", email).execute()
        if existing.data:
            return {"success": False, "error": "An account with this email already exists."}

        pw_hash = hash_password(password)
        result = (
            db.table("users")
            .insert({"name": name, "email": email, "password_hash": pw_hash})
            .execute()
        )

        if result.data:
            return {"success": True, "user": result.data[0]}
        return {"success": False, "error": "Registration failed. Please try again."}

    except Exception as e:
        error_msg = str(e)
        if "duplicate" in error_msg.lower() or "unique" in error_msg.lower():
            return {"success": False, "error": "An account with this email already exists."}
        if "connection" in error_msg.lower() or "timeout" in error_msg.lower():
            return {"success": False, "error": "Unable to connect to the server. Please check your internet connection and try again."}
        return {"success": False, "error": f"Registration failed: {error_msg}"}


# ── Login ─────────────────────────────────────────────────────

def login(email: str, password: str) -> dict:
    """
    Authenticate a user.
    Returns {"success": True, "user": {...}} or {"success": False, "error": "..."}.
    """
    try:
        db = get_supabase_client()
        result = db.table("users").select("*").eq("email", email).execute()

        if not result.data:
            return {"success": False, "error": "No account found with this email."}

        user = result.data[0]
        if not verify_password(password, user["password_hash"]):
            return {"success": False, "error": "Incorrect password."}

        return {"success": True, "user": user}

    except Exception as e:
        error_msg = str(e)
        if "connection" in error_msg.lower() or "timeout" in error_msg.lower():
            return {"success": False, "error": "Unable to connect to the server. Please check your internet connection and try again."}
        return {"success": False, "error": f"Login failed: {error_msg}"}


# ── Profile ───────────────────────────────────────────────────

def get_user_profile(user_id: str) -> dict | None:
    """Fetch the full user row by user_id."""
    try:
        db = get_supabase_client()
        result = db.table("users").select("*").eq("user_id", user_id).execute()
        return result.data[0] if result.data else None
    except Exception:
        return None


def update_user_name(user_id: str, new_name: str) -> bool:
    """Update the user's display name."""
    try:
        db = get_supabase_client()
        result = (
            db.table("users")
            .update({"name": new_name})
            .eq("user_id", user_id)
            .execute()
        )
        return bool(result.data)
    except Exception:
        return False
