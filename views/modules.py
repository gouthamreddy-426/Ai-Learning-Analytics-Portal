"""
Modules page — browse modules per subject, watch embedded videos, take tests.
"""

import re
import json
import streamlit as st
import streamlit.components.v1 as components
from backend.subject_manager import get_subjects
from backend.module_generator import (
    get_modules,
    mark_module_complete,
    mark_module_incomplete,
    generate_and_save_videos,
    get_videos,
    generate_and_save_test,
    get_test,
    save_test_result,
)


# ── Helper: sync module tasks ──────────────────────────────────
def _sync_module_tasks(user_id: str, subject_id: str, module_title: str, new_status: str):
    """Auto-mark tasks related to this module as Completed or Pending."""
    try:
        from backend.task_manager import get_tasks, update_task_status
        tasks = get_tasks(user_id)
        mod_words = {w.lower() for w in re.split(r'\W+', module_title) if len(w) > 3}
        for task in tasks:
            if task.get("status") == new_status:
                continue
            if task.get("subject_id") != subject_id:
                continue
            task_name_lower = task["task_name"].lower()
            if any(w in task_name_lower for w in mod_words):
                update_task_status(task["task_id"], new_status)
    except Exception:
        pass


# ── Helper: extract YouTube search query ──────────────────────
def _extract_search_query(video: dict) -> str:
    desc = video.get("description", "")
    if desc and "Recommended video" not in desc:
        return desc
    url = video.get("video_url", "")
    if "search_query=" in url:
        from urllib.parse import unquote_plus
        query = url.split("search_query=")[-1].split("&")[0]
        return unquote_plus(query)
    return video.get("video_title", "educational video")


# ── Helper: search a real YouTube video ID ────────────────────
def _search_youtube_video_id(query: str, exclude_ids: set = None) -> str | None:
    import requests
    from urllib.parse import quote_plus

    if exclude_ids is None:
        exclude_ids = set()

    url = f"https://www.youtube.com/results?search_query={quote_plus(query)}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            video_ids = re.findall(r'"videoId":"([a-zA-Z0-9_-]{11})"', resp.text)
            seen = set()
            unique_ids = []
            for vid in video_ids:
                if vid not in seen:
                    seen.add(vid)
                    unique_ids.append(vid)
            for vid in unique_ids:
                if vid not in exclude_ids:
                    return vid
    except Exception:
        pass
    return None


# ── Helper: embed a YouTube video ─────────────────────────────
def _embed_youtube_video(video: dict, module_id: str, video_index: int):
    query = _extract_search_query(video)
    title = video.get("video_title", "")

    video_db_id = video.get("video_id", f"{module_id}_{video_index}")
    cache_key = f"vid_cache_{video_db_id}"

    used_key = f"used_vids_{module_id}"
    if used_key not in st.session_state:
        st.session_state[used_key] = set()

    if cache_key in st.session_state:
        video_id = st.session_state[cache_key]
    else:
        video_id = _search_youtube_video_id(query, exclude_ids=st.session_state[used_key])
        if video_id:
            st.session_state[cache_key] = video_id
            st.session_state[used_key].add(video_id)

    if video_id:
        embed_html = f"""
        <div style="
            border-radius: 12px;
            overflow: hidden;
            margin-bottom: 1rem;
            box-shadow: 0 4px 15px rgba(108,99,255,0.2);
        ">
            <iframe
                width="100%"
                height="315"
                src="https://www.youtube.com/embed/{video_id}"
                title="{title}"
                frameborder="0"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowfullscreen
                style="border-radius: 12px;"
            ></iframe>
        </div>
        """
        components.html(embed_html, height=340)
    else:
        from urllib.parse import quote_plus
        search_url = f"https://www.youtube.com/results?search_query={quote_plus(query)}"
        st.warning(f"Could not embed video. [Search on YouTube]({search_url})")


