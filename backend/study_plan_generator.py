"""
AI-powered study plan generator.
Builds a COMPLETE multi-week study plan from today until all deadlines,
covering ALL incomplete modules across ALL enrolled subjects.
Auto-creates tasks for every day in the plan.
"""

import json
import math
from datetime import datetime, timedelta
from database.db_connection import get_supabase_client
from ai_services.ai_client import ask_llm_json
from ai_services.prompt_templates import study_plan_prompt
from backend.subject_manager import get_subjects
from backend.module_generator import get_modules
from backend.task_manager import get_pending_tasks, create_task


# ── Context Builders ──────────────────────────────────────────

def _build_subjects_info(user_id: str) -> tuple[str, list[dict]]:
    """
    Build a detailed summary of subjects with deadlines and progress.
    Returns (info_string, subjects_with_modules_list).
    """
    subjects = get_subjects(user_id)
    if not subjects:
        return "No subjects enrolled yet.", []

    today = datetime.now().date()
    lines = []
    enriched = []

    for subj in subjects:
        modules = get_modules(subj["subject_id"])
        total = len(modules)
        completed = sum(1 for m in modules if m.get("is_completed"))
        pct = round(completed / total * 100) if total else 0

        incomplete_modules = [
            m for m in modules if not m.get("is_completed")
        ]
        incomplete_names = [m["module_title"] for m in incomplete_modules]
        modules_str = ", ".join(incomplete_names) if incomplete_names else "All completed"

        # Calculate days until exam
        exam_date = subj.get("exam_date", "")
        deadline_str = "No deadline set"
        days_left = 62  # default for no deadline
        if exam_date:
            try:
                exam_dt = datetime.fromisoformat(str(exam_date)).date()
                days_left = (exam_dt - today).days
                deadline_str = f"Exam on {exam_date} ({days_left} days left)"
            except Exception:
                pass

        line = (
            f"- {subj['subject_name']} | Difficulty: {subj['difficulty_level']} | "
            f"Progress: {completed}/{total} modules ({pct}%) | "
            f"Deadline: {deadline_str} | "
            f"Remaining modules: {modules_str}"
        )
        lines.append(line)

        enriched.append({
            "subject_id": subj["subject_id"],
            "subject_name": subj["subject_name"],
            "difficulty_level": subj["difficulty_level"],
            "exam_date": exam_date,
            "days_left": days_left,
            "total_modules": total,
            "completed_modules": completed,
            "incomplete_modules": incomplete_names,
        })

    return "\n".join(lines), enriched


def _build_modules_to_complete(enriched_subjects: list[dict]) -> str:
    """Build a numbered list of ALL modules that must be completed, grouped by subject."""
    if not enriched_subjects:
        return "No modules to complete."

    lines = []
    module_num = 0
    for subj in sorted(enriched_subjects, key=lambda s: s["days_left"]):
        if not subj["incomplete_modules"]:
            continue
        lines.append(f"\n📚 {subj['subject_name']} (Deadline: {subj['exam_date'] or 'None'}, "
                     f"Difficulty: {subj['difficulty_level']}):")
        for mod_name in subj["incomplete_modules"]:
            module_num += 1
            lines.append(f"  {module_num}. {mod_name}")

    if not lines:
        return "All modules completed! 🎉"
    return "\n".join(lines)


def _calculate_weeks_needed(enriched_subjects: list[dict]) -> int:
    """Calculate how many weeks the plan should cover based on deadlines."""
    today = datetime.now().date()

    # Find the furthest deadline
    max_days = 7  # minimum 1 week
    for subj in enriched_subjects:
        if subj["incomplete_modules"]:
            max_days = max(max_days, subj["days_left"])

    # Cap at 8 weeks (56 days) to keep AI output manageable
    max_days = min(max_days, 56)
    # At least 1 week
    weeks = max(1, math.ceil(max_days / 7))
    return min(weeks, 8)


def _get_week_boundaries(total_weeks: int) -> list[tuple]:
    """
    Return a list of (week_start_date, week_end_date) tuples.
    Week 1: today → coming Sunday (may be a partial week).
    Week 2+: strict Monday → Sunday blocks with NO overlap.
    """
    today = datetime.now().date()
    boundaries = []

    # Week 1 ends on the Sunday of the current week
    days_until_sunday = 6 - today.weekday()  # weekday(): Mon=0 … Sun=6
    week1_end = today + timedelta(days=days_until_sunday)
    boundaries.append((today, week1_end))

    # Subsequent weeks: full Mon–Sun blocks
    next_monday = week1_end + timedelta(days=1)  # always a Monday
    for _ in range(1, total_weeks):
        week_start = next_monday
        week_end = week_start + timedelta(days=6)  # Sunday
        boundaries.append((week_start, week_end))
        next_monday = week_end + timedelta(days=1)

    return boundaries


