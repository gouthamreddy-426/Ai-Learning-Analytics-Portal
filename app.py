"""
app.py — Main entry point for the Student Learning Portal.
Run with: streamlit run app.py
"""

import base64
from pathlib import Path
import streamlit as st
from utils.constants import APP_TITLE, APP_ICON, APP_LAYOUT, NAV_ITEMS
from utils.session_manager import clear_session

# ── Load logo as base64 ───────────────────────────────────────
def _load_logo_b64() -> str:
    logo_path = Path(__file__).parent / "assets" / "logo.png"
    if logo_path.exists():
        return base64.b64encode(logo_path.read_bytes()).decode()
    return ""

LOGO_B64 = _load_logo_b64()

# ── Page Config ───────────────────────────────────────────────
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout=APP_LAYOUT,
    initial_sidebar_state="expanded",
)

# ── Global CSS ────────────────────────────────────────────────
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"], .stApp {
        font-family: 'Inter', sans-serif !important;
        background-color: #0E1117;
        color: #FAFAFA;
    }

    /* Hide Streamlit chrome */
    #MainMenu, footer, header { visibility: hidden; }
    .stDeployButton { display: none !important; }

    /* Main content area — fixed left offset so it never shifts */
    .main .block-container {
        padding: 2rem 2.5rem 3rem;
        max-width: 1200px;
    }
    section[data-testid="stMain"] {
        position: relative !important;
        flex: 1 1 auto !important;
        min-width: 0 !important;
    }

    /* ══════════════════════════════════════════════════════
       SIDEBAR  —  fixed width, no scroll, everything flush
    ══════════════════════════════════════════════════════ */

    [data-testid="stSidebar"] {
        background: #1C1F26 !important;
        border-right: 1px solid #252B36 !important;
        width: 240px !important;
        min-width: 240px !important;
        max-width: 240px !important;
        flex-shrink: 0 !important;
        position: relative !important;
    }

    /* Kill ALL overflow — sidebar never scrolls */
    [data-testid="stSidebar"] > div:first-child {
        overflow: hidden !important;
        padding: 0 !important;
    }

    /* Collapse every default gap/margin inside sidebar */
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"],
    [data-testid="stSidebar"] .stVerticalBlock {
        gap: 3px !important;
        padding: 0 !important;
    }
    [data-testid="stSidebar"] .element-container {
        margin: 0 !important;
        padding: 0 !important;
    }
    [data-testid="stSidebar"] .block-container {
        padding: 4px 0 0 0 !important;
        margin: 0 !important;
    }

    /* ── Nav buttons — compact, straight-left-aligned ── */
    [data-testid="stSidebar"] .stButton {
        margin: 0 !important;
        padding: 0 !important;
        width: 100% !important;
    }
    /* Inactive nav button */
    [data-testid="stSidebar"] .stButton > button {
        background: transparent !important;
        border: none !important;
        border-left: 3px solid transparent !important;
        border-radius: 0 !important;
        color: #8B949E !important;
        text-align: left !important;
        padding: 0.65rem 1rem 0.65rem 0.85rem !important;
        width: 100% !important;
        font-size: 0.875rem !important;
        font-weight: 500 !important;
        font-family: 'Inter', sans-serif !important;
        line-height: 1.5 !important;
        height: auto !important;
        min-height: 0 !important;
        box-shadow: none !important;
        outline: none !important;
        transition: background 0.15s, color 0.15s, border-color 0.15s !important;
    }
    /* Active nav button (type=primary) */
    [data-testid="stSidebar"] .stButton > button[kind="primary"] {
        background: rgba(0,194,168,0.1) !important;
        border-left: 3px solid #00C2A8 !important;
        color: #00C2A8 !important;
        font-weight: 600 !important;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(0,194,168,0.07) !important;
        color: #00C2A8 !important;
        border-left-color: rgba(0,194,168,0.35) !important;
    }
    [data-testid="stSidebar"] .stButton > button[kind="primary"]:hover {
        background: rgba(0,194,168,0.18) !important;
        border-left-color: #00C2A8 !important;
    }
    [data-testid="stSidebar"] .stButton > button:focus,
    [data-testid="stSidebar"] .stButton > button:active {
        box-shadow: none !important;
        outline: none !important;
    }

    /* ══════════════════════════════════════════════════════
       REST OF APP STYLES
    ══════════════════════════════════════════════════════ */

    /* Buttons */
    .stButton > button {
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-family: 'Inter', sans-serif !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #00C2A8, #00A896) !important;
        color: #0E1117 !important;
        border: none !important;
    }
    .stButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(0,194,168,0.2) !important;
    }

    /* Inputs */
    .stTextInput > div > div > input,
    .stSelectbox > div > div,
    .stDateInput > div > div > input {
        background: #252B36 !important;
        border-color: #30363D !important;
        color: #FAFAFA !important;
        border-radius: 8px !important;
    }

    /* Forms */
    [data-testid="stForm"] {
        background: #1C1F26 !important;
        border: 1px solid #252B36 !important;
        border-radius: 12px !important;
        padding: 1.5rem !important;
    }

    /* Expanders */
    .stExpander {
        background: #1C1F26 !important;
        border: 1px solid #252B36 !important;
        border-radius: 12px !important;
    }
    .stExpander > details > summary { font-weight: 600 !important; }

    /* Metrics */
    [data-testid="stMetric"] {
        background: #1C1F26 !important;
        border: 1px solid #252B36 !important;
        border-radius: 12px !important;
        padding: 1rem !important;
    }
    [data-testid="stMetricValue"] { color: #00C2A8 !important; }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background: #1C1F26 !important;
        border-radius: 10px !important;
        padding: 4px !important;
        gap: 4px !important;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px !important;
        color: #8B949E !important;
        font-weight: 500 !important;
    }
    .stTabs [aria-selected="true"] {
        background: rgba(0,194,168,0.15) !important;
        color: #00C2A8 !important;
    }

    /* Progress */
    .stProgress > div > div {
        background: linear-gradient(90deg, #00C2A8, #4CC9F0) !important;
        border-radius: 10px !important;
    }
    .stProgress > div {
        background: #252B36 !important;
        border-radius: 10px !important;
    }

    /* Dataframe */
    .stDataFrame { border-radius: 12px !important; overflow: hidden !important; }

    /* Alerts */
    .stAlert { border-radius: 10px !important; }

    /* Scrollbar */
    ::-webkit-scrollbar { width: 5px; }
    ::-webkit-scrollbar-track { background: #1C1F26; }
    ::-webkit-scrollbar-thumb { background: #30363D; border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: #00C2A8; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Session Initialisation ────────────────────────────────────
from utils.session_manager import load_session

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "Dashboard"

# Restore session from local file if not already logged in
if not st.session_state["logged_in"]:
    saved_user = load_session()
    if saved_user:
        st.session_state["logged_in"] = True
        st.session_state["user"]       = saved_user

# ── Auth Gate ─────────────────────────────────────────────────
if not st.session_state["logged_in"]:
    from views.login import render as render_login
    render_login()
    st.stop()



# ── Sidebar ───────────────────────────────────────────────────
selected_page = st.session_state["current_page"]
user          = st.session_state.get("user", {})
initials      = "".join(w[0].upper() for w in user.get("name", "S").split()[:2])

with st.sidebar:

    # ── 1. Branding block ─────────────────────────────────────
    logo_html = (
        f'<img src="data:image/png;base64,{LOGO_B64}" '
        f'style="width:34px;height:34px;border-radius:8px;flex-shrink:0;object-fit:cover;">'
        if LOGO_B64 else
        '<div style="background:linear-gradient(135deg,#00C2A8,#4CC9F0);'
        'border-radius:8px;width:34px;height:34px;flex-shrink:0;'
        'display:flex;align-items:center;justify-content:center;font-size:1rem;">🎓</div>'
    )
    st.markdown(
        f"""
        <div style="padding:1.1rem 1rem 1rem;border-bottom:1px solid #252B36;">
            <div style="display:flex;align-items:center;gap:0.65rem;">
                {logo_html}
                <div>
                    <div style="font-weight:800;font-size:0.95rem;color:#FAFAFA;
                        line-height:1.2;letter-spacing:-0.01em;">EduPulse</div>
                    <div style="font-size:0.65rem;color:#00C2A8;font-weight:600;
                        letter-spacing:0.04em;">AI-POWERED LEARNING</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── 2. Spacer between branding and nav buttons ─────────
    st.markdown('<div style="padding-top:0.6rem;"></div>', unsafe_allow_html=True)

    # ── 3. Nav items — ALL rendered as st.button (no layout shift) ───
    #   Active page  → type="primary"  (CSS gives it teal highlight)
    #   Inactive page → type="secondary" (CSS gives it grey style)
    for page_name, icon in NAV_ITEMS.items():
        is_active = (selected_page == page_name)
        btn_type  = "primary" if is_active else "secondary"

        if st.button(
            f"{icon}  {page_name}",
            key=f"nav_{page_name}",
            type=btn_type,
            use_container_width=True,
        ):
            st.session_state["current_page"] = page_name
            selected_page = page_name
            st.rerun()

    # ── 4. User info — normal flow, at end of list ────────────
    st.markdown(
        f"""
        <div style="
            border-top:1px solid #252B36;
            margin-top:0.6rem;
            padding:0.7rem 1rem;
            display:flex;align-items:center;gap:0.6rem;">
            <div style="background:linear-gradient(135deg,#00C2A8,#4CC9F0);
                border-radius:50%;width:26px;height:26px;flex-shrink:0;
                display:flex;align-items:center;justify-content:center;
                font-weight:700;font-size:0.7rem;color:#0E1117;">{initials}</div>
            <div style="overflow:hidden;flex:1;min-width:0;">
                <div style="font-weight:600;font-size:0.78rem;color:#FAFAFA;
                    white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">
                    {user.get('name', 'Student')}</div>
                <div style="font-size:0.65rem;color:#8B949E;
                    white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">
                    {user.get('email', '')}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── Page Router ───────────────────────────────────────────────
page_map = {
    "Dashboard":    "views.dashboard",
    "Subjects":     "views.subjects",
    "Modules":      "views.modules",
    "Assignments":  "views.assignments",
    "Cheat Sheets": "views.cheatsheets",
    "Tasks":        "views.tasks",
    "Study Plan":   "views.study_plan",
    "Exams":        "views.exams",
    "Analytics":    "views.analytics",
    "Profile":      "views.profile",
}


import importlib
module_path = page_map.get(selected_page, "views.dashboard")
page_module = importlib.import_module(module_path)
page_module.render()
