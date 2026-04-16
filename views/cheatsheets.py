"""
Cheat Sheets page — clean module-centric UI with subject dropdown filter.
"""

import streamlit as st
from backend.subject_manager import get_subjects
from backend.module_generator import get_modules
from backend.cheatsheet_generator import (
    generate_and_save_cheatsheet,
    get_cheatsheets,
    delete_cheatsheet,
)


def render():
    user    = st.session_state.get("user", {})
    user_id = user.get("user_id", "")

    st.markdown(
        """
        <h1 style="
            background: linear-gradient(135deg, #43E97B, #38F9D7);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.2rem;
        ">📋 AI Cheat Sheets</h1>
        """,
        unsafe_allow_html=True,
    )
    st.caption("Select a subject to browse module cheat sheets or generate new ones.")

    subjects = get_subjects(user_id)
    if not subjects:
        st.info("Enroll in subjects first to generate cheat sheets.")
        return

    # ── Subject dropdown ──────────────────────────────────────
    subject_map = {s["subject_id"]: s["subject_name"] for s in subjects}
    selected_subject_id = st.selectbox(
        "📚 Subject",
        options=list(subject_map.keys()),
        format_func=lambda sid: subject_map[sid],
        key="cs_subject_filter",
    )
    selected_subject_name = subject_map[selected_subject_id]

    st.markdown("---")

    # ── Load modules for selected subject ─────────────────────
    try:
        modules = get_modules(selected_subject_id)
    except Exception:
        modules = []

    if not modules:
        st.warning("No modules found for this subject. Generate modules from the Subjects page first.")
        return

    # ── Load ALL cheat sheets for subject once ────────────────
    all_sheets = get_cheatsheets(selected_subject_id)

    # Group sheets by module_title (key), fallback to "General"
    sheets_by_module: dict[str, list] = {}
    for cs in all_sheets:
        key = cs.get("module_title") or "__general__"
        sheets_by_module.setdefault(key, []).append(cs)

    # ── Render each module as a card ──────────────────────────
    for mod in modules:
        mod_id    = mod["module_id"]
        mod_title = mod["module_title"]
        mod_order = mod.get("module_order", "")
        is_done   = mod.get("is_completed", False)

        status_badge = (
            '<span style="background:rgba(0,214,143,0.15);color:#00D68F;'
            'padding:0.2rem 0.6rem;border-radius:20px;font-size:0.75rem;'
            'font-weight:600;border:1px solid rgba(0,214,143,0.3);">✅ Completed</span>'
            if is_done else
            '<span style="background:rgba(255,170,0,0.15);color:#FFAA00;'
            'padding:0.2rem 0.6rem;border-radius:20px;font-size:0.75rem;'
            'font-weight:600;border:1px solid rgba(255,170,0,0.3);">⏳ Pending</span>'
        )

        module_sheets = sheets_by_module.get(mod_title, [])
        sheet_count   = len(module_sheets)
        sheet_info    = (
            f'<span style="color:#38F9D7;font-size:0.8rem;font-weight:600;">'
            f'📄 {sheet_count} sheet(s)</span>'
            if sheet_count > 0 else
            '<span style="color:#555;font-size:0.8rem;">No sheet yet</span>'
        )

        # Module card header
        st.markdown(
            f"""
            <div style="
                background: linear-gradient(135deg, #1A1A2E, #16213E);
                border: 1px solid #252B3A;
                border-left: 4px solid #43E97B;
                border-radius: 12px;
                padding: 0.8rem 1.2rem;
                margin-bottom: 0.3rem;
                display: flex;
                align-items: center;
                justify-content: space-between;
            ">
                <div>
                    <span style="color:#8888AA;font-size:0.75rem;font-weight:600;
                        text-transform:uppercase;letter-spacing:0.05em;">
                        Module {mod_order}
                    </span><br>
                    <span style="color:#FAFAFA;font-size:1rem;font-weight:600;">
                        {mod_title}
                    </span>
                </div>
                <div style="display:flex;align-items:center;gap:0.8rem;">
                    {sheet_info}
                    {status_badge}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # ── Existing cheat sheets for this module ─────────────
        if module_sheets:
            for cs in module_sheets:
                created = cs.get("created_at", "")[:10]
                with st.expander(f"   📄 Cheat Sheet — Generated on {created}"):
                    st.markdown(cs.get("content", ""))
                    col_del, col_spacer = st.columns([1, 4])
                    with col_del:
                        if st.button("🗑️ Delete", key=f"del_cs_{cs['cheatsheet_id']}"):
                            delete_cheatsheet(cs["cheatsheet_id"])
                            st.success("Deleted.")
                            st.rerun()

        # ── Generate button ───────────────────────────────────
        gen_label = "⚡ Regenerate Cheat Sheet" if sheet_count > 0 else "⚡ Generate Cheat Sheet"
        col_btn, col_pad = st.columns([2, 5])
        with col_btn:
            if st.button(gen_label, key=f"gen_cs_{mod_id}", use_container_width=True):
                with st.spinner(f"Generating cheat sheet for '{mod_title}'…"):
                    result = generate_and_save_cheatsheet(
                        subject_id   = selected_subject_id,
                        subject_name = selected_subject_name,
                        module_id    = mod_id,
                        module_title = mod_title,
                    )
                    if result:
                        st.success(f"✅ Cheat sheet for **{mod_title}** ready!")
                        st.rerun()
                    else:
                        st.error("Failed to generate. Please try again.")

        st.markdown("<div style='margin-bottom:1rem;'></div>", unsafe_allow_html=True)
