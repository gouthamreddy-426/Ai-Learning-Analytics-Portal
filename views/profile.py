"""
Profile page — view and update user profile.
"""

import streamlit as st
from backend.auth import get_user_profile, update_user_name
from utils.helpers import format_date
from utils.session_manager import clear_session, save_session


def render():
    """Render the profile page."""
    user = st.session_state.get("user", {})
    user_id = user.get("user_id", "")

    st.markdown(
        """
        <h1 style="
            background: linear-gradient(135deg, #9966FF, #FF6584);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        ">👤 Profile</h1>
        """,
        unsafe_allow_html=True,
    )

    # ── Profile Card ──────────────────────────────────────────
    profile = get_user_profile(user_id)
    if not profile:
        st.error("Could not load profile.")
        return

    member_since = profile.get("created_at", "")[:10]

    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, #1A1A2E, #25254B);
            border: 1px solid #6C63FF30;
            border-radius: 16px;
            padding: 2rem 2.5rem;
            text-align: center;
            margin-bottom: 2rem;
        ">
            <div style="
                width: 80px; height: 80px;
                background: linear-gradient(135deg, #6C63FF, #FF6584);
                border-radius: 50%;
                display: inline-flex;
                align-items: center;
                justify-content: center;
                font-size: 2rem;
                margin-bottom: 1rem;
            ">👤</div>
            <h2 style="margin: 0.5rem 0 0.2rem;">{profile['name']}</h2>
            <p style="color: #8888AA; margin: 0;">{profile['email']}</p>
            <p style="color: #6C63FF; font-size: 0.85rem; margin-top: 0.5rem;">
                📅 Member since {member_since}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Update Name ───────────────────────────────────────────
    st.subheader("✏️ Update Profile")
    with st.form("update_profile_form"):
        new_name = st.text_input("Display Name", value=profile["name"])
        submitted = st.form_submit_button("Save Changes", use_container_width=True)

    if submitted:
        if not new_name.strip():
            st.error("Name cannot be empty.")
        elif new_name.strip() == profile["name"]:
            st.info("No changes detected.")
        else:
            success = update_user_name(user_id, new_name.strip())
            if success:
                st.session_state["user"]["name"] = new_name.strip()
                save_session(st.session_state["user"])  # refresh cookie with updated name
                st.success("Profile updated!")
                st.rerun()
            else:
                st.error("Failed to update. Please try again.")

    # ── Account Info ──────────────────────────────────────────
    st.markdown("---")
    st.subheader("ℹ️ Account Information")
    col1, col2 = st.columns(2)
    col1.markdown(f"**User ID:** `{user_id[:8]}...`")
    col2.markdown(f"**Email:** {profile['email']}")

    # ── Logout ────────────────────────────────────────────────
    st.markdown("---")
    if st.button("🚪 Logout", use_container_width=True, type="primary"):
        clear_session()                           # delete browser cookie
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

