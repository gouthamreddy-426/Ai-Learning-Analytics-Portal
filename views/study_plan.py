"""
Study Plan page — premium calendar grid UI.
Week selector dropdown → 7-day grid → clickable topics navigate to Modules.
Uses st.container(border=True) so ALL content (header, tasks, footer) lives
inside one real bordered Streamlit container.
"""

import json
import re
import streamlit as st
from datetime import datetime
from backend.study_plan_generator import generate_and_save_plan, get_latest_plan
from backend.task_manager import get_tasks
from backend.subject_manager import get_subjects
from backend.module_generator import get_modules


# ── Constants ────────────────────────────────────────────────────────────────
WEEK_COLORS = ["#00C2A8","#4CC9F0","#F59E0B","#F85149","#A8DADC","#7B2D8B","#0096C7","#43E97B"]
PRIO_ICON   = {"high": "🔴", "medium": "🟡", "low": "🟢"}
BREAK_SUBJS = {"break", "rest", "revision break", "short break", "revision"}


def _is_break(t: dict) -> bool:
    return t.get("subject", "").strip().lower() in BREAK_SUBJS

def _strip_prefix(text: str) -> str:
    return re.sub(
        r'^(study|practice|review|revise|recap|complete|finish|module\s*\d+\s*:?)\s*',
        '', text, flags=re.IGNORECASE
    ).strip()

