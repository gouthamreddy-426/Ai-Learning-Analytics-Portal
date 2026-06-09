"""
Login & Signup page.
"""

import streamlit as st
from backend.auth import signup, login



def render():
    """Render the authentication page with login and signup tabs."""

    # ── Centered card ─────────────────────────────────────────
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(
            """
            <div style="text-align:center; margin-bottom:2rem;">
                <span style="font-size:3.5rem;">🎓</span>
                <h1 style="
                    background: linear-gradient(135deg, #6C63FF, #FF6584);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    font-size: 1.55rem;
                    margin-bottom: 0.25rem;
                    line-height: 1.3;
                    letter-spacing: 0.5px;
                ">AI ENABLED STUDENT LEARNING AND PERFORMANCE IMPROVEMENTAL PORTAL</h1>
                <p style="color:#8888AA; font-size:1rem;">
                    AI-powered study companion for smarter learning
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        tab_login, tab_signup = st.tabs(["🔑 Login", "✨ Sign Up"])

        # ── Login Tab ─────────────────────────────────────────
        with tab_login:
            with st.form("login_form", clear_on_submit=False):
                email = st.text_input("Email", placeholder="student@example.com")
                password = st.text_input("Password", type="password", placeholder="••••••••")
                submitted = st.form_submit_button("Login", use_container_width=True)

            if submitted:
                if not email or not password:
                    st.error("Please fill in all fields.")
                else:
                    with st.spinner("Authenticating…"):
                        try:
                            result = login(email.strip(), password)
                        except Exception as e:
                            result = {"success": False, "error": f"Connection error: {e}"}
                    if result["success"]:
                        # Detect first login (user just signed up in this session)
                        fresh_email = st.session_state.pop("fresh_signup_email", None)
                        is_first = (
                            fresh_email is not None
                            and fresh_email.lower() == result["user"]["email"].lower()
                        )
                        st.session_state["user"]         = result["user"]
                        st.session_state["logged_in"]    = True
                        st.session_state["is_first_login"] = is_first
                        # ── Persist login in browser cookie ────────────

                        if is_first:
                            st.success(f"🎉 Welcome, {result['user']['name']}! Your account is all set.")
                        else:
                            st.success(f"👋 Welcome back, {result['user']['name']}!")
                        st.rerun()
                    else:
                        st.error(result["error"])

        # ── Signup Tab ────────────────────────────────────────
        with tab_signup:
            with st.form("signup_form", clear_on_submit=True):
                name = st.text_input("Full Name", placeholder="John Doe")
                email_s = st.text_input("Email", placeholder="student@example.com", key="signup_email")
                password_s = st.text_input("Password", type="password", placeholder="Min 6 characters", key="signup_pw")
                password_c = st.text_input("Confirm Password", type="password", placeholder="••••••••", key="confirm_pw")
                submitted_s = st.form_submit_button("Create Account", use_container_width=True)

            if submitted_s:
                if not name or not email_s or not password_s:
                    st.error("Please fill in all fields.")
                elif len(password_s) < 6:
                    st.error("Password must be at least 6 characters.")
                elif password_s != password_c:
                    st.error("Passwords do not match.")
                else:
                    with st.spinner("Creating your account…"):
                        try:
                            result = signup(name.strip(), email_s.strip(), password_s)
                        except Exception as e:
                            result = {"success": False, "error": f"Connection error: {e}"}
                    if result["success"]:
                        # Remember this email so we can detect their first login
                        st.session_state["fresh_signup_email"] = email_s.strip()
                        st.success(
                            "🎉 Account created successfully! "
                            "Please go to the **Login** tab to sign in."
                        )
                    else:
                        st.error(result["error"])
