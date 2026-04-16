"""
AI-powered cheat sheet generator — supports both subject-level and module-level sheets.
"""

from database.db_connection import get_supabase_client
from ai_services.ai_client import ask_llm
from ai_services.prompt_templates import cheatsheet_prompt, cheatsheet_module_prompt


def generate_and_save_cheatsheet(
    subject_id: str,
    subject_name: str,
    module_id: str = None,
    module_title: str = None,
) -> dict | None:
    """
    Generate a cheat sheet via AI and persist it.
    If module_id + module_title are provided, generates a per-module sheet.
    Otherwise falls back to a subject-level sheet.
    """
    try:
        if module_id and module_title:
            prompt = cheatsheet_module_prompt(subject_name, module_title)
        else:
            prompt = cheatsheet_prompt(subject_name)

        content = ask_llm(prompt, temperature=0.6)

        db = get_supabase_client()
        row = {
            "subject_id": subject_id,
            "content": content,
        }
        # Store module info if the table has those columns (added via migration)
        if module_id:
            row["module_id"]    = module_id
            row["module_title"] = module_title or ""

        result = db.table("cheatsheets").insert(row).execute()
        return result.data[0] if result.data else None
    except Exception:
        return None


def get_cheatsheets(subject_id: str) -> list[dict]:
    """Return all cheat sheets for a subject, newest first."""
    try:
        db = get_supabase_client()
        result = (
            db.table("cheatsheets")
            .select("*")
            .eq("subject_id", subject_id)
            .order("created_at", desc=True)
            .execute()
        )
        return result.data or []
    except Exception:
        return []


def get_cheatsheets_by_module(module_id: str) -> list[dict]:
    """Return all cheat sheets for a specific module, newest first."""
    try:
        db = get_supabase_client()
        result = (
            db.table("cheatsheets")
            .select("*")
            .eq("module_id", module_id)
            .order("created_at", desc=True)
            .execute()
        )
        return result.data or []
    except Exception:
        return []


def get_latest_cheatsheet(subject_id: str) -> dict | None:
    """Return the latest cheat sheet for a subject."""
    try:
        db = get_supabase_client()
        result = (
            db.table("cheatsheets")
            .select("*")
            .eq("subject_id", subject_id)
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )
        return result.data[0] if result.data else None
    except Exception:
        return None


def delete_cheatsheet(cheatsheet_id: str) -> bool:
    """Delete a cheat sheet by ID."""
    try:
        db = get_supabase_client()
        result = db.table("cheatsheets").delete().eq("cheatsheet_id", cheatsheet_id).execute()
        return bool(result.data)
    except Exception:
        return False
