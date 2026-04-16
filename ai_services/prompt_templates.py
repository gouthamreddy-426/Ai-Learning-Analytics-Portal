"""
Prompt templates for all AI-powered features.
Each function returns a formatted prompt string ready for the LLM.
"""

# ── Module Generation ─────────────────────────────────────────

def study_modules_prompt(subject_name: str, difficulty_level: str) -> str:
    count_map = {"Easy": 3, "Medium": 5, "Hard": 7}
    count = count_map.get(difficulty_level, 5)

    return f"""You are an expert curriculum designer.

Generate exactly {count} study modules for the subject: **{subject_name}**
Difficulty level: **{difficulty_level}**

Guidelines:
- Easy  → cover foundational / introductory topics only.
- Medium → cover foundational + intermediate topics.
- Hard  → cover foundational + intermediate + advanced topics.

Return ONLY a numbered list (1. Module Title) with no extra commentary.
Each module title should be concise (3-8 words).
"""


# ── YouTube Video Suggestions ─────────────────────────────────

def youtube_videos_prompt(subject_name: str, module_title: str) -> str:
    return f"""You are a helpful study assistant who recommends educational YouTube videos.

Generate 3 highly specific and UNIQUE YouTube search queries for finding the BEST educational videos about:

Subject: {subject_name}
Module/Topic: {module_title}

CRITICAL RULES:
- Each search query MUST be UNIQUELY about "{module_title}" — NOT about the general subject "{subject_name}".
- Each of the 3 queries MUST target a DIFFERENT aspect of "{module_title}" so they return DIFFERENT videos.
- Query 1: Focus on a conceptual explanation or introduction to {module_title}
- Query 2: Focus on a practical example, tutorial, or hands-on demo of {module_title}
- Query 3: Focus on an advanced concept, real-world application, or interview prep for {module_title}
- Include specific technical keywords from the module topic in every query.
- DO NOT use generic terms like "tutorial" or "explained" alone — combine with specific topic terms.

Return the result as a numbered list in this EXACT format:
1. Descriptive Video Title | unique specific search query terms here
2. Descriptive Video Title | different specific search query terms here
3. Descriptive Video Title | another unique specific search query terms here

Example for Subject: Machine Learning, Module: Neural Networks:
1. What Are Neural Networks and How They Work | what are neural networks architecture layers explained
2. Build a Neural Network from Scratch in Python | build neural network from scratch python code tutorial
3. Neural Network Backpropagation Deep Dive | neural network backpropagation gradient descent math

Return ONLY the numbered list, nothing else.
"""


# ── Module Quiz / Test ────────────────────────────────────────

def module_test_prompt(subject_name: str, module_title: str) -> str:
    return f"""You are an expert educator.

Create a quiz of exactly 5 multiple-choice questions for the following module:

Subject: {subject_name}
Module: {module_title}

Return ONLY valid JSON — an array of objects. Each object must have:
- "question": the question text
- "options": an array of exactly 4 option strings ["A) ...", "B) ...", "C) ...", "D) ..."]
- "correct_answer": the letter of the correct option (A, B, C, or D)
- "explanation": a 1-2 sentence explanation of the correct answer

Example format:
[
  {{
    "question": "What is ...?",
    "options": ["A) ...", "B) ...", "C) ...", "D) ..."],
    "correct_answer": "A",
    "explanation": "Because ..."
  }}
]

Return ONLY the JSON array, no markdown fences, no extra text.
"""


# ── Cheat Sheet ───────────────────────────────────────────────

def cheatsheet_prompt(subject_name: str) -> str:
    return f"""You are a knowledgeable tutor.

Create a concise cheat sheet for the subject: **{subject_name}**.

Include the following sections:
1. **Key Formulas** — list the most important formulas with brief descriptions.
2. **Core Concepts** — summarise the fundamental ideas.
3. **Quick Explanations** — short, easy-to-understand explanations.
4. **Interview Highlights** — important points frequently asked in interviews.

Format the output in clean Markdown with headers and bullet points.
"""


def cheatsheet_module_prompt(subject_name: str, module_title: str) -> str:
    return f"""You are a knowledgeable tutor.

Create a focused, concise cheat sheet specifically for the module: **{module_title}**
(Part of the subject: {subject_name})

Include the following sections:
1. **Key Concepts** — the core ideas unique to this module.
2. **Important Formulas / Techniques** — specific formulas or methods used in this module.
3. **Quick Summary** — 3-5 bullet points covering the most critical points.
4. **Common Mistakes** — pitfalls students commonly encounter in this module.
5. **Interview / Exam Tips** — frequently asked questions on this exact topic.

Keep it specific to "{module_title}" — do NOT write a general cheat sheet for the entire subject.
Format the output in clean Markdown with headers and bullet points.
"""



# ── Assignment Generation ─────────────────────────────────────

