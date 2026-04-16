"""
Tasks page — view auto-generated tasks from study plans, track completion.
Tasks are created automatically when a study plan is generated.
Auto-adjusts overdue tasks to upcoming days on page load.
"""

import streamlit as st
from datetime import datetime
from backend.subject_manager import get_subjects
from backend.task_manager import (
    get_tasks,
    get_pending_tasks,
    update_task_status,
    auto_adjust_overdue_tasks,
)


def _status_badge(status: str) -> str:
    """Return a colored HTML badge for a task status."""
    if status == "Completed":
        return (
            '<span style="background:rgba(0,194,168,0.15);color:#00C2A8;'
            'padding:2px 10px;border-radius:20px;font-size:0.75rem;'
            'font-weight:600;border:1px solid rgba(0,194,168,0.3);">✅ Completed</span>'
        )
    return (
        '<span style="background:rgba(245,158,11,0.15);color:#F59E0B;'
        'padding:2px 10px;border-radius:20px;font-size:0.75rem;'
        'font-weight:600;border:1px solid rgba(245,158,11,0.3);">⏳ Pending</span>'
    )


def render():
    """Render the task tracking page."""
    user = st.session_state.get("user", {})
    user_id = user.get("user_id", "")

    st.markdown(
        '<h1 style="background:linear-gradient(135deg,#00C2A8,#4CC9F0);'
        '-webkit-background-clip:text;-webkit-text-fill-color:transparent;">'
        '✅ Task Tracker</h1>',
        unsafe_allow_html=True,
    )
    st.caption(
        "Tasks are auto-generated from your AI Study Plan. "
        "Overdue tasks are auto-rescheduled. Mark modules complete to auto-update tasks!"
    )

    # ── Auto-adjust overdue tasks ──────────────────────────────
    rescheduled = auto_adjust_overdue_tasks(user_id)
    if rescheduled > 0:
        st.info(
            f"🔄 **{rescheduled} overdue task(s)** were automatically rescheduled "
            f"to upcoming days to keep your plan on track."
        )

    subjects = get_subjects(user_id)
    tasks = get_tasks(user_id)

    if not tasks:
        st.info(
            "📋 No tasks yet! Go to **Study Plan** → Generate a plan, "
            "and tasks will be automatically created for you."
        )
        return

    # Build lookup maps
    subj_lookup = {s["subject_id"]: s["subject_name"] for s in subjects}

    # ── Task Stats ────────────────────────────────────────────
    total = len(tasks)
    completed = sum(1 for t in tasks if t.get("status") == "Completed")
    pending = total - completed
    pct = round(completed / total * 100) if total else 0

    today = datetime.now().date()
    overdue = sum(
        1 for t in tasks
        if t.get("status") == "Pending" and t.get("due_date", "9999") < today.isoformat()
    )

    col1, col2, col3, col4 = st.columns(4)
    stat_card = lambda c, val, label, color: c.markdown(
        f'<div style="background:#1C1F26;border:1px solid #252B36;border-radius:12px;'
        f'padding:1rem;text-align:center;border-top:3px solid {color};">'
        f'<div style="font-size:2rem;font-weight:700;color:{color};">{val}</div>'
        f'<div style="color:#8B949E;font-size:0.82rem;margin-top:2px;">{label}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )
    stat_card(col1, total,     "Total Tasks",  "#4CC9F0")
    stat_card(col2, completed, "Completed",    "#00C2A8")
    stat_card(col3, pending,   "Pending",      "#F59E0B")
    ov_color = "#F85149" if overdue > 0 else "#00C2A8"
    stat_card(col4, overdue,   "Overdue",       ov_color)

    st.progress(pct / 100)
    st.caption(f"📊 Overall progress: **{pct}%** complete")
    st.markdown("---")

    # ── Filter ────────────────────────────────────────────────
    from collections import defaultdict
    by_date = defaultdict(list)
    for t in tasks:
        by_date[t.get("due_date", "Unknown")].append(t)

    filter_choice = st.radio(
        "Filter tasks:",
        ["📋 All", "📅 Today", "⏳ Pending", "✅ Completed", "🔴 Overdue"],
        horizontal=True,
        label_visibility="collapsed",
    )

    any_visible = False

    for date_str in sorted(by_date.keys()):
        day_tasks = by_date[date_str]

        # Apply filter
        if filter_choice == "📅 Today":
            day_tasks = [t for t in day_tasks if t.get("due_date", "") == today.isoformat()]
        elif filter_choice == "⏳ Pending":
            day_tasks = [t for t in day_tasks if t.get("status") == "Pending"]
        elif filter_choice == "✅ Completed":
            day_tasks = [t for t in day_tasks if t.get("status") == "Completed"]
        elif filter_choice == "🔴 Overdue":
            day_tasks = [
                t for t in day_tasks
                if t.get("status") == "Pending" and t.get("due_date", "9999") < today.isoformat()
            ]

        if not day_tasks:
            continue

        any_visible = True

        # Date header
        try:
            dt = datetime.fromisoformat(str(date_str)).date()
            is_today_date = (dt == today)
            is_past = (dt < today)
            day_label = dt.strftime("%A, %b %d %Y")
        except Exception:
            day_label = date_str
            is_today_date = False
            is_past = False

        if is_today_date:
            date_color = "#00C2A8"
            day_label += "  🔵 TODAY"
        elif is_past:
            date_color = "#F85149"
        else:
            date_color = "#4CC9F0"

        st.markdown(
            f'<p style="color:{date_color};font-weight:700;font-size:0.9rem;'
            f'margin:1rem 0 0.4rem;letter-spacing:0.02em;">📅 {day_label}</p>',
            unsafe_allow_html=True,
        )

        for t in day_tasks:
            is_done = t.get("status") == "Completed"
            left_color = "#00C2A8" if is_done else "#F59E0B"
            subj_name = subj_lookup.get(t.get("subject_id"), "—")
            opacity = "opacity:0.55;" if is_done else ""

            col_task, col_btn = st.columns([5, 1])
            with col_task:
                st.markdown(
                    f'<div style="background:#1C1F26;border-left:3px solid {left_color};'
                    f'border-radius:8px;padding:0.6rem 1rem;margin-bottom:0.3rem;{opacity}">'
                    f'<div style="display:flex;justify-content:space-between;align-items:center;">'
                    f'<strong style="font-size:0.9rem;">{t["task_name"]}</strong>'
                    f'{_status_badge(t.get("status","Pending"))}'
                    f'</div>'
                    f'<span style="color:#8B949E;font-size:0.78rem;">'
                    f'📚 {subj_name} · ⏱ {t.get("estimated_hours", 1)}h'
                    f'</span></div>',
                    unsafe_allow_html=True,
                )
            with col_btn:
                if not is_done:
                    if st.button("✅ Done", key=f"done_{t['task_id']}"):
                        update_task_status(t["task_id"], "Completed")
                        st.rerun()
                else:
                    if st.button("↩️ Undo", key=f"undo_{t['task_id']}"):
                        update_task_status(t["task_id"], "Pending")
                        st.rerun()

    if not any_visible:
        st.info("No tasks match this filter.")
