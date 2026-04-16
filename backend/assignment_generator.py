"""
AI-powered assignment generator.
"""

from database.db_connection import get_supabase_client
from ai_services.ai_client import ask_llm
from ai_services.prompt_templates import assignment_prompt


def generate_and_save_assignment(subject_id: str, subject_name: str) -> dict | None:
    """Generate an assignment via AI and persist it."""
    try:
        prompt = assignment_prompt(subject_name)
        content = ask_llm(prompt, temperature=0.7)

        db = get_supabase_client()
        result = (
            db.table("assignments")
            .insert({
                "subject_id": subject_id,
                "assignment_text": content,
            })
            .execute()
        )
        return result.data[0] if result.data else None
    except Exception:
        return None


def get_assignments(subject_id: str) -> list[dict]:
    """Return all assignments for a subject, newest first."""
    try:
        db = get_supabase_client()
        result = (
            db.table("assignments")
            .select("*")
            .eq("subject_id", subject_id)
            .order("created_at", desc=True)
            .execute()
        )
        return result.data or []
    except Exception:
        return []


def get_all_assignments_for_user(user_id: str) -> list[dict]:
    """Return all assignments across every subject the user is enrolled in."""
    try:
        db = get_supabase_client()
        # First get all subject IDs for the user
        subjects = (
            db.table("subjects")
            .select("subject_id, subject_name")
            .eq("user_id", user_id)
            .execute()
        )
        if not subjects.data:
            return []

        all_assignments = []
        for subj in subjects.data:
            try:
                assignments = (
                    db.table("assignments")
                    .select("*")
                    .eq("subject_id", subj["subject_id"])
                    .order("created_at", desc=True)
                    .execute()
                )
                for a in (assignments.data or []):
                    a["subject_name"] = subj["subject_name"]
                    all_assignments.append(a)
            except Exception:
                continue
        return all_assignments
    except Exception:
        return []


def delete_assignment(assignment_id: str) -> bool:
    """Delete an assignment by ID."""
    try:
        db = get_supabase_client()
        result = db.table("assignments").delete().eq("assignment_id", assignment_id).execute()
        return bool(result.data)
    except Exception:
        return False