def _build_week_dates(total_weeks: int) -> str:
    """Build a date-range string for each week (used in the AI prompt)."""
    boundaries = _get_week_boundaries(total_weeks)
    lines = []
    for w, (week_start, week_end) in enumerate(boundaries):
        lines.append(
            f"Week {w + 1}: {week_start.strftime('%b %d')} - {week_end.strftime('%b %d, %Y')} "
            f"({week_start.isoformat()} to {week_end.isoformat()})"
        )
    return "\n".join(lines)


def _get_skipped_tasks_info(user_id: str) -> str:
    """Build info about tasks that are past due and still pending (skipped)."""
    tasks = get_pending_tasks(user_id)
    if not tasks:
        return "None"

    today = datetime.now().date()
    skipped = []
    for t in tasks:
        due = t.get("due_date", "")
        if due:
            try:
                due_dt = datetime.fromisoformat(str(due)).date()
                if due_dt < today:
                    skipped.append(
                        f"- {t['task_name']} (was due {due}, {(today - due_dt).days} days overdue)"
                    )
            except Exception:
                pass

    return "\n".join(skipped) if skipped else "None"


# ── Plan Generation ───────────────────────────────────────────

def generate_and_save_plan(
    user_id: str,
    study_hours: float = 3.0,
) -> dict | None:
    """Generate a COMPLETE multi-week study plan, save it, and auto-create tasks."""
    subjects_info, enriched_subjects = _build_subjects_info(user_id)

    if not enriched_subjects:
        return None

    # Check if there are any incomplete modules at all
    total_incomplete = sum(len(s["incomplete_modules"]) for s in enriched_subjects)
    if total_incomplete == 0:
        return None

    modules_to_complete = _build_modules_to_complete(enriched_subjects)
    total_weeks = _calculate_weeks_needed(enriched_subjects)
    week_dates = _build_week_dates(total_weeks)
    skipped_tasks = _get_skipped_tasks_info(user_id)
    today = datetime.now().date()

    prompt = study_plan_prompt(
        subjects_info=subjects_info,
        modules_to_complete=modules_to_complete,
        total_weeks=total_weeks,
        week_dates=week_dates,
        today_date=today.isoformat(),
        study_hours_per_day=study_hours,
        skipped_tasks=skipped_tasks,
    )

    # Use higher max_tokens for multi-week plans
    max_tokens = min(4000 + (total_weeks * 1500), 8000)
    plan_data = ask_llm_json(prompt, temperature=0.7, max_tokens=max_tokens)

    if not isinstance(plan_data, list):
        return None

    # Normalize: handle both flat day-list and nested week-list formats
    plan_data = _normalize_plan_data(plan_data, total_weeks)

    # Save the structured plan with metadata
    plan_metadata = {
        "total_weeks": total_weeks,
        "total_incomplete_modules": total_incomplete,
        "subjects_count": len(enriched_subjects),
        "study_hours_per_day": study_hours,
        "generated_for": today.isoformat(),
    }

    db = get_supabase_client()
    result = (
        db.table("study_plans")
        .insert({
            "user_id": user_id,
            "plan_content": json.dumps({
                "metadata": plan_metadata,
                "weeks": plan_data,
            }),
        })
        .execute()
    )

    if not result.data:
        return None

    plan = result.data[0]

    # Auto-create tasks from the plan
    _auto_create_tasks_from_plan(user_id, plan_data)

    return plan


