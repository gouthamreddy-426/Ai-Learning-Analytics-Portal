"""
Dashboard page — the student's home screen after login.
Shows key metrics, progress overview, and quick actions.
"""

import streamlit as st
from analytics.progress_metrics import (
    get_subject_progress,
    get_task_stats,
    get_weekly_task_stats,
    get_overall_progress,
)
from analytics.charts import (
    task_completion_pie,
    subject_progress_bar,
    overall_progress_gauge,
)
from backend.subject_manager import get_subjects
from backend.task_manager import get_pending_tasks
from backend.exam_manager import get_all_exams
from utils.helpers import format_date


def render():
    """Render the main dashboard."""
    user = st.session_state.get("user", {})
    user_id = user.get("user_id", "")

    # ── Header ────────────────────────────────────────────────
    # Pop the flag so the special welcome only shows once
    is_first_login = st.session_state.pop("is_first_login", False)

    if is_first_login:
        greeting = f"🎉 Welcome, {user.get('name', 'Student')}!"
        subtitle = "Your account is ready. Start by enrolling in a subject below!"
    else:
        greeting = f"👋 Welcome back, {user.get('name', 'Student')}!"
        subtitle = "Here\u2019s your learning overview for today."

    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, #00C2A815, #4CC9F015);
            border: 1px solid #00C2A830;
            border-radius: 16px;
            padding: 2rem 2.5rem;
            margin-bottom: 1.5rem;
        ">
            <h1 style="margin:0; font-size:1.8rem;">
                {greeting}
            </h1>
            <p style="color:#8B949E; margin-top:0.5rem; font-size:1rem;">
                {subtitle}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Metric Cards ──────────────────────────────────────────
    subjects = get_subjects(user_id)
    task_stats = get_task_stats(user_id)
    weekly = get_weekly_task_stats(user_id)
    overall = get_overall_progress(user_id)

    c1, c2, c3, c4, c5 = st.columns(5)
    _card(c1, "📚", "Subjects", str(len(subjects)), "#6C63FF")
    _card(c2, "✅", "Tasks Done", f"{task_stats['completed']}/{task_stats['total']}", "#00D68F")
    _card(c3, "📅", "This Week", f"{weekly['completed']}/{weekly['total']}", "#FFAA00")
    _card(c4, "🏆", "Overall", f"{overall:.0f}%", "#FF6584")

    # Exam performance metric
    all_exams = get_all_exams(user_id)
    completed_exams = [e for e in all_exams if e.get("status") == "completed"]
    avg_score = round(sum(e.get("final_score", 0) for e in completed_exams) / len(completed_exams), 1) if completed_exams else 0
    _card(c5, "🎓", "Avg Exam", f"{avg_score}%", "#4CC9F0")

    st.markdown("---")

    # ── Charts Row ────────────────────────────────────────────
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("📊 Task Completion")
        if task_stats["total"] > 0:
            fig = task_completion_pie(task_stats["completed"], task_stats["pending"])
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No tasks created yet. Add tasks to see your completion stats!")

    with col_right:
        st.subheader("📈 Subject Progress")
        progress = get_subject_progress(user_id)
        if progress:
            names = [p["subject_name"] for p in progress]
            pcts = [p["progress_pct"] for p in progress]
            fig = subject_progress_bar(names, pcts)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Enroll in subjects to track your progress!")

    st.markdown("---")

    # ── Overall Progress Gauge ────────────────────────────────
    st.subheader("🎯 Overall Learning Progress")
    gauge = overall_progress_gauge(overall)
    st.plotly_chart(gauge, use_container_width=True)

    # ── Pending Tasks Quick View ──────────────────────────────
    st.markdown("---")
    st.subheader("⏳ Upcoming Tasks")
    pending = get_pending_tasks(user_id)
    if pending:
        for t in pending[:5]:
            st.markdown(
                f"""
                <div style="
                    background: #1A1A2E;
                    border-left: 4px solid #FFAA00;
                    border-radius: 8px;
                    padding: 0.8rem 1.2rem;
                    margin-bottom: 0.6rem;
                ">
                    <strong>{t['task_name']}</strong>
                    <span style="color:#8888AA; float:right;">
                        Due: {t.get('due_date', 'N/A')} · {t.get('estimated_hours', 1)}h
                    </span>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.success("No pending tasks — you're all caught up! 🎉")

    # ── Exam Performance ─────────────────────────────────────
    st.markdown("---")
    st.subheader("🎓 Exam Performance")
    attempted_exams = [e for e in all_exams if e.get("status") in ("completed", "failed")]
    if attempted_exams:
        for ex in attempted_exams:
            fs = ex.get("final_score", 0)
            rs = ex.get("raw_score", 0)
            pen = ex.get("penalty_pct", 0)
            cert = ex.get("certificate", False)
            is_failed = ex.get("status") == "failed"
            sc = "#00D68F" if fs >= 80 else "#FFAA00" if fs >= 50 else "#FF3D71"
            # Find subject name
            sname = "Unknown"
            for s in subjects:
                if s["subject_id"] == ex.get("subject_id"):
                    sname = s["subject_name"]
                    break
            if cert:
                badge = ' <span style="background:#FFD70020;color:#FFD700;padding:1px 8px;border-radius:20px;font-size:0.65rem;font-weight:700;border:1px solid #FFD70040;">🏆 Certificate</span>'
            elif is_failed:
                badge = ' <span style="background:#FF6B6B20;color:#FF6B6B;padding:1px 8px;border-radius:20px;font-size:0.65rem;font-weight:700;border:1px solid #FF6B6B40;">🔄 Retake</span>'
            else:
                badge = ""
            st.markdown(
                f'<div style="background:linear-gradient(135deg,#1A1A2E,#20243A);'
                f'border-left:4px solid {sc};border-radius:12px;'
                f'padding:0.7rem 1rem;margin-bottom:0.4rem;">'
                f'<div style="display:flex;justify-content:space-between;align-items:center;">'
                f'<div>'
                f'<span style="font-weight:700;">{sname}</span>{badge}'
                f'<div style="font-size:0.72rem;color:#8888AA;margin-top:2px;">'
                f'Raw: {rs:.1f}% · Penalty: -{pen:.0f}%</div>'
                f'</div>'
                f'<span style="font-size:1.5rem;font-weight:800;color:{sc};">{fs:.1f}%</span>'
                f'</div></div>',
                unsafe_allow_html=True,
            )
    else:
        pending_exams = [e for e in all_exams if e.get("status") in ("ready", "overdue")]
        if pending_exams:
            st.warning(f"You have {len(pending_exams)} exam(s) waiting — head to the Exams page!")
        else:
            st.info("No exams completed yet. Complete all modules in a subject to unlock its final exam!")


# ── Helper: Metric Card ──────────────────────────────────────

def _card(col, icon: str, label: str, value: str, color: str):
    """Render a styled metric card in a column."""
    col.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, {color}18, {color}08);
            border: 1px solid {color}30;
            border-radius: 14px;
            padding: 1.2rem 1.4rem;
            text-align: center;
        ">
            <div style="font-size:2rem;">{icon}</div>
            <div style="font-size:1.6rem; font-weight:700; color:{color};">{value}</div>
            <div style="color:#8888AA; font-size:0.85rem; margin-top:0.2rem;">{label}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
