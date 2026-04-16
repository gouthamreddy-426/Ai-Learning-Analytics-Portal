# EduPulse — AI-Enabled Student Learning & Performance Portal

EduPulse is a full-stack web application that personalizes the learning experience for students using AI. Students enroll in subjects, and the system generates structured study modules, quizzes, assignments, cheat sheets, and weekly study plans — all powered by large language models. The portal tracks progress across every dimension: module completion, task management, exam scores, and overall performance analytics.

Built with **Python**, **Streamlit**, **Supabase (PostgreSQL)**, and **Groq/LLaMA 3.3**.

---

## Features

### Authentication & User Management
- Secure signup and login with **bcrypt** password hashing
- Persistent session management (auto-login on return visits)
- Editable user profile

### Subject Enrollment
- Add subjects with a difficulty level (Easy, Medium, Hard) and an exam deadline
- Difficulty determines the number of generated modules (3 / 5 / 7)
- Delete subjects and cascade-remove all related data

### AI Module Generation
- Automatically generates topic-wise study modules for each subject via LLM
- Each module includes:
  - **YouTube video suggestions** — search-based links for self-study
  - **Interactive quizzes** — multiple-choice questions with explanations
  - **Completion tracking** — mark modules done, track progress per subject

### AI Assignments & Cheat Sheets
- Generate subject-level or module-level **assignments** with a single click
- Generate concise **cheat sheets** covering key formulas, definitions, and shortcuts
- All content is stored in the database for future reference

### Task Management
- Create, edit, and track study tasks with due dates and estimated hours
- Tasks are auto-created when a study plan is generated
- **Automatic rescheduling** — overdue tasks are pushed to the next available date
- Filter by status (Pending / Completed) and subject

### AI Study Plan Generator
- Generates a **multi-week, day-by-day study calendar** that covers all enrolled subjects
- Accounts for subject difficulty, module count, and exam deadlines
- Visual calendar UI with:
  - Week selector dropdown
  - Day cards showing tasks, priorities, and study hours
  - Clickable tasks that navigate directly to the corresponding module
  - Color-coded urgency indicators for approaching deadlines
- Progress bar and module coverage breakdown per subject

### Final Exam System
- Exams unlock when:
  - The subject deadline arrives, **or**
  - All modules for that subject are completed (early unlock)
- AI generates a full exam (multiple-choice) tailored to the subject and difficulty
- Scoring with **late-penalty** system: −2% per day overdue (capped at 50%)
- Pass threshold: **80%** — students scoring below must retake with a fresh exam
- Certificates awarded on passing

### Analytics Dashboard
- **Task completion** donut chart (completed vs pending)
- **Subject progress** horizontal bar chart (% modules done per subject)
- **Overall progress** gauge indicator
- **Module completion** grouped bar chart
- **Weekly learning trend** line chart
- **Exam performance** summary with scores and certificate status

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit (Python) |
| Backend | Python 3.10+ |
| Database | Supabase (PostgreSQL, hosted) |
| AI / LLM | Groq API — LLaMA 3.3 70B Versatile |
| Auth | bcrypt hashing + local session files |
| Charts | Plotly (interactive, dark-themed) |
| Styling | Custom CSS (Inter font, teal dark theme) |

---

## Project Structure

```
├── app.py                      # Entry point, routing, sidebar, global styles
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variable template
├── .streamlit/
│   └── config.toml             # Streamlit dark theme configuration
├── assets/
│   └── logo.png                # App logo
├── ai_services/
│   ├── ai_client.py            # LLM client wrapper (Groq / OpenAI compatible)
│   └── prompt_templates.py     # All LLM prompt templates
├── backend/
│   ├── auth.py                 # Signup, login, profile updates
│   ├── subject_manager.py      # Subject CRUD operations
│   ├── module_generator.py     # AI module + video + quiz generation
│   ├── assignment_generator.py # AI assignment generation
│   ├── cheatsheet_generator.py # AI cheat sheet generation
│   ├── study_plan_generator.py # AI study plan generation + task creation
│   ├── task_manager.py         # Task CRUD + auto-rescheduling
│   └── exam_manager.py         # Exam generation, scoring, retakes
├── database/
│   ├── db_connection.py        # Supabase client initialization
│   ├── schema.sql              # Full database schema (11 tables)
│   └── setup_tables.py         # Programmatic table setup
├── data_models/
│   ├── user_model.py           # User data structures
│   ├── subject_model.py        # Subject data structures
│   └── task_model.py           # Task data structures
├── analytics/
│   ├── progress_metrics.py     # Metric computation functions
│   └── charts.py               # Plotly chart builders
├── views/
│   ├── login.py                # Login / signup page
│   ├── dashboard.py            # Home screen with metrics and charts
│   ├── subjects.py             # Subject management page
│   ├── modules.py              # Module viewer with videos and quizzes
│   ├── assignments.py          # Assignment generation and viewing
│   ├── cheatsheets.py          # Cheat sheet generation and viewing
│   ├── tasks.py                # Task management page
│   ├── study_plan.py           # Weekly calendar study plan
│   ├── exams.py                # Final exam interface
│   ├── analytics.py            # Analytics dashboard
│   └── profile.py              # User profile page
└── utils/
    ├── constants.py            # App-wide constants, nav items, theme colors
    ├── session_manager.py      # Session persistence (save/load/clear)
    └── helpers.py              # Date formatting, markdown parsing utilities
```

---

## Database Schema

The application uses **11 PostgreSQL tables** hosted on Supabase:

| Table | Purpose |
|---|---|
| `users` | User accounts (name, email, bcrypt hash) |
| `subjects` | Enrolled subjects with difficulty and exam date |
| `subject_modules` | AI-generated modules per subject |
| `module_videos` | YouTube video suggestions per module |
| `module_tests` | Quiz questions (JSON) per module |
| `test_results` | Student quiz attempts and scores |
| `cheatsheets` | Generated cheat sheets (subject or module level) |
| `assignments` | Generated assignments per subject |
| `tasks` | Study tasks with due dates and status |
| `study_plans` | AI-generated weekly study plans (JSON) |
| `final_exams` | Final exam records, scores, and certificates |

Full schema available in [`database/schema.sql`](database/schema.sql).

---

## Setup & Installation

### Prerequisites
- Python 3.10 or higher
- A [Supabase](https://supabase.com) project (free tier works)
- A [Groq](https://console.groq.com) API key (free, no credit card)

### Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/gouthamreddy-426/Edu_Pulse_AI.git
   cd Edu_Pulse_AI
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate        # Linux/Mac
   venv\Scripts\activate           # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up the database**
   - Open your Supabase project → SQL Editor
   - Paste and run the contents of `database/schema.sql`

5. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and fill in your Supabase URL, Supabase anon key, and Groq API key.

6. **Run the application**
   ```bash
   streamlit run app.py
   ```
   The app opens at `http://localhost:8501`.

---

## How It Works

1. **Sign up** and log in to your account.
2. **Add subjects** you want to study — set the difficulty and exam deadline.
3. The system **generates modules** for each subject using AI.
4. Study each module using **video suggestions** and test yourself with **quizzes**.
5. **Generate a study plan** — the AI creates a week-by-week calendar with daily tasks.
6. Track your progress on the **Dashboard** and **Analytics** pages.
7. When ready (or when the deadline arrives), take the **Final Exam**.
8. Score 80% or above to earn a **certificate**. Below 80%? Retake with a fresh exam.

---

## Screenshots

> Screenshots can be added to the `assets/` folder and referenced here.

---

## License

This project was developed as an academic project (IOMP — Integrated Online Mini Project).