def _normalize_plan_data(plan_data: list, total_weeks: int) -> list[dict]:
    """
    Normalize the AI response to ensure it's in the correct week-based format.
    Handles cases where the AI returns a flat day list instead of nested weeks.
    Then fills in any missing days so every week has all 7 days.
    """
    if not plan_data:
        return []

    weeks = []

    # Check if it's already in week format
    if isinstance(plan_data[0], dict) and "week" in plan_data[0] and "days" in plan_data[0]:
        weeks = plan_data
    elif isinstance(plan_data[0], dict) and "day" in plan_data[0]:
        # Flat list of days — group them into weeks
        for i in range(0, len(plan_data), 7):
            week_days = plan_data[i:i + 7]
            week_num = (i // 7) + 1
            first_date = week_days[0].get("date", "") if week_days else ""
            last_date = week_days[-1].get("date", "") if week_days else ""
            # Format label safely
            try:
                from datetime import datetime as _dt
                f_fmt = _dt.fromisoformat(first_date).strftime("%b %d") if first_date else "?"
                l_fmt = _dt.fromisoformat(last_date).strftime("%b %d, %Y") if last_date else "?"
                label = f"Week {week_num}: {f_fmt} – {l_fmt}"
            except Exception:
                label = f"Week {week_num}: {first_date} to {last_date}"
            weeks.append({
                "week": week_num,
                "week_label": label,
                "days": week_days,
            })
    else:
        return plan_data

    # Fill missing days in every week
    weeks = _fill_missing_days(weeks)

    return weeks


DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def _fill_missing_days(weeks: list[dict]) -> list[dict]:
    """
    Ensure every week has exactly the right days with no cross-week overlap.
    Uses _get_week_boundaries as the single source of truth for date ranges:
      - Week 1: today → coming Sunday (partial week allowed)
      - Week 2+: Monday → Sunday (strict full weeks)
    Any day the AI omitted is inserted as a rest/revision placeholder.
    """
    boundaries = _get_week_boundaries(len(weeks))

    for w_idx, week in enumerate(weeks):
        week_start, week_end = boundaries[w_idx]

        days = week.get("days", [])

        # Build a lookup: date_str -> day_dict from AI output
        existing_dates: dict[str, dict] = {}
        for d in days:
            date_str = d.get("date", "")
            if date_str:
                existing_dates[date_str] = d

        # Walk every calendar day in this week's boundary
        complete_days = []
        current = week_start
        while current <= week_end:
            date_str = current.isoformat()
            if date_str in existing_dates:
                # Use the AI's day but ensure the 'day' name is correct
                day_obj = existing_dates[date_str].copy()
                day_obj["day"] = DAY_NAMES[current.weekday()]  # force correct name
                complete_days.append(day_obj)
            else:
                # Missing day — insert a placeholder
                is_weekend = current.weekday() >= 5
                complete_days.append({
                    "day": DAY_NAMES[current.weekday()],
                    "date": date_str,
                    "tasks": [{
                        "time": "Flexible",
                        "subject": "Break" if is_weekend else "Revision",
                        "task": "Rest day 😴" if is_weekend else "Review this week's topics & practice",
                        "duration_hours": 0.5 if is_weekend else 1.0,
                        "priority": "low",
                    }],
                })
            current += timedelta(days=1)

        week["days"] = complete_days

        # Rewrite week label based on the authoritative boundary dates
        try:
            week["week_label"] = (
                f"Week {week.get('week', w_idx + 1)}: "
                f"{week_start.strftime('%b %d')} – {week_end.strftime('%b %d, %Y')}"
            )
        except Exception:
            pass

    return weeks


def _auto_create_tasks_from_plan(user_id: str, plan_data: list[dict]):
    """Extract tasks from the multi-week AI plan and create them in the tasks table."""
    subjects = get_subjects(user_id)
    subject_map = {s["subject_name"].lower(): s["subject_id"] for s in subjects}

    # Delete old auto-generated tasks (pending ones only)
    db = get_supabase_client()
    try:
        db.table("tasks").delete().eq("user_id", user_id).eq("status", "Pending").execute()
    except Exception:
        pass

    for week in plan_data:
        days = week.get("days", [])
        for day in days:
            day_date = day.get("date", "")
            tasks = day.get("tasks", [])
            for task in tasks:
                subject_name = task.get("subject", "")
                task_name = task.get("task", "")
                duration = task.get("duration_hours", 1.0)

                # Skip breaks
                if subject_name.lower() in ["break", "rest", "revision break", "short break"]:
                    continue

                # Match subject
                subject_id = subject_map.get(subject_name.lower())
                if not subject_id:
                    # Try partial match
                    for key, sid in subject_map.items():
                        if key in subject_name.lower() or subject_name.lower() in key:
                            subject_id = sid
                            break

                if subject_id and task_name:
                    create_task(
                        user_id=user_id,
                        subject_id=subject_id,
                        task_name=task_name,
                        due_date=day_date,
                        estimated_hours=float(duration),
                    )


# ── Plan Retrieval ────────────────────────────────────────────

def get_study_plans(user_id: str) -> list[dict]:
    """Return all study plans for a user, newest first."""
    db = get_supabase_client()
    result = (
        db.table("study_plans")
        .select("*")
        .eq("user_id", user_id)
        .order("generated_date", desc=True)
        .execute()
    )
    return result.data or []


def get_latest_plan(user_id: str) -> dict | None:
    """Return the most recent study plan."""
    db = get_supabase_client()
    result = (
        db.table("study_plans")
        .select("*")
        .eq("user_id", user_id)
        .order("generated_date", desc=True)
        .limit(1)
        .execute()
    )
    return result.data[0] if result.data else None