# ── Main render ───────────────────────────────────────────────
def render():
    """Render the modules page."""
    user    = st.session_state.get("user", {})
    user_id = user.get("user_id", "")

    st.markdown(
        """
        <h1 style="
            background: linear-gradient(135deg, #6C63FF, #FF6584);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        ">📖 Learning Modules</h1>
        """,
        unsafe_allow_html=True,
    )
    st.caption("Track your progress, watch recommended videos, and test your knowledge.")

    try:
        subjects = get_subjects(user_id)
    except Exception:
        subjects = []

    if not subjects:
        st.info("Enroll in subjects first to see learning modules.")
        return

    # ── Deep-link from Study Plan ──────────────────────────────
    goto_subject_name   = st.session_state.pop("goto_subject_name", None)
    goto_module_keyword = st.session_state.pop("goto_module_keyword", None)

    # Subject selector
    subject_names  = {s["subject_id"]: s["subject_name"] for s in subjects}
    subject_id_list = list(subject_names.keys())

    SELECTBOX_KEY = "modules_subject_sel"
    if goto_subject_name:
        for sid, sname in subject_names.items():
            if sname.strip().lower() == goto_subject_name.strip().lower():
                st.session_state[SELECTBOX_KEY] = sid
                break

    selected_id = st.selectbox(
        "Select a Subject",
        options=subject_id_list,
        format_func=lambda sid: subject_names[sid],
        key=SELECTBOX_KEY,
    )
    selected_name = subject_names[selected_id]

    # Navigation banner (deep-link from study plan)
    if goto_module_keyword:
        st.markdown(
            f"""
            <div style="
                background: linear-gradient(135deg, #6C63FF18, #43E97B18);
                border: 1px solid #6C63FF40;
                border-radius: 10px;
                padding: 0.7rem 1.2rem;
                margin-bottom: 0.8rem;
                display: flex;
                align-items: center;
                gap: 0.8rem;
            ">
                <span style="font-size:1.3rem;">🗓️</span>
                <div>
                    <span style="font-weight:600; color:#6C63FF;">Navigated from Study Plan</span><br>
                    <span style="color:#8888AA; font-size:0.85rem;">
                        Looking for: <em style="color:#E8E8F0;">{goto_module_keyword}</em>
                    </span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("← Back to Study Plan", key="back_to_plan"):
            st.session_state["current_page"] = "Study Plan"
            st.rerun()

    try:
        modules = get_modules(selected_id)
    except Exception:
        modules = []

    if not modules:
        st.warning("No modules found. Try re-enrolling the subject.")
        return

    # ── Progress Overview ───────────────────────────────────────
    completed_count = sum(1 for m in modules if m.get("is_completed"))
    total_count     = len(modules)
    pct             = completed_count / total_count if total_count else 0

    col_prog, col_stat = st.columns([3, 1])
    with col_prog:
        st.progress(pct)
    with col_stat:
        color = "#00D68F" if pct >= 0.8 else "#FFAA00" if pct >= 0.4 else "#FF3D71"
        st.markdown(
            f'<p style="text-align:center; font-size:1.5rem; font-weight:700; color:{color};">'
            f'{completed_count}/{total_count}</p>',
            unsafe_allow_html=True,
        )

    st.markdown(
        f"""
        <div style="display:flex; gap:1rem; margin-bottom:1rem;">
            <span style="
                background: rgba(0,214,143,0.15); color: #00D68F;
                padding: 0.4rem 1rem; border-radius: 20px; font-weight: 600;
                border: 1px solid rgba(0,214,143,0.3);
            ">✅ Completed: {completed_count}</span>
            <span style="
                background: rgba(255,170,0,0.15); color: #FFAA00;
                padding: 0.4rem 1rem; border-radius: 20px; font-weight: 600;
                border: 1px solid rgba(255,170,0,0.3);
            ">⏳ Pending: {total_count - completed_count}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")

    # ── Module cards ───────────────────────────────────────────
    active_quiz_module_id = st.session_state.get("active_quiz_module", None)

    for idx, mod in enumerate(modules):
        is_done      = mod.get("is_completed", False)
        status_icon  = "✅" if is_done else "⏳"
        status_text  = "COMPLETED" if is_done else "PENDING"
        status_color = "#00D68F" if is_done else "#FFAA00"

        # Deep-link targeting
        is_targeted = False
        if goto_module_keyword:
            mod_title_lower = mod["module_title"].lower()
            kw_lower        = goto_module_keyword.lower()
            kw_words        = [w for w in re.split(r'\W+', kw_lower) if len(w) > 3]
            is_targeted = (
                kw_lower in mod_title_lower
                or mod_title_lower in kw_lower
                or any(w in mod_title_lower for w in kw_words)
            )

        if is_targeted:
            st.markdown(
                '<div style="border:2px solid #6C63FF;border-radius:14px;'
                'padding:3px;margin-bottom:6px;'
                'box-shadow:0 0 12px rgba(108,99,255,0.4);">',
                unsafe_allow_html=True,
            )

        targeted_label = "  🎯 ← STUDY THIS" if is_targeted else ""
        with st.expander(
            f"{status_icon} Module {mod.get('module_order', idx+1)}: {mod['module_title']}  —  {status_text}{targeted_label}",
            expanded=is_targeted,
        ):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(
                    f'<span style="background:{status_color}22; color:{status_color}; '
                    f'padding:0.3rem 0.8rem; border-radius:12px; font-weight:600; font-size:0.85rem; '
                    f'border: 1px solid {status_color}44;">'
                    f'{status_icon} {status_text}</span>',
                    unsafe_allow_html=True,
                )
            with col2:
                if is_done:
                    if st.button("❌ Mark Incomplete", key=f"inc_{mod['module_id']}"):
                        mark_module_incomplete(mod["module_id"])
                        _sync_module_tasks(user_id, selected_id, mod["module_title"], "Pending")
                        st.rerun()
                else:
                    if st.button("✅ Mark Complete", key=f"comp_{mod['module_id']}"):
                        mark_module_complete(mod["module_id"])
                        _sync_module_tasks(user_id, selected_id, mod["module_title"], "Completed")
                        st.rerun()

            # ── Video Lessons ─────────────────────────────────
            st.markdown("#### 🎬 Video Lessons")
            try:
                videos = get_videos(mod["module_id"])
            except Exception:
                videos = []

            if videos:
                used_key = f"used_vids_{mod['module_id']}"
                if used_key not in st.session_state:
                    st.session_state[used_key] = set()
                for v_idx, v in enumerate(videos):
                    st.markdown(f"**🎥 {v['video_title']}**")
                    _embed_youtube_video(v, mod["module_id"], v_idx)
            else:
                if st.button("🔍 Generate Video Lessons", key=f"vid_{mod['module_id']}"):
                    with st.spinner("Finding relevant educational videos…"):
                        try:
                            generated = generate_and_save_videos(
                                mod["module_id"], selected_name, mod["module_title"]
                            )
                            if generated:
                                st.success(f"Found {len(generated)} videos!")
                                st.rerun()
                            else:
                                st.error("Could not find video suggestions. Try again.")
                        except Exception as e:
                            st.error(f"Error generating videos: {e}")

            st.markdown("---")

            # ── Quiz / Test ───────────────────────────────────
            st.markdown("#### 📝 Module Test")
            try:
                test = get_test(mod["module_id"])
            except Exception:
                test = None

            if test:
                if st.button(
                    "📝 Take Quiz" if active_quiz_module_id != mod["module_id"] else "📝 Hide Quiz",
                    key=f"open_quiz_{mod['module_id']}",
                ):
                    st.session_state["active_quiz_module"] = (
                        None if active_quiz_module_id == mod["module_id"] else mod["module_id"]
                    )
                    st.rerun()
            else:
                if st.button("🧠 Generate Quiz", key=f"quiz_{mod['module_id']}"):
                    with st.spinner("Generating quiz questions…"):
                        try:
                            generated = generate_and_save_test(
                                mod["module_id"], selected_name, mod["module_title"]
                            )
                            if generated:
                                st.success("Quiz ready! Click 'Take Quiz' to start.")
                                st.rerun()
                            else:
                                st.error("Could not generate quiz. Try again.")
                        except Exception as e:
                            st.error(f"Error generating quiz: {e}")

        if is_targeted:
            st.markdown("</div>", unsafe_allow_html=True)

    # ── Quiz rendering (outside all expanders) ─────────────────
    if active_quiz_module_id:
        target_mod = next((m for m in modules if m["module_id"] == active_quiz_module_id), None)
        if target_mod:
            try:
                test = get_test(target_mod["module_id"])
            except Exception:
                test = None

            if test:
                st.markdown("---")
                st.markdown(
                    f"""
                    <div style="
                        background: linear-gradient(135deg, #1A1A2E, #25254B);
                        border: 1px solid #6C63FF;
                        border-radius: 12px;
                        padding: 1.5rem;
                        margin-top: 1rem;
                    ">
                        <h3 style="margin:0; color:#6C63FF;">
                            📝 Quiz: {target_mod['module_title']}
                        </h3>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                _render_quiz(test, target_mod, user_id)


# ── Quiz renderer ─────────────────────────────────────────────
def _render_quiz(test: dict, module: dict, user_id: str):
    """Render an interactive multiple-choice quiz (called OUTSIDE expanders)."""
    try:
        questions = json.loads(test["questions"]) if isinstance(test["questions"], str) else test["questions"]
    except (json.JSONDecodeError, TypeError):
        st.error("Quiz data is corrupted.")
        return

    if not isinstance(questions, list) or not questions:
        st.warning("No valid quiz questions available.")
        return

    form_key = f"quiz_form_{module['module_id']}"
    with st.form(form_key):
        answers = []
        for i, q in enumerate(questions):
            st.markdown(f"**Q{i+1}.** {q.get('question', '')}")
            options = q.get("options", [])
            choice = st.radio(
                "Select your answer:",
                options=options,
                key=f"q_{module['module_id']}_{i}",
                label_visibility="collapsed",
            )
            answers.append(choice)
            st.markdown("")

        submitted = st.form_submit_button("Submit Answers", use_container_width=True)

    if submitted:
        score = 0
        total = len(questions)
        for i, q in enumerate(questions):
            correct   = q.get("correct_answer", "")
            user_letter = answers[i][0] if answers[i] else ""
            if user_letter.upper() == correct.upper():
                score += 1

        try:
            save_test_result(test["test_id"], user_id, score, total, answers)
        except Exception:
            pass

        pct = round(score / total * 100) if total else 0
        if pct >= 80:
            st.success(f"🎉 Excellent! You scored **{score}/{total}** ({pct}%)")
        elif pct >= 50:
            st.warning(f"👍 Good effort! You scored **{score}/{total}** ({pct}%)")
        else:
            st.error(f"📖 Keep studying! You scored **{score}/{total}** ({pct}%)")

        st.markdown("---")
        st.markdown("##### 📋 Explanations")
        for i, q in enumerate(questions):
            correct     = q.get("correct_answer", "")
            explanation = q.get("explanation", "")
            user_ans    = answers[i][0].upper() if answers[i] else ""
            is_right    = user_ans == correct.upper()
            icon        = "✅" if is_right else "❌"
            st.markdown(f"{icon} **Q{i+1}.** Correct: **{correct}** — {explanation}")
