"""
exam_manager.py — Backend logic for final exams.

Handles: exam generation, status tracking, scoring with late-penalty,
certificate eligibility, and retake flow.
"""

import json
from datetime import datetime, date
from database.db_connection import get_supabase_client
from ai_services.ai_client import ask_llm_json
from ai_services.prompt_templates import final_exam_prompt


# ── Penalty: -2% per day late ────────────────────────────────
PENALTY_PER_DAY = 2.0
PASS_THRESHOLD  = 80.0   # minimum score for certificate


def get_exam(user_id: str, subject_id: str) -> dict | None:
    """Get the latest final exam record for a subject, or None."""
    sb = get_supabase_client()
    try:
        r = sb.table("final_exams") \
              .select("*") \
              .eq("user_id", user_id) \
              .eq("subject_id", subject_id) \
              .order("created_at", desc=True) \
              .limit(1) \
              .execute()
        return r.data[0] if r.data else None
    except Exception:
        return None


def get_all_exams(user_id: str) -> list:
    """Get all final exams for a user."""
    sb = get_supabase_client()
    try:
        r = sb.table("final_exams") \
              .select("*") \
              .eq("user_id", user_id) \
              .execute()
        return r.data or []
    except Exception:
        return []


def compute_exam_status(
    exam_date_str: str,
    exam_record: dict | None,
    all_modules_done: bool = False,
) -> tuple[str, str, float]:
    """
    Returns (status, status_label, penalty_pct).
    Status values: not_ready, ready, completed, failed, overdue

    Exam unlocks when:
      1. The exam date arrives (or has passed), OR
      2. All modules are completed (even before deadline).
    """
    today = date.today()

    # ── Already passed ───────────────────────────────────────
    if exam_record and exam_record.get("status") == "completed":
        return "completed", "✅ Completed", 0.0

    # ── Failed — needs retake ────────────────────────────────
    if exam_record and exam_record.get("status") == "failed":
        return "failed", "🔄 Retake Required", 0.0

    # ── No exam date set ─────────────────────────────────────
    if not exam_date_str:
        # Even without a date, if all modules are done the student can take
        if all_modules_done:
            return "ready", "🟢 All Modules Done — Ready!", 0.0
        return "not_ready", "📅 No exam date set", 0.0

    try:
        exam_dt = datetime.fromisoformat(str(exam_date_str)).date()
    except Exception:
        if all_modules_done:
            return "ready", "🟢 All Modules Done — Ready!", 0.0
        return "not_ready", "📅 Invalid date", 0.0

    days_until = (exam_dt - today).days

    # ── All modules complete early — unlock now ──────────────
    if all_modules_done and days_until > 0:
        return "ready", f"🟢 All Modules Done — Ready! ({days_until}d early 🎉)", 0.0

    if days_until > 0:
        return "not_ready", f"📚 Keep Studying — {days_until}d left", 0.0
    elif days_until == 0:
        return "ready", "🟢 Exam Day — Ready to Start!", 0.0
    else:
        days_late = abs(days_until)
        penalty = min(days_late * PENALTY_PER_DAY, 50.0)  # cap at 50%
        return "overdue", f"⚠️ Overdue by {days_late}d — {penalty:.0f}% penalty", penalty


def generate_exam(user_id: str, subject_id: str, subject_name: str,
                  module_titles: list[str], difficulty: str) -> dict | None:
    """Generate AI exam questions and save to DB."""
    sb = get_supabase_client()

    prompt = final_exam_prompt(subject_name, module_titles, difficulty)
    questions = ask_llm_json(prompt, temperature=0.4, max_tokens=4000)

    if not isinstance(questions, list):
        return None

    record = {
        "user_id": user_id,
        "subject_id": subject_id,
        "status": "ready",
        "questions": json.dumps(questions),
        "total_questions": len(questions),
    }

    try:
        r = sb.table("final_exams").insert(record).execute()
        return r.data[0] if r.data else None
    except Exception:
        return None


def submit_exam(exam_id: str, user_answers: dict, questions: list,
                penalty_pct: float = 0.0) -> dict:
    """
    Evaluate the exam, compute score with penalty, update the record.
    If final_score < 80, mark as 'failed' (allows retake).
    If final_score >= 80, mark as 'completed' with certificate.
    """
    sb = get_supabase_client()

    total = len(questions)
    correct = 0
    results = []

    for i, q in enumerate(questions):
        user_ans = user_answers.get(str(i), "")
        correct_ans = q.get("correct_answer", "")
        is_correct = user_ans.strip().upper() == correct_ans.strip().upper()
        if is_correct:
            correct += 1
        results.append({
            "question": q.get("question", ""),
            "user_answer": user_ans,
            "correct_answer": correct_ans,
            "is_correct": is_correct,
            "explanation": q.get("explanation", ""),
        })

    raw_score = round(correct / total * 100, 1) if total else 0
    final_score = max(0, raw_score - penalty_pct)
    passed = final_score >= PASS_THRESHOLD
    certificate = passed

    # Status: "completed" if passed, "failed" if not (allows retake)
    new_status = "completed" if passed else "failed"

    try:
        sb.table("final_exams").update({
            "status": new_status,
            "user_answers": json.dumps(user_answers),
            "correct_answers": correct,
            "raw_score": raw_score,
            "penalty_pct": penalty_pct,
            "final_score": final_score,
            "certificate": certificate,
            "attempted_at": datetime.now().isoformat(),
        }).eq("exam_id", exam_id).execute()
    except Exception:
        pass

    return {
        "raw_score": raw_score,
        "penalty_pct": penalty_pct,
        "final_score": final_score,
        "correct": correct,
        "total": total,
        "certificate": certificate,
        "passed": passed,
        "results": results,
    }


def reset_exam_for_retake(exam_id: str) -> bool:
    """
    Delete the failed exam record so the student can generate a fresh exam.
    Returns True on success.
    """
    sb = get_supabase_client()
    try:
        sb.table("final_exams").delete().eq("exam_id", exam_id).execute()
        return True
    except Exception:
        return False