def _navigate(subject: str, task_desc: str):
    st.session_state["goto_subject_name"]   = subject
    st.session_state["goto_module_keyword"] = _strip_prefix(task_desc)
    st.session_state["current_page"]        = "Modules"
    st.rerun()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# DAY CARD — everything inside one st.container(border=True)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def _render_day(day_data: dict, week_color: str, ci: int, di: int):
    today     = datetime.now().date()
    day_name  = day_data.get("day", "")
    date_str  = day_data.get("date", "")
    tasks     = day_data.get("tasks", [])

    is_today = is_past = False
    date_lbl = date_str
    try:
        if date_str:
            d = datetime.fromisoformat(date_str).date()
            is_today = d == today
            is_past  = d < today
            date_lbl = d.strftime("%b %d")
    except Exception:
        pass

    study = [t for t in tasks if not _is_break(t)]
    brks  = [t for t in tasks if _is_break(t)]
    hrs   = sum(t.get("duration_hours", 0) for t in tasks)

    # Badge
    if is_today:
        hc = week_color
        bdg = f' <span style="background:{week_color};color:#0E1117;padding:0 5px;border-radius:20px;font-size:0.55rem;font-weight:800;">TODAY</span>'
    elif is_past:
        hc = "#484F58"
        bdg = ' <span style="background:#30363D;color:#484F58;padding:0 5px;border-radius:20px;font-size:0.55rem;font-weight:700;">PAST</span>'
    else:
        hc = "#C9D1D9"
        bdg = ""

    # ── Container — this wraps EVERYTHING ─────────────────────
    with st.container(border=True):

        # ── Top: Day name + date ──────────────────────────────
        st.markdown(
            f'<div style="margin:-0.2rem 0 0.35rem 0;">'
            f'<span style="font-weight:800;font-size:0.82rem;color:{hc};">{day_name}</span>{bdg}<br>'
            f'<span style="font-size:0.65rem;color:#555E6B;">{date_lbl}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

        # ── Middle: Tasks / Rest ──────────────────────────────
        if not study and not brks:
            st.markdown(
                '<div style="text-align:center;padding:0.5rem 0;">'
                '<div style="font-size:1.2rem;color:#484F58;">😴</div>'
                '<div style="font-size:0.68rem;color:#484F58;">Rest Day</div>'
                '</div>',
                unsafe_allow_html=True,
            )
        else:
            for ti, task in enumerate(study):
                subj = task.get("subject", "")
                desc = task.get("task", "")
                dur  = task.get("duration_hours", 1.0)
                pri  = task.get("priority", "low")
                ico  = PRIO_ICON.get(pri, "🟢")
                lbl  = desc if len(desc) <= 28 else desc[:26] + "…"

                if st.button(
                    f"{ico} {lbl}",
                    key=f"t_{di}_{ci}_{ti}",
                    use_container_width=True,
                    help=f"{desc}\n📚 {subj} · ⏱ {dur}h",
                ):
                    _navigate(subj, desc)

            for b in brks:
                st.markdown(
                    f'<div style="color:#555E6B;font-size:0.66rem;padding:1px 0;">☕ {b.get("task","Break")}</div>',
                    unsafe_allow_html=True,
                )

        # ── Bottom: Stats — inside the same container ─────────
        st.markdown(
            f'<div style="border-top:1px solid #2D3548;margin-top:0.25rem;padding-top:0.25rem;'
            f'display:flex;justify-content:space-between;align-items:center;">'
            f'<span style="background:rgba(76,201,240,0.12);color:#4CC9F0;'
            f'padding:1px 6px;border-radius:20px;font-size:0.6rem;font-weight:600;'
            f'border:1px solid rgba(76,201,240,0.25);">⏱ {hrs:.1f}h</span>'
            f'<span style="background:rgba(0,194,168,0.12);color:#00C2A8;'
            f'padding:1px 6px;border-radius:20px;font-size:0.6rem;font-weight:600;'
            f'border:1px solid rgba(0,194,168,0.25);">{len(study)} task(s)</span>'
            f'</div>',
            unsafe_allow_html=True,
        )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MAIN RENDER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def render():
    user    = st.session_state.get("user", {})
    user_id = user.get("user_id", "")

    # ── Scoped CSS ────────────────────────────────────────────
    st.markdown(
        """
        <style>
        /* Day containers — style the bordered container wrapper */
        .day-grid [data-testid="stVerticalBlockBorderWrapper"] {
            background: linear-gradient(180deg, #1C2130 0%, #171B26 100%) !important;
            border: 1px solid #2D3548 !important;
            border-radius: 14px !important;
            transition: transform 0.15s ease, box-shadow 0.15s ease !important;
        }
        .day-grid [data-testid="stVerticalBlockBorderWrapper"]:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 18px rgba(0,194,168,0.1) !important;
            border-color: #3D4B65 !important;
        }
        /* Compact task buttons inside day cards */
        .day-grid [data-testid="stButton"] > button {
            font-size: 0.72rem !important;
            padding: 4px 7px !important;
            height: auto !important;
            min-height: 0 !important;
            white-space: normal !important;
            text-align: left !important;
            line-height: 1.3 !important;
            border-radius: 8px !important;
            margin-bottom: 2px !important;
            background: rgba(0,194,168,0.06) !important;
            border: 1px solid rgba(0,194,168,0.12) !important;
            color: #C9D1D9 !important;
        }
        .day-grid [data-testid="stButton"] > button:hover {
            background: rgba(0,194,168,0.18) !important;
            border-color: rgba(0,194,168,0.4) !important;
            color: #00C2A8 !important;
        }
        /* Module coverage columns */
        .mod-coverage [data-testid="stColumn"] {
            background: #1A1A2E !important;
            border: 1px solid #2D3548 !important;
            border-radius: 10px !important;
            padding: 0.35rem 0.45rem !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<h1 style="background:linear-gradient(135deg,#00C2A8,#4CC9F0);'
        '-webkit-background-clip:text;-webkit-text-fill-color:transparent;">'
        '🗓️ AI Study Plan</h1>',
        unsafe_allow_html=True,
    )
    st.caption("Click any task to jump to that module. Overdue tasks auto-reschedule.")

    # ── Auto-adjust overdue tasks ────────────────────────────
    from backend.task_manager import auto_adjust_overdue_tasks
    adjusted = auto_adjust_overdue_tasks(user_id)
    if adjusted > 0:
        st.markdown(
            f'<div style="background:rgba(0,194,168,0.08);border:1px solid rgba(0,194,168,0.3);'
            f'border-radius:10px;padding:0.6rem 1rem;margin-bottom:0.8rem;font-size:0.85rem;">'
            f'🔄 <span style="color:#00C2A8;font-weight:600;">{adjusted} overdue task(s)</span>'
            f' auto-rescheduled.</div>',
            unsafe_allow_html=True,
        )

    # ── Deadline summary ─────────────────────────────────────
    try:
        subjects = get_subjects(user_id)
    except Exception:
        subjects = []

    today = datetime.now().date()

    if subjects:
        cols = st.columns(min(len(subjects), 4))
        for i, subj in enumerate(subjects[:4]):
            with cols[i]:
                exam_date = subj.get("exam_date", "")
                days_left, uc = "—", "#8888AA"
                if exam_date:
                    try:
                        delta = (datetime.fromisoformat(str(exam_date)).date() - today).days
                        days_left = f"{delta}d"
                        uc = "#FF3D71" if delta <= 7 else "#FFAA00" if delta <= 14 else "#43E97B"
                    except Exception:
                        pass
                try:
                    mods = get_modules(subj["subject_id"])
                    mt   = f"{sum(1 for m in mods if m.get('is_completed'))}/{len(mods)} modules"
                except Exception:
                    mt = ""
                dc = {"Easy":"#43E97B","Medium":"#FFAA00","Hard":"#FF3D71"}.get(subj.get("difficulty_level","Medium"),"#6C63FF")
                st.markdown(
                    f'<div style="background:#1A1A2E;border:1px solid {dc}40;'
                    f'border-radius:10px;padding:0.8rem;text-align:center;">'
                    f'<div style="font-size:0.82rem;font-weight:600;">{subj["subject_name"]}</div>'
                    f'<div style="font-size:1.4rem;font-weight:700;color:{uc};">{days_left}</div>'
                    f'<span style="font-size:0.68rem;color:{dc};">{subj.get("difficulty_level","")}</span>'
                    f' · <span style="font-size:0.68rem;color:#8888AA;">{mt}</span></div>',
                    unsafe_allow_html=True,
                )
        st.markdown("")

    # ── Generate panel ───────────────────────────────────────
    try:
        existing_plan = get_latest_plan(user_id)
    except Exception:
        existing_plan = None

    with st.expander("⚙️ Generate New Plan", expanded=not bool(existing_plan)):
        study_hours = st.slider("Available study hours per day", 1.0, 12.0, 3.0, 0.5)
        st.info("💡 The AI builds a **complete plan covering ALL your modules** across multiple weeks.")
        if st.button("🤖 Generate Complete Study Plan", use_container_width=True):
            with st.spinner("Building your full study plan…"):
                try:
                    result = generate_and_save_plan(user_id, study_hours=study_hours)
                    if result:
                        st.success("✅ Plan generated & tasks auto-created!")
                        st.rerun()
                    else:
                        st.error("Failed. Make sure you have subjects with incomplete modules.")
                except Exception as e:
                    st.error(f"Error: {e}")

    st.markdown("---")

    # ── Load plan ────────────────────────────────────────────
    latest = existing_plan or get_latest_plan(user_id) if not existing_plan else existing_plan
    if not latest:
        st.info("No study plans yet. Generate your first plan above!")
        return

    generated = latest.get("generated_date", "")[:10]

    try:
        pc = latest.get("plan_content", "")
        plan_data = json.loads(pc) if isinstance(pc, str) else pc
    except (json.JSONDecodeError, TypeError):
        st.markdown(str(latest.get("plan_content", "")))
        return

    weeks_data = []
    if isinstance(plan_data, dict) and "weeks" in plan_data:
        weeks_data = plan_data["weeks"]
    elif isinstance(plan_data, list):
        if plan_data and "week" in plan_data[0] and "days" in plan_data[0]:
            weeks_data = plan_data
        elif plan_data and "day" in plan_data[0]:
            weeks_data = [{"week": 1, "week_label": "Week 1", "days": plan_data}]
    if not weeks_data:
        st.warning("Plan data could not be parsed.")
        return

    # ── Stats ────────────────────────────────────────────────
    try:
        all_tasks = get_tasks(user_id)
    except Exception:
        all_tasks = []

    tt = len(all_tasks)
    ct = sum(1 for t in all_tasks if t.get("status") == "Completed")
    pt = tt - ct
    pct = round(ct / tt * 100) if tt else 0
    pc_col = "#00D68F" if pct >= 80 else "#FFAA00" if pct >= 40 else "#FF3D71"

    st.markdown(
        f'<div style="background:linear-gradient(135deg,#6C63FF12,#FF658412);'
        f'border:1px solid #6C63FF30;border-radius:14px;'
        f'padding:1rem 1.5rem;margin-bottom:1rem;'
        f'display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;">'
        f'<div>'
        f'<div style="font-size:1.05rem;font-weight:700;">📅 Your Study Calendar</div>'
        f'<div style="color:#8888AA;font-size:0.82rem;">Generated {generated} · {len(weeks_data)} week(s)</div>'
        f'</div>'
        f'<div style="text-align:right;">'
        f'<div style="font-size:2rem;font-weight:800;color:{pc_col};line-height:1;">{pct}%</div>'
        f'<div style="color:#8888AA;font-size:0.78rem;">{ct}/{tt} tasks done</div>'
        f'</div></div>',
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📅 Weeks", len(weeks_data))
    c2.metric("📋 Tasks", tt)
    c3.metric("✅ Done", ct)
    c4.metric("⏳ Pending", pt)
    st.progress(pct / 100)
    st.markdown("")

    # ── Week selector ────────────────────────────────────────
    current_week_idx = 0
    found = False
    for wi, wk in enumerate(weeks_data):
        if found:
            break
        for day in wk.get("days", []):
            try:
                if datetime.fromisoformat(day.get("date", "")).date() >= today:
                    current_week_idx = wi
                    found = True
                    break
            except Exception:
                pass

    wk_labels = []
    for wi, wk in enumerate(weeks_data):
        wn = wk.get("week", wi + 1)
        wl = wk.get("week_label", f"Week {wn}")
        ds = wk.get("days", [])
        nt = sum(len(d.get("tasks", [])) for d in ds)
        nh = sum(t.get("duration_hours", 0) for d in ds for t in d.get("tasks", []))
        bg = "  🔵 CURRENT" if wi == current_week_idx else ""
        wk_labels.append(f"📅  {wl}{bg}  —  {len(ds)} days · {nt} tasks · {nh:.0f}h")

    sel = st.selectbox(
        "📅  Select Week",
        options=range(len(wk_labels)),
        format_func=lambda i: wk_labels[i],
        index=current_week_idx,
        key="sp_week_sel",
    )

    week     = weeks_data[sel]
    wnum     = week.get("week", sel + 1)
    wcolor   = WEEK_COLORS[(wnum - 1) % len(WEEK_COLORS)]
    wlabel   = week.get("week_label", f"Week {wnum}")
    days     = week.get("days", [])

    st.markdown(
        f'<div style="background:linear-gradient(135deg,{wcolor}20,{wcolor}08);'
        f'border-left:4px solid {wcolor};border-radius:12px;'
        f'padding:0.7rem 1.2rem;margin:0.8rem 0 1rem 0;">'
        f'<span style="font-weight:700;color:{wcolor};font-size:1rem;">📅 {wlabel}</span>'
        f'<span style="color:#555E6B;font-size:0.82rem;margin-left:1rem;">'
        f'{len(days)} days · click any task to jump to module</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

    if not days:
        st.info("No days found for this week.")
        return

    # ── Day grid — wrapped in .day-grid for scoped CSS ───────
    row1 = days[:4]
    row2 = days[4:]

    st.markdown('<div class="day-grid">', unsafe_allow_html=True)

    if row1:
        cols1 = st.columns(len(row1))
        for ci, (col, dd) in enumerate(zip(cols1, row1)):
            with col:
                _render_day(dd, wcolor, ci, sel * 7 + ci)

    if row2:
        cols2 = st.columns(len(row2))
        for ci, (col, dd) in enumerate(zip(cols2, row2)):
            with col:
                _render_day(dd, wcolor, ci + 4, sel * 7 + ci + 4)

    st.markdown('</div>', unsafe_allow_html=True)

    # ── Module Coverage ──────────────────────────────────────
    if subjects:
        st.markdown("---")
        st.markdown("### 📊 Module Coverage")

        for subj in subjects:
            try:
                mods = get_modules(subj["subject_id"])
            except Exception:
                mods = []
            if not mods:
                continue

            done  = sum(1 for m in mods if m.get("is_completed"))
            total = len(mods)
            spct  = round(done / total * 100) if total else 0
            pcol  = "#00D68F" if spct >= 80 else "#FFAA00" if spct >= 40 else "#FF3D71"
            dc    = {"Easy":"#43E97B","Medium":"#FFAA00","Hard":"#FF3D71"}.get(subj.get("difficulty_level","Medium"),"#6C63FF")

            # Use st.container(border=True) for module coverage too
            with st.container(border=True):
                st.markdown(
                    f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.4rem;">'
                    f'<div>'
                    f'<span style="font-weight:700;font-size:0.92rem;">{subj["subject_name"]}</span>'
                    f' <span style="background:{dc}18;color:{dc};padding:1px 8px;border-radius:20px;'
                    f'font-size:0.65rem;font-weight:600;border:1px solid {dc}30;">{subj.get("difficulty_level","")}</span>'
                    f'</div>'
                    f'<div style="display:flex;align-items:center;gap:0.5rem;">'
                    f'<span style="background:rgba(0,194,168,0.1);color:#00C2A8;padding:2px 8px;'
                    f'border-radius:20px;font-size:0.68rem;font-weight:600;'
                    f'border:1px solid rgba(0,194,168,0.2);">{done}/{total} done</span>'
                    f'<span style="font-size:1.2rem;font-weight:800;color:{pcol};">{spct}%</span>'
                    f'</div></div>',
                    unsafe_allow_html=True,
                )

                # Module list inside the same container
                st.markdown('<div class="mod-coverage">', unsafe_allow_html=True)
                mc = st.columns(min(total, 3))
                for mi, m in enumerate(mods):
                    with mc[mi % min(total, 3)]:
                        ic = "✅" if m.get("is_completed") else "⬜"
                        cl = "#00D68F" if m.get("is_completed") else "#8888AA"
                        st.markdown(
                            f'<div style="font-size:0.78rem;color:{cl};padding:2px 0;">{ic} {m["module_title"]}</div>',
                            unsafe_allow_html=True,
                        )
                st.markdown('</div>', unsafe_allow_html=True)
