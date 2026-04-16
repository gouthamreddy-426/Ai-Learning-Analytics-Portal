"""
Progress metrics — calculations for the analytics dashboard.
"""

from backend.subject_manager import get_subjects
from backend.module_generator import get_modules
from backend.task_manager import get_tasks
from utils.helpers import percentage, week_date_range


def get_subject_progress(user_id: str) -> list[dict]:
    """
    Return a list of dicts with subject-level completion metrics:
    [{subject_name, total_modules, completed_modules, progress_pct}, ...]
    """
    subjects = get_subjects(user_id)
    progress = []
    for subj in subjects:
        modules = get_modules(subj["subject_id"])
        total = len(modules)
        completed = sum(1 for m in modules if m.get("is_completed"))
        progress.append({
            "subject_id": subj["subject_id"],
            "subject_name": subj["subject_name"],
            "difficulty": subj["difficulty_level"],
            "total_modules": total,
            "completed_modules": completed,
            "progress_pct": percentage(completed, total),
        })
    return progress


def get_task_stats(user_id: str) -> dict:
    """
    Return overall task statistics:
    {total, completed, pending, completion_rate}
    """
    tasks = get_tasks(user_id)
    total = len(tasks)
    completed = sum(1 for t in tasks if t.get("status") == "Completed")
    pending = total - completed
    return {
        "total": total,
        "completed": completed,
        "pending": pending,
        "completion_rate": percentage(completed, total),
    }


def get_weekly_task_stats(user_id: str) -> dict:
    """
    Return task stats scoped to the current week (Mon–Sun).
    """
    tasks = get_tasks(user_id)
    start, end = week_date_range()
    weekly = [
        t for t in tasks
        if t.get("due_date") and start.isoformat() <= t["due_date"] <= end.isoformat()
    ]
    total = len(weekly)
    completed = sum(1 for t in weekly if t.get("status") == "Completed")
    return {
        "total": total,
        "completed": completed,
        "pending": total - completed,
        "completion_rate": percentage(completed, total),
        "week_start": start.isoformat(),
        "week_end": end.isoformat(),
    }


def get_overall_progress(user_id: str) -> float:
    """Return the overall learning progress as a percentage (0-100)."""
    progress_list = get_subject_progress(user_id)
    if not progress_list:
        return 0.0
    return round(
        sum(p["progress_pct"] for p in progress_list) / len(progress_list), 1
    )
