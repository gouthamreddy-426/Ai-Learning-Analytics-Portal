"""
Exams page — Final subject exams with AI-generated questions,
penalty scoring, retake flow, and EDUPULSE certificate issuance.
"""

import json
import streamlit as st
from datetime import datetime, date
from backend.subject_manager import get_subjects
from backend.module_generator import get_modules
from backend.exam_manager import (
    get_exam, get_all_exams, compute_exam_status,
    generate_exam, submit_exam, reset_exam_for_retake,
    PASS_THRESHOLD,
)


def render():
    user    = st.session_state.get("user", {})
    user_id = user.get("user_id", "")

    # ── Header ───────────────────────────────────────────────
    st.markdown(
        '<h1 style="background:linear-gradient(135deg,#F59E0B,#FF6B6B);'
        '-webkit-background-clip:text;-webkit-text-fill-color:transparent;">'
        '🎓 Final Exams</h1>',
        unsafe_allow_html=True,
    )

    # ── Instructions panel ───────────────────────────────────
    with st.expander("📋 Exam Rules & Instructions", expanded=False):
        st.markdown(f"""
### 🎯 How the Final Exam Works

| Step | Description |
|------|-------------|
| 1️⃣ **Complete Modules** | Finish all modules of a subject to unlock the exam early! |
| 2️⃣ **Exam Unlocks** | The exam unlocks when **all modules are completed** OR on the **exam date**. |
| 3️⃣ **Take the Exam** | Answer all AI-generated multiple-choice questions carefully. |
| 4️⃣ **Get Results** | Your exam is auto-evaluated instantly with detailed explanations. |
| 5️⃣ **Certificate** | Score **{PASS_THRESHOLD:.0f}% or above** to earn an **EDUPULSE Certificate**! 🏆 |
| 🔄 **Retake** | Score below {PASS_THRESHOLD:.0f}%? No worries — retake the exam until you pass! |

### ⚠️ Penalty System
- If you **don't take the exam on its scheduled date**, a penalty applies:
  - **−2% per day** past the exam date (capped at −50%)
  - Example: 5 days late → 10% deducted from your score
- **Exam statuses:**

| Status | Meaning |
|--------|---------|
| 📚 **Keep Studying** | Exam day hasn't arrived yet and modules are incomplete. |
| 🟢 **Ready** | All modules complete OR exam day arrived — start your exam! |
| ⚠️ **Overdue** | Exam day has passed. Take it ASAP to minimise penalty! |
| 🔄 **Retake Required** | You scored below {PASS_THRESHOLD:.0f}%. Generate a new exam! |
| ✅ **Completed** | You passed and earned your certificate! |

> **Tip:** Complete all modules AND take the exam on time for the best score!
        """)

    # ── Load subjects ────────────────────────────────────────
    try:
        subjects = get_subjects(user_id)
    except Exception:
        subjects = []

    if not subjects:
        st.info("No subjects enrolled yet. Add subjects first!")
        return

    today = date.today()

    # ── Exam cards ───────────────────────────────────────────
    st.markdown("### 📝 Your Exams")

    for subj in subjects:
        sid   = subj["subject_id"]
        sname = subj["subject_name"]
        diff  = subj.get("difficulty_level", "Medium")
        edate = subj.get("exam_date", "")

        # Module progress
        try:
            mods = get_modules(sid)
        except Exception:
            mods = []
        total_mods = len(mods)
        done_mods  = sum(1 for m in mods if m.get("is_completed"))
        all_done   = total_mods > 0 and done_mods == total_mods

        # Exam record
        exam_rec = get_exam(user_id, sid)
        status, label, penalty = compute_exam_status(edate, exam_rec, all_done)

        # Status colour
        status_colors = {
            "not_ready":  "#F59E0B",
            "ready":      "#00C2A8",
            "overdue":    "#FF3D71",
            "completed":  "#00D68F",
            "failed":     "#FF6B6B",
        }
        scol = status_colors.get(status, "#8888AA")

        # Difficulty colour
        dc = {"Easy": "#43E97B", "Medium": "#FFAA00", "Hard": "#FF3D71"}.get(diff, "#6C63FF")

        # Days info
        days_txt = ""
        if edate:
            try:
                delta = (datetime.fromisoformat(str(edate)).date() - today).days
                days_txt = f"{delta}d left" if delta > 0 else "Today!" if delta == 0 else f"{abs(delta)}d overdue"
            except Exception:
                pass

        with st.container(border=True):
            # ── Card header ──────────────────────────────────
            h1, h2 = st.columns([3, 1])
            with h1:
                st.markdown(
                    f'<div style="font-size:1.05rem;font-weight:700;">{sname}'
                    f' <span style="background:{dc}18;color:{dc};padding:1px 8px;border-radius:20px;'
                    f'font-size:0.65rem;font-weight:600;border:1px solid {dc}30;">{diff}</span></div>'
                    f'<div style="font-size:0.78rem;color:#8888AA;margin-top:2px;">'
                    f'📅 {edate or "No date"} · {days_txt} · {done_mods}/{total_mods} modules done</div>',
                    unsafe_allow_html=True,
                )
            with h2:
                st.markdown(
                    f'<div style="text-align:right;">'
                    f'<span style="background:{scol}18;color:{scol};padding:3px 12px;border-radius:20px;'
                    f'font-size:0.75rem;font-weight:700;border:1px solid {scol}40;">{label}</span></div>',
                    unsafe_allow_html=True,
                )

            # Module progress bar
            if total_mods > 0:
                st.progress(done_mods / total_mods)

            # ── Completed exam (passed) — show results ────────
            if status == "completed" and exam_rec:
                _show_results(exam_rec, sname)

            # ── Failed exam — show results + retake option ────
            elif status == "failed" and exam_rec:
                _show_failed_results(exam_rec, sname, sid, user_id, mods, diff, penalty)

            # ── Ready / Overdue — show exam or generate ───────
            elif status in ("ready", "overdue"):
                if penalty > 0:
                    st.warning(f"⚠️ Late penalty: **−{penalty:.0f}%** will be deducted from your score.")

                if exam_rec and exam_rec.get("questions"):
                    # Exam already generated — take it
                    _take_exam(exam_rec, penalty, sname)
                else:
                    # Generate exam
                    if not all_done:
                        st.info(f"📚 Complete all {total_mods} modules first to unlock the exam.")
                    else:
                        module_titles = [m["module_title"] for m in mods]
                        if st.button(f"🤖 Generate Final Exam", key=f"gen_{sid}", use_container_width=True):
                            with st.spinner("AI is creating your exam…"):
                                result = generate_exam(user_id, sid, sname, module_titles, diff)
                                if result:
                                    st.success("✅ Exam generated! Refresh to start.")
                                    st.rerun()
                                else:
                                    st.error("Failed to generate exam. Try again.")

            # ── Not ready ────────────────────────────────────
            elif status == "not_ready":
                if not all_done:
                    remaining = total_mods - done_mods
                    st.markdown(
                        f'<div style="color:#F59E0B;font-size:0.82rem;padding:0.3rem 0;">'
                        f'📚 Complete {remaining} more module(s) to unlock the exam.</div>',
                        unsafe_allow_html=True,
                    )


