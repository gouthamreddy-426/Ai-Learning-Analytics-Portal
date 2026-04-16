"""
Subjects page — enroll in subjects with exam deadlines and manage enrollments.
"""

import streamlit as st
from datetime import datetime, timedelta
from backend.subject_manager import enroll_subject, get_subjects, delete_subject
from backend.module_generator import generate_and_save_modules, get_modules
from utils.constants import DIFFICULTY_LEVELS


def render():
    """Render the subject enrollment page."""
    user = st.session_state.get("user", {})
    user_id = user.get("user_id", "")

    st.markdown(
        '<h1 style="background:linear-gradient(135deg,#6C63FF,#43E97B);'
        '-webkit-background-clip:text;-webkit-text-fill-color:transparent;">'
        '📚 Subject Enrollment</h1>',
        unsafe_allow_html=True,
    )
    st.caption("Add subjects you want to study. AI will generate customised learning modules automatically.")

    # ── Enroll New Subject ────────────────────────────────────
    with st.expander("➕ Enroll in a New Subject", expanded=True):
        with st.form("enroll_form", clear_on_submit=True):
            col1, col2 = st.columns([3, 1])
            with col1:
                subject_name = st.text_input("Subject Name", placeholder="e.g. Machine Learning")
            with col2:
                difficulty = st.selectbox("Difficulty", DIFFICULTY_LEVELS, index=1)

            col3, col4 = st.columns(2)
            with col3:
                max_deadline = datetime.now().date() + timedelta(days=60)
                exam_date = st.date_input(
                    "📅 Exam / Deadline Date",
                    value=datetime.now().date() + timedelta(days=30),
                    min_value=datetime.now().date(),
                    max_value=max_deadline,
                    help="Deadline must be within 2 months from today.",
                )
            with col4:
                st.markdown("")
                st.markdown("")
                st.info("💡 The deadline must be within **2 months** from today. The AI will create a study plan based on this deadline.")

            submitted = st.form_submit_button("Enroll & Generate Modules", use_container_width=True)

        if submitted:
            if not subject_name.strip():
                st.error("Please enter a subject name.")
            elif exam_date and (exam_date - datetime.now().date()).days > 60:
                st.error("⚠️ The subject deadline must be within 2 months from today. Please select a shorter deadline.")
            else:
                with st.spinner("Enrolling and generating AI modules…"):
                    try:
                        subject = enroll_subject(
                            user_id,
                            subject_name.strip(),
                            difficulty,
                            exam_date=exam_date.isoformat() if exam_date else None,
                        )
                        if subject:
                            modules = generate_and_save_modules(
                                subject["subject_id"], subject_name.strip(), difficulty
                            )
                            st.success(
                                f"✅ Enrolled in **{subject_name}** with "
                                f"{len(modules)} learning modules generated!"
                            )
                            st.rerun()
                        else:
                            st.error("Failed to enroll. Please try again.")
                    except Exception as e:
                        st.error(f"Error during enrollment: {e}")

    st.markdown("---")

    # ── Enrolled Subjects ─────────────────────────────────────
    st.subheader("📖 Your Subjects")
    subjects = get_subjects(user_id)

    if not subjects:
        st.info("You haven't enrolled in any subjects yet. Start by adding one above!")
        return

    for subj in subjects:
        # Wrap get_modules in try/except to handle connection pool errors
        try:
            modules = get_modules(subj["subject_id"])
        except Exception:
            modules = []

        completed = sum(1 for m in modules if m.get("is_completed"))
        total = len(modules)
        pct = round(completed / total * 100) if total else 0
        diff_colors = {"Easy": "#43E97B", "Medium": "#FFAA00", "Hard": "#FF3D71"}
        color = diff_colors.get(subj.get("difficulty_level", "Medium"), "#6C63FF")

        # Calculate days remaining
        exam_str = subj.get("exam_date", "")
        days_left_text = ""
        if exam_str:
            try:
                exam_dt = datetime.fromisoformat(str(exam_str))
                delta = (exam_dt.date() - datetime.now().date()).days
                if delta > 0:
                    days_left_text = f"📅 {delta} days left"
                elif delta == 0:
                    days_left_text = "🔥 Exam TODAY!"
                else:
                    days_left_text = "✅ Exam passed"
            except Exception:
                pass

        # Use columns for the subject card layout
        card_col, btn_col = st.columns([5, 1])
        with card_col:
            st.markdown(
                f'<div style="background:linear-gradient(135deg,#1A1A2E,#25254B);'
                f'border-left:4px solid {color};border-radius:12px;'
                f'padding:1.2rem 1.5rem;margin-bottom:0.3rem;">'
                f'<div style="display:flex;justify-content:space-between;align-items:center;">'
                f'<div>'
                f'<h3 style="margin:0;font-size:1.2rem;">{subj["subject_name"]}</h3>'
                f'<span style="background:{color}22;color:{color};'
                f'padding:2px 10px;border-radius:20px;font-size:0.75rem;">'
                f'{subj.get("difficulty_level","Medium")}</span>'
                f' <span style="color:#36A2EB;font-size:0.8rem;">{days_left_text}</span>'
                f'</div>'
                f'<div style="text-align:right;">'
                f'<div style="font-size:1.4rem;font-weight:700;color:{color};">{pct}%</div>'
                f'<div style="color:#8888AA;font-size:0.8rem;">{completed}/{total} modules</div>'
                f'</div></div></div>',
                unsafe_allow_html=True,
            )
        with btn_col:
            st.markdown("")
            if st.button("🗑️ Remove", key=f"del_{subj['subject_id']}"):
                delete_subject(subj["subject_id"])
                st.success(f"Removed {subj['subject_name']}")
                st.rerun()
