"""
Task manager — CRUD for study tasks.
"""

from database.db_connection import get_supabase_client


def create_task(
    user_id: str,
    subject_id: str,
    task_name: str,
    due_date: str,
    estimated_hours: float = 1.0,
) -> dict | None:
    """Create a new study task."""
    try:
        db = get_supabase_client()
        result = (
            db.table("tasks")
            .insert({
                "user_id": user_id,
                "subject_id": subject_id,
                "task_name": task_name,
                "due_date": due_date,
                "estimated_hours": estimated_hours,
                "status": "Pending",
            })
            .execute()
        )
        return result.data[0] if result.data else None
    except Exception:
        return None


def get_tasks(user_id: str) -> list[dict]:
    """Return all tasks for a user, ordered by due date."""
    try:
        db = get_supabase_client()
        result = (
            db.table("tasks")
            .select("*")
            .eq("user_id", user_id)
            .order("due_date")
            .execute()
        )
        return result.data or []
    except Exception:
        return []


def get_pending_tasks(user_id: str) -> list[dict]:
    """Return only pending tasks for a user, ordered by due date."""
    try:
        db = get_supabase_client()
        result = (
            db.table("tasks")
            .select("*")
            .eq("user_id", user_id)
            .eq("status", "Pending")
            .order("due_date")
            .execute()
        )
        return result.data or []
    except Exception:
        return []


def update_task_status(task_id: str, status: str) -> bool:
    """Update a task's status (Pending / Completed)."""
    try:
        db = get_supabase_client()
        result = (
            db.table("tasks")
            .update({"status": status})
            .eq("task_id", task_id)
            .execute()
        )
        return bool(result.data)
    except Exception:
        return False


def update_task_due_date(task_id: str, new_due_date: str) -> bool:
    """Reschedule a task to a new due date."""
    try:
        db = get_supabase_client()
        result = (
            db.table("tasks")
            .update({"due_date": new_due_date})
            .eq("task_id", task_id)
            .execute()
        )
        return bool(result.data)
    except Exception:
        return False


def delete_task(task_id: str) -> bool:
    """Delete a task by ID."""
    try:
        db = get_supabase_client()
        result = db.table("tasks").delete().eq("task_id", task_id).execute()
        return bool(result.data)
    except Exception:
        return False


def auto_adjust_overdue_tasks(user_id: str) -> int:
    """
    Automatically reschedule overdue pending tasks to upcoming days.
    Spreads up to MAX_PER_DAY tasks per day starting from today.
    Returns the number of tasks rescheduled.
    """
    from datetime import date, timedelta

    today = date.today()

    try:
        pending = get_pending_tasks(user_id)
    except Exception:
        return 0

    overdue = [t for t in pending if t.get("due_date", "9999") < today.isoformat()]
    if not overdue:
        return 0

    MAX_PER_DAY = 4  # max tasks assigned to one day

    # Build current load map for upcoming days
    upcoming = [t for t in pending if t.get("due_date", "") >= today.isoformat()]
    day_load: dict[str, int] = {}
    for t in upcoming:
        d = t.get("due_date", "")
        if d:
            day_load[d] = day_load.get(d, 0) + 1

    rescheduled = 0
    offset = 0  # days from today

    for task in overdue:
        # Find the next day that's not at capacity
        while True:
            candidate = (today + timedelta(days=offset)).isoformat()
            if day_load.get(candidate, 0) < MAX_PER_DAY:
                break
            offset += 1
            if offset > 60:  # safety cap
                break

        candidate = (today + timedelta(days=offset)).isoformat()
        if update_task_due_date(task["task_id"], candidate):
            day_load[candidate] = day_load.get(candidate, 0) + 1
            rescheduled += 1
            # Move to next day slot every MAX_PER_DAY tasks
            if day_load[candidate] >= MAX_PER_DAY:
                offset += 1

    return rescheduled
