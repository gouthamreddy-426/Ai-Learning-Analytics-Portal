"""
AI-powered module generator.
Generates study modules for a subject, along with YouTube video suggestions
and quizzes/tests for each module.
"""

import json
from database.db_connection import get_supabase_client
from ai_services.ai_client import ask_llm, ask_llm_json
from ai_services.prompt_templates import (
    study_modules_prompt,
    youtube_videos_prompt,
    module_test_prompt,
)
from utils.helpers import parse_markdown_list


# ── Module Generation ─────────────────────────────────────────

def generate_and_save_modules(subject_id: str, subject_name: str, difficulty_level: str) -> list[dict]:
    """
    Call the LLM to generate modules, persist them, then return the list.
    """
    try:
        prompt = study_modules_prompt(subject_name, difficulty_level)
        raw = ask_llm(prompt, temperature=0.6)
        titles = parse_markdown_list(raw)

        db = get_supabase_client()
        rows = []
        for idx, title in enumerate(titles, start=1):
            rows.append({
                "subject_id": subject_id,
                "module_title": title,
                "module_order": idx,
                "difficulty_level": difficulty_level,
            })

        if rows:
            result = db.table("subject_modules").insert(rows).execute()
            return result.data or []
        return []
    except Exception:
        return []


def get_modules(subject_id: str) -> list[dict]:
    """Return all modules for a subject, ordered by module_order."""
    try:
        db = get_supabase_client()
        result = (
            db.table("subject_modules")
            .select("*")
            .eq("subject_id", subject_id)
            .order("module_order")
            .execute()
        )
        return result.data or []
    except Exception:
        return []


def mark_module_complete(module_id: str) -> bool:
    """Mark a module as completed."""
    try:
        from datetime import datetime
        db = get_supabase_client()
        result = (
            db.table("subject_modules")
            .update({"is_completed": True, "completed_at": datetime.now().isoformat()})
            .eq("module_id", module_id)
            .execute()
        )
        return bool(result.data)
    except Exception:
        return False


def mark_module_incomplete(module_id: str) -> bool:
    """Revert a module to incomplete."""
    try:
        db = get_supabase_client()
        result = (
            db.table("subject_modules")
            .update({"is_completed": False, "completed_at": None})
            .eq("module_id", module_id)
            .execute()
        )
        return bool(result.data)
    except Exception:
        return False


# ── YouTube Video Suggestions ─────────────────────────────────

def generate_and_save_videos(module_id: str, subject_name: str, module_title: str) -> list[dict]:
    """Generate video suggestions via LLM and persist them as search-based URLs."""
    try:
        from urllib.parse import quote_plus
        prompt = youtube_videos_prompt(subject_name, module_title)
        raw = ask_llm(prompt, temperature=0.5)

        db = get_supabase_client()
        videos = []
        for line in raw.strip().split("\n"):
            line = line.strip()
            if not line:
                continue
            # Remove leading number prefix
            for prefix in ["1. ", "2. ", "3. ", "- ", "• "]:
                if line.startswith(prefix):
                    line = line[len(prefix):]
                    break
            parts = line.split("|")
            if len(parts) >= 2:
                title = parts[0].strip()
                search_query = parts[1].strip()

                # Build a YouTube search URL from the query
                encoded_query = quote_plus(search_query)
                search_url = f"https://www.youtube.com/results?search_query={encoded_query}"

                videos.append({
                    "module_id": module_id,
                    "video_title": title,
                    "video_url": search_url,
                    "description": search_query,  # Store raw query for embedding
                })

        if videos:
            result = db.table("module_videos").insert(videos).execute()
            return result.data or []
        return []
    except Exception:
        return []


def get_videos(module_id: str) -> list[dict]:
    """Return all videos for a module."""
    try:
        db = get_supabase_client()
        result = (
            db.table("module_videos")
            .select("*")
            .eq("module_id", module_id)
            .execute()
        )
        return result.data or []
    except Exception:
        return []


# ── Module Quiz / Test ────────────────────────────────────────

def generate_and_save_test(module_id: str, subject_name: str, module_title: str) -> dict | None:
    """Generate a quiz via LLM and persist it."""
    try:
        prompt = module_test_prompt(subject_name, module_title)
        questions = ask_llm_json(prompt, temperature=0.4)

        if not isinstance(questions, list):
            return None

        db = get_supabase_client()
        result = (
            db.table("module_tests")
            .insert({
                "module_id": module_id,
                "questions": json.dumps(questions),
            })
            .execute()
        )
        return result.data[0] if result.data else None
    except Exception:
        return None


def get_test(module_id: str) -> dict | None:
    """Return the latest test for a module."""
    try:
        db = get_supabase_client()
        result = (
            db.table("module_tests")
            .select("*")
            .eq("module_id", module_id)
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )
        return result.data[0] if result.data else None
    except Exception:
        return None


def save_test_result(test_id: str, user_id: str, score: int, total: int, answers: list) -> dict | None:
    """Save a student's test attempt."""
    try:
        db = get_supabase_client()
        result = (
            db.table("test_results")
            .insert({
                "test_id": test_id,
                "user_id": user_id,
                "score": score,
                "total": total,
                "answers": json.dumps(answers),
            })
            .execute()
        )
        return result.data[0] if result.data else None
    except Exception:
        return None


def get_test_results(user_id: str) -> list[dict]:
    """Return all test results for a user."""
    try:
        db = get_supabase_client()
        result = (
            db.table("test_results")
            .select("*")
            .eq("user_id", user_id)
            .order("completed_at", desc=True)
            .execute()
        )
        return result.data or []
    except Exception:
        return []
