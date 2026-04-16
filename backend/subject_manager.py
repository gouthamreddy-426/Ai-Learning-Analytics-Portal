"""
Subject enrollment manager.
Handles CRUD operations for the subjects table.
"""

from database.db_connection import get_supabase_client


def enroll_subject(
    user_id: str,
    subject_name: str,
    difficulty_level: str,
    exam_date: str | None = None,
) -> dict:
    """
    Enroll the student in a new subject with optional exam deadline.
    Returns the inserted subject row or None.
    """
    try:
        db = get_supabase_client()
        row = {
            "user_id": user_id,
            "subject_name": subject_name,
            "difficulty_level": difficulty_level,
        }
        if exam_date:
            row["exam_date"] = exam_date

        result = db.table("subjects").insert(row).execute()
        return result.data[0] if result.data else None
    except Exception:
        return None


def get_subjects(user_id: str) -> list[dict]:
    """Return all subjects for a given user, ordered by creation date."""
    try:
        db = get_supabase_client()
        result = (
            db.table("subjects")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .execute()
        )
        return result.data or []
    except Exception:
        return []


def get_subject_by_id(subject_id: str) -> dict | None:
    """Fetch a single subject by its ID."""
    try:
        db = get_supabase_client()
        result = db.table("subjects").select("*").eq("subject_id", subject_id).execute()
        return result.data[0] if result.data else None
    except Exception:
        return None


def delete_subject(subject_id: str) -> bool:
    """Delete a subject and cascade to modules, assignments, etc."""
    try:
        db = get_supabase_client()
        result = db.table("subjects").delete().eq("subject_id", subject_id).execute()
        return bool(result.data)
    except Exception:
        return False