def assignment_prompt(subject_name: str) -> str:
    return f"""You are a university professor.

Create a student assignment for the subject: **{subject_name}**.

Include the following sections:
1. **Theory Questions** (3 questions)
2. **Problem-Solving / Practical Questions** (3 questions)
3. **Short-Answer Questions** (2 questions)
4. **Multiple-Choice Questions** (2 questions with 4 options each, indicate the correct answer)

If the subject is technical, include at least one coding task.

Format the output in clean Markdown.
"""


# ── Study Plan ────────────────────────────────────────────────

def study_plan_prompt(
    subjects_info: str,
    modules_to_complete: str,
    total_weeks: int,
    week_dates: str,
    today_date: str = "",
    study_hours_per_day: float = 3.0,
    skipped_tasks: str = "None",
) -> str:
    return f"""You are an expert AI study coach. Create a COMPLETE study plan that covers ALL remaining modules.

### Today's Date
{today_date}

### Plan Duration
{total_weeks} weeks (covering all days from today until the deadlines)

### Week Date Ranges
{week_dates}

### Enrolled Subjects (with deadlines, difficulty, and progress)
{subjects_info}

### ALL MODULES THAT MUST BE COMPLETED
{modules_to_complete}

### Available Study Hours Per Day
{study_hours_per_day} hours

### Tasks Skipped from Previous Days (MUST be redistributed)
{skipped_tasks}

### CRITICAL RULES
1. You MUST create a plan that covers ALL {total_weeks} weeks listed above.
2. STRICT WEEK BOUNDARIES — use EXACTLY the date ranges specified in 'Week Date Ranges' above.
   - Week 1 may be a PARTIAL week (starts today, ends on the coming Sunday).
   - Week 2 and beyond are FULL weeks: Monday through Sunday ONLY.
   - A day (e.g. Monday) must appear in ONE week only — NEVER at the end of one week and the start of the next.
   - Do NOT include any date outside the range specified for that week.
3. EVERY day in each week's specified range MUST appear in the output — do NOT skip any day.
4. Saturday and Sunday should have LIGHTER study tasks (revision, practice, or review) but MUST still be included with at least 1-2 tasks.
5. EVERY incomplete module listed above MUST appear in the plan — do NOT skip any module.
6. Each module should be split across 1-2 days: one day for studying/learning, optionally another for practice/revision.
7. PRIORITIZE subjects with closer deadlines — their modules MUST be completed first.
8. HARDER subjects (Hard difficulty) need more study time per module than Easy ones.
9. Space out modules logically — don't cram everything into Week 1.
10. Include short breaks between study sessions.
11. Add revision/recap sessions before exam dates.
12. Each task MUST reference the actual module name (e.g. "Study Module 3: Data Structures", NOT just "Study Math").
13. All modules for a subject MUST be completed BEFORE that subject's exam date.

### OUTPUT FORMAT
Return ONLY valid JSON — an array of WEEK objects. Each week object must have:
- "week": week number (1, 2, 3, ...)
- "week_label": descriptive label (e.g. "Week 1: Mar 24 - Mar 30")
- "days": an array of EXACTLY 7 day objects (or remaining days for the first partial week), each with:
  - "day": the day name (e.g. "Monday")
  - "date": the actual date in YYYY-MM-DD format
  - "tasks": an array of task objects, each with:
    - "time": time slot (e.g. "9:00 AM - 10:30 AM")
    - "subject": the subject name (MUST match enrolled subject names exactly)
    - "task": specific task referencing the module name
    - "duration_hours": duration as a number (e.g. 1.5, 1.0, 0.5)
    - "priority": "high", "medium", or "low"

Return ONLY the JSON array, no markdown fences, no extra text.
"""


# ── Final Exam ────────────────────────────────────────────────

def final_exam_prompt(subject_name: str, module_titles: list[str], difficulty: str) -> str:
    modules_str = "\n".join(f"  {i+1}. {m}" for i, m in enumerate(module_titles))
    q_count = {"Easy": 10, "Medium": 15, "Hard": 20}.get(difficulty, 15)

    return f"""You are a strict university examination expert.

Create a final exam with exactly {q_count} multiple-choice questions for:

Subject: {subject_name}
Difficulty: {difficulty}

The exam MUST cover ALL of these modules evenly:
{modules_str}

RULES:
- Questions should test UNDERSTANDING, not just memorisation.
- Include a mix of conceptual, application, and analysis questions.
- Each question must clearly relate to one of the modules above.
- Distribute questions evenly across all modules.
- Make the exam challenging enough that only students who studied properly can score above 80%.

Return ONLY valid JSON — an array of objects. Each object must have:
- "question": the question text
- "module": which module this question is from (exact title from the list above)
- "options": an array of exactly 4 option strings ["A) ...", "B) ...", "C) ...", "D) ..."]
- "correct_answer": the letter of the correct option (A, B, C, or D)
- "explanation": a 1-2 sentence explanation of the correct answer

Return ONLY the JSON array, no markdown fences, no extra text.
"""