def _take_exam(exam_rec: dict, penalty: float, subject_name: str):
    """Render the exam-taking interface."""
    exam_id = exam_rec["exam_id"]

    try:
        questions = exam_rec.get("questions", "[]")
        if isinstance(questions, str):
            questions = json.loads(questions)
    except Exception:
        st.error("Could not load exam questions.")
        return

    if not questions:
        st.error("No questions found in this exam.")
        return

    st.markdown("---")
    st.markdown(
        f'<div style="font-size:0.95rem;font-weight:700;color:#4CC9F0;margin-bottom:0.5rem;">'
        f'📝 {subject_name} — Final Exam ({len(questions)} questions)</div>',
        unsafe_allow_html=True,
    )

    # Initialize answers in session state
    ans_key = f"exam_answers_{exam_id}"
    if ans_key not in st.session_state:
        st.session_state[ans_key] = {}

    for i, q in enumerate(questions):
        module_tag = q.get("module", "")
        st.markdown(
            f'<div style="color:#8888AA;font-size:0.68rem;margin-top:0.5rem;">Module: {module_tag}</div>',
            unsafe_allow_html=True,
        )
        choice = st.radio(
            f"**Q{i+1}.** {q['question']}",
            options=q.get("options", []),
            key=f"q_{exam_id}_{i}",
            index=None,
        )
        if choice:
            st.session_state[ans_key][str(i)] = choice[0]  # "A", "B", "C", "D"

    st.markdown("---")
    answered = len(st.session_state.get(ans_key, {}))
    st.caption(f"Answered: {answered}/{len(questions)}")

    if st.button("📨 Submit Exam", key=f"submit_{exam_id}", use_container_width=True,
                  type="primary", disabled=answered < len(questions)):
        user_answers = st.session_state.get(ans_key, {})
        result = submit_exam(exam_id, user_answers, questions, penalty)
        st.session_state.pop(ans_key, None)
        st.session_state[f"exam_result_{exam_id}"] = result
        st.rerun()


