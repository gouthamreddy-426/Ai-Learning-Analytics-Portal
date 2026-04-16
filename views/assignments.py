"""
Assignments page — generate and view AI-powered assignments.
"""

import streamlit as st
from backend.subject_manager import get_subjects
from backend.assignment_generator import (
    generate_and_save_assignment,
    get_assignments,
    get_all_assignments_for_user,
    delete_assignment,
)


def render():
    """Render the assignments page."""
    user = st.session_state.get("user", {})
    user_id = user.get("user_id", "")

    st.markdown(
        """
        <h1 style="
            background: linear-gradient(135deg, #FF6584, #FFAA00);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        ">📝 AI Assignments</h1>
        """,
        unsafe_allow_html=True,
    )
    st.caption("Generate practice assignments powered by AI for any enrolled subject.")

    subjects = get_subjects(user_id)
    if not subjects:
        st.info("Enroll in subjects first to generate assignments.")
        return

    # ── Generate New Assignment ───────────────────────────────
    with st.expander("🤖 Generate New Assignment", expanded=True):
        subject_map = {s["subject_id"]: s["subject_name"] for s in subjects}
        selected_id = st.selectbox(
            "Select Subject",
            options=list(subject_map.keys()),
            format_func=lambda sid: subject_map[sid],
            key="assign_subj",
        )
        if st.button("⚡ Generate Assignment", use_container_width=True):
            with st.spinner("AI is crafting your assignment…"):
                result = generate_and_save_assignment(selected_id, subject_map[selected_id])
                if result:
                    st.success("Assignment generated successfully!")
                    st.rerun()
                else:
                    st.error("Failed to generate assignment. Please try again.")

    st.markdown("---")

    # ── View Assignments ──────────────────────────────────────
    st.subheader("📄 Your Assignments")

    all_assignments = get_all_assignments_for_user(user_id)
    if not all_assignments:
        st.info("No assignments yet. Generate one above!")
        return

    for a in all_assignments:
        subj_name = a.get("subject_name", "Unknown Subject")
        created = a.get("created_at", "")[:10]
        with st.expander(f"📎 {subj_name} — {created}"):
            st.markdown(a.get("assignment_text", ""))
            if st.button("🗑️ Delete", key=f"del_assign_{a['assignment_id']}"):
                delete_assignment(a["assignment_id"])
                st.success("Assignment deleted.")
                st.rerun()
