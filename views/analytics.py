"""
Analytics page — charts and metrics for learning progress.
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
    weekly_trend_line,
    overall_progress_gauge,
    module_completion_grouped,
)
from backend.task_manager import get_tasks


def render():
    """Render the analytics dashboard."""
    user = st.session_state.get("user", {})
    user_id = user.get("user_id", "")

    st.markdown(
        """
        <h1 style="
            background: linear-gradient(135deg, #FF6584, #6C63FF);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        ">📈 Learning Analytics</h1>
        """,
        unsafe_allow_html=True,
    )
    st.caption("Comprehensive view of your study performance and progress.")

    # ── Key Metrics Row ───────────────────────────────────────
    progress_data = get_subject_progress(user_id)
    task_stats = get_task_stats(user_id)
    weekly = get_weekly_task_stats(user_id)
    overall = get_overall_progress(user_id)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📚 Subjects", len(progress_data))
    c2.metric("✅ Tasks Completed", task_stats["completed"])
    c3.metric("📊 Completion Rate", f"{task_stats['completion_rate']:.0f}%")
    c4.metric("🏆 Overall Progress", f"{overall:.0f}%")

    st.markdown("---")

    # ── Row 1: Pie + Bar ──────────────────────────────────────
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🍩 Task Completion")
        if task_stats["total"] > 0:
            fig = task_completion_pie(task_stats["completed"], task_stats["pending"])
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Create tasks to see completion analytics.")

    with col2:
        st.subheader("📊 Subject Progress")
        if progress_data:
            names = [p["subject_name"] for p in progress_data]
            pcts = [p["progress_pct"] for p in progress_data]
            fig = subject_progress_bar(names, pcts)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Enroll in subjects to see progress.")

    st.markdown("---")

    # ── Row 2: Module Completion + Weekly Trend ───────────────
    col3, col4 = st.columns(2)

    with col3:
        st.subheader("📖 Module Completion")
        if progress_data:
            fig = module_completion_grouped(progress_data)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No module data available yet.")

    with col4:
        st.subheader("📈 Weekly Trend")
        # Build a simple daily task completion count for the current week
        tasks = get_tasks(user_id)
        from utils.helpers import week_date_range
        from datetime import timedelta
        start, end = week_date_range()
        days_labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        daily_counts = [0] * 7
        for t in tasks:
            if t.get("status") == "Completed" and t.get("due_date"):
                try:
                    from datetime import date
                    td = date.fromisoformat(t["due_date"])
                    if start <= td <= end:
                        day_idx = td.weekday()
                        daily_counts[day_idx] += 1
                except ValueError:
                    pass

        fig = weekly_trend_line(days_labels, daily_counts)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ── Overall Gauge ─────────────────────────────────────────
    st.subheader("🎯 Overall Learning Progress")
    gauge = overall_progress_gauge(overall)
    st.plotly_chart(gauge, use_container_width=True)

    # ── Subject Detail Table ──────────────────────────────────
    if progress_data:
        st.markdown("---")
        st.subheader("📋 Detailed Subject Breakdown")
        try:
            import pandas as pd
            df = pd.DataFrame(progress_data)
            rename_map = {
                "subject_name": "Subject",
                "difficulty": "Difficulty",
                "total_modules": "Total Modules",
                "completed_modules": "Completed",
                "progress_pct": "Progress %",
            }
            df = df.rename(columns=rename_map)
            # Only select columns that actually exist in the dataframe
            desired_cols = ["Subject", "Difficulty", "Total Modules", "Completed", "Progress %"]
            available_cols = [c for c in desired_cols if c in df.columns]
            st.dataframe(df[available_cols], use_container_width=True, hide_index=True)
        except Exception as e:
            st.error(f"Could not display table: {e}")