def _show_failed_results(exam_rec: dict, subject_name: str, subject_id: str,
                         user_id: str, mods: list, difficulty: str, penalty: float):
    """Display failed exam results and offer retake."""
    raw     = exam_rec.get("raw_score", 0)
    pen     = exam_rec.get("penalty_pct", 0)
    final   = exam_rec.get("final_score", 0)
    correct = exam_rec.get("correct_answers", 0)
    total   = exam_rec.get("total_questions", 0)
    exam_id = exam_rec.get("exam_id", "")

    st.markdown("---")

    # Stats row
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📊 Raw Score", f"{raw:.1f}%")
    c2.metric("⏰ Penalty", f"−{pen:.0f}%")
    c3.metric("🎯 Final Score", f"{final:.1f}%")
    c4.metric("✅ Correct", f"{correct}/{total}")

    # Failed message with motivational design
    needed = PASS_THRESHOLD - final
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, #FF3D7110, #FF6B6B08);
            border: 1px solid #FF3D7130;
            border-radius: 16px;
            padding: 1.5rem 2rem;
            text-align: center;
            margin: 1rem 0;
        ">
            <div style="font-size:2.5rem;margin-bottom:0.3rem;">📝</div>
            <div style="font-size:1.8rem;font-weight:800;color:#FF6B6B;">{final:.1f}%</div>
            <div style="color:#8888AA;font-size:0.9rem;margin:0.5rem 0;">
                You need <strong style="color:#FFD700;">{needed:.1f}% more</strong> to pass and earn your certificate.
            </div>
            <div style="
                background: linear-gradient(135deg, #00C2A815, #4CC9F015);
                border: 1px solid #00C2A830;
                border-radius: 12px;
                padding: 1rem;
                margin-top: 1rem;
                text-align: left;
            ">
                <div style="font-size:0.85rem;font-weight:700;color:#4CC9F0;margin-bottom:0.5rem;">
                    💡 Tips for your retake:
                </div>
                <div style="font-size:0.8rem;color:#C0C0D0;line-height:1.6;">
                    • Review the detailed answers below to understand what you got wrong<br>
                    • Revisit the module materials for topics you struggled with<br>
                    • Take your time — there's no limit on retakes!<br>
                    • A fresh set of AI-generated questions will be created for you
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Retake button
    if st.button("🔄 Retake Exam — Generate New Questions", key=f"retake_{exam_id}",
                  use_container_width=True, type="primary"):
        with st.spinner("Preparing your retake exam…"):
            # Delete the old failed attempt
            deleted = reset_exam_for_retake(exam_id)
            if deleted:
                # Generate new questions
                module_titles = [m["module_title"] for m in mods]
                result = generate_exam(user_id, subject_id, subject_name, module_titles, difficulty)
                if result:
                    st.success("✅ New exam generated! Starting fresh…")
                    st.rerun()
                else:
                    st.error("Failed to generate new exam. Please try again.")
            else:
                st.error("Could not reset exam. Please try again.")

    # Detailed results toggle
    with st.expander("📋 View Detailed Answers — Learn from your mistakes", expanded=False):
        _render_detailed_answers(exam_rec)


def _show_results(exam_rec: dict, subject_name: str):
    """Display passed exam results and EDUPULSE certificate."""
    raw     = exam_rec.get("raw_score", 0)
    penalty = exam_rec.get("penalty_pct", 0)
    final   = exam_rec.get("final_score", 0)
    correct = exam_rec.get("correct_answers", 0)
    total   = exam_rec.get("total_questions", 0)
    cert    = exam_rec.get("certificate", False)

    # Score colour
    sc = "#00D68F" if final >= 80 else "#FFAA00" if final >= 50 else "#FF3D71"

    st.markdown("---")

    # Stats row
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📊 Raw Score", f"{raw:.1f}%")
    c2.metric("⏰ Penalty", f"−{penalty:.0f}%")
    c3.metric("🎯 Final Score", f"{final:.1f}%")
    c4.metric("✅ Correct", f"{correct}/{total}")

    # Big score display
    st.markdown(
        f'<div style="text-align:center;padding:0.8rem 0;">'
        f'<div style="font-size:2.5rem;font-weight:900;color:{sc};">{final:.1f}%</div>'
        f'<div style="color:#8888AA;font-size:0.85rem;">'
        f'{"🏆 Certificate Earned!" if cert else "Score below 80% — No certificate"}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # ── EDUPULSE Certificate ─────────────────────────────────
    if cert:
        user = st.session_state.get("user", {})
        name = user.get("name", "Student")
        attempted = exam_rec.get("attempted_at", "")
        try:
            cert_date = datetime.fromisoformat(attempted).strftime("%B %d, %Y")
        except Exception:
            cert_date = datetime.now().strftime("%B %d, %Y")

        # Grade calculation
        if final >= 95:
            grade, grade_color = "A+", "#FFD700"
        elif final >= 90:
            grade, grade_color = "A", "#FFD700"
        elif final >= 85:
            grade, grade_color = "A-", "#C0C0C0"
        else:
            grade, grade_color = "B+", "#CD7F32"

        st.markdown(
            f"""
            <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Inter:wght@400;600;700&family=Orbitron:wght@700;900&display=swap" rel="stylesheet">
            <div style="
                background: linear-gradient(135deg, #0a0a1a 0%, #1a1a2e 25%, #16213e 50%, #0f3460 75%, #0a0a1a 100%);
                border: 3px solid #FFD700;
                border-radius: 24px;
                padding: 2.5rem 2rem;
                text-align: center;
                margin: 1.5rem 0;
                box-shadow:
                    0 0 40px rgba(255,215,0,0.15),
                    0 0 80px rgba(255,215,0,0.05),
                    inset 0 0 60px rgba(255,215,0,0.03);
                position: relative;
                overflow: hidden;
            ">
                <!-- Decorative corner accents -->
                <div style="position:absolute;top:12px;left:12px;width:40px;height:40px;
                    border-top:2px solid #FFD70060;border-left:2px solid #FFD70060;border-radius:4px 0 0 0;"></div>
                <div style="position:absolute;top:12px;right:12px;width:40px;height:40px;
                    border-top:2px solid #FFD70060;border-right:2px solid #FFD70060;border-radius:0 4px 0 0;"></div>
                <div style="position:absolute;bottom:12px;left:12px;width:40px;height:40px;
                    border-bottom:2px solid #FFD70060;border-left:2px solid #FFD70060;border-radius:0 0 0 4px;"></div>
                <div style="position:absolute;bottom:12px;right:12px;width:40px;height:40px;
                    border-bottom:2px solid #FFD70060;border-right:2px solid #FFD70060;border-radius:0 0 4px 0;"></div>

                <!-- EDUPULSE Brand -->
                <div style="
                    font-family: 'Orbitron', sans-serif;
                    font-size: 1.6rem;
                    font-weight: 900;
                    background: linear-gradient(135deg, #FFD700, #FFA500, #FFD700);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    letter-spacing: 0.3em;
                    margin-bottom: 0.2rem;
                    text-shadow: 0 0 20px rgba(255,215,0,0.3);
                ">EDUPULSE</div>

                <div style="
                    width: 60px;
                    height: 2px;
                    background: linear-gradient(90deg, transparent, #FFD700, transparent);
                    margin: 0.5rem auto;
                "></div>

                <!-- Trophy Icon -->
                <div style="font-size:2.8rem;margin:0.5rem 0;">🏆</div>

                <!-- Certificate Title -->
                <div style="
                    font-family: 'Playfair Display', serif;
                    font-size: 0.85rem;
                    color: #FFD700;
                    letter-spacing: 0.25em;
                    text-transform: uppercase;
                    font-weight: 700;
                    margin-bottom: 0.8rem;
                ">Certificate of Achievement</div>

                <div style="
                    font-size: 0.75rem;
                    color: #8888AA;
                    font-family: 'Inter', sans-serif;
                    margin-bottom: 0.3rem;
                ">This is to certify that</div>

                <!-- Student Name -->
                <div style="
                    font-family: 'Playfair Display', serif;
                    font-size: 2rem;
                    font-weight: 900;
                    color: #FAFAFA;
                    margin: 0.3rem 0;
                    text-shadow: 0 2px 10px rgba(255,255,255,0.1);
                ">{name}</div>

                <div style="
                    color: #8888AA;
                    font-size: 0.85rem;
                    font-family: 'Inter', sans-serif;
                    margin-bottom: 0.8rem;
                ">has successfully completed the final examination in</div>

                <!-- Subject Name -->
                <div style="
                    font-family: 'Playfair Display', serif;
                    font-size: 1.5rem;
                    font-weight: 700;
                    color: #4CC9F0;
                    margin-bottom: 0.8rem;
                    text-shadow: 0 0 15px rgba(76,201,240,0.2);
                ">{subject_name}</div>

                <!-- Score & Grade -->
                <div style="
                    display: flex;
                    justify-content: center;
                    gap: 3rem;
                    margin: 1rem 0;
                ">
                    <div>
                        <div style="
                            font-family: 'Orbitron', sans-serif;
                            font-size: 1.8rem;
                            font-weight: 800;
                            color: #00D68F;
                        ">{final:.1f}%</div>
                        <div style="font-size:0.7rem;color:#8888AA;font-family:'Inter',sans-serif;">
                            Final Score</div>
                    </div>
                    <div style="width:1px;background:linear-gradient(180deg,transparent,#FFD70040,transparent);"></div>
                    <div>
                        <div style="
                            font-family: 'Orbitron', sans-serif;
                            font-size: 1.8rem;
                            font-weight: 800;
                            color: {grade_color};
                        ">{grade}</div>
                        <div style="font-size:0.7rem;color:#8888AA;font-family:'Inter',sans-serif;">
                            Grade</div>
                    </div>
                </div>

                <!-- Divider -->
                <div style="
                    border-top: 1px solid #FFD70025;
                    padding-top: 1rem;
                    margin-top: 0.8rem;
                ">
                    <div style="
                        font-size: 0.72rem;
                        color: #8888AA;
                        font-family: 'Inter', sans-serif;
                    ">
                        📅 {cert_date}
                    </div>
                    <div style="
                        font-family: 'Orbitron', sans-serif;
                        font-size: 0.55rem;
                        color: #FFD70080;
                        letter-spacing: 0.15em;
                        margin-top: 0.5rem;
                    ">POWERED BY EDUPULSE AI · VERIFIED CERTIFICATE</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Detailed results toggle
    with st.expander("📋 View Detailed Answers", expanded=False):
        _render_detailed_answers(exam_rec)


def _render_detailed_answers(exam_rec: dict):
    """Render the detailed question-by-question breakdown."""
    try:
        questions = exam_rec.get("questions", "[]")
        if isinstance(questions, str):
            questions = json.loads(questions)
        answers_raw = exam_rec.get("user_answers", "{}")
        if isinstance(answers_raw, str):
            user_answers = json.loads(answers_raw)
        else:
            user_answers = answers_raw or {}
    except Exception:
        st.error("Could not load answer details.")
        return

    for i, q in enumerate(questions):
        user_a    = user_answers.get(str(i), "—")
        correct_a = q.get("correct_answer", "")
        is_ok     = user_a.strip().upper() == correct_a.strip().upper()
        icon      = "✅" if is_ok else "❌"
        acol      = "#00D68F" if is_ok else "#FF3D71"

        st.markdown(
            f'<div style="background:#161B22;border-radius:10px;padding:0.6rem 0.8rem;'
            f'margin-bottom:0.4rem;border-left:3px solid {acol};">'
            f'<div style="font-size:0.82rem;font-weight:600;">{icon} Q{i+1}. {q["question"]}</div>'
            f'<div style="font-size:0.75rem;color:{acol};margin-top:0.2rem;">'
            f'Your: {user_a}) · Correct: {correct_a})</div>'
            f'<div style="font-size:0.72rem;color:#8888AA;margin-top:0.2rem;">'
            f'💡 {q.get("explanation", "")}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
