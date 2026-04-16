# 🎓 AI-Enabled Student Learning Analytics & Performance Portal

> An intelligent, AI-powered student study companion built with **Streamlit**, **Supabase**, and **OpenAI**.  
> Plan smarter, learn faster, track everything.

---

## 🚀 Features

| Module | Description |
|--------|-------------|
| **🔐 Authentication** | Secure signup / login with bcrypt password hashing |
| **📚 Subject Enrollment** | Enroll in subjects with Easy / Medium / Hard difficulty |
| **📖 AI Learning Modules** | Auto-generated study modules based on difficulty level |
| **🎬 YouTube Videos** | AI-suggested topic-relevant YouTube videos per module |
| **📝 Module Quizzes** | AI-generated MCQ tests with instant scoring & explanations |
| **📋 AI Cheat Sheets** | Key formulas, concepts, and interview highlights in one page |
| **📝 AI Assignments** | Theory, problem-solving, MCQ, and coding assignments |
| **✅ Task Manager** | Create, track, and complete study tasks with deadlines |
| **🗓️ AI Study Plans** | Personalised weekly schedules based on your workload |
| **📈 Analytics Dashboard** | Pie, bar, line, gauge charts — full progress visibility |

---

## 🏗️ Architecture

```
Browser
  ↓
Streamlit UI  (pages/)
  ↓
Python Backend Logic  (backend/)
  ↓
AI Services  (ai_services/ → OpenAI API)
  ↓
Supabase Database  (PostgreSQL)
```

---

## 📂 Project Structure

```
student-learning-portal/
│
├── app.py                      # Main entry point
├── requirements.txt
├── .env.example
├── .streamlit/config.toml      # Theme & server config
│
├── pages/                      # Streamlit UI pages
│   ├── login.py
│   ├── dashboard.py
│   ├── subjects.py
│   ├── modules.py
│   ├── assignments.py
│   ├── cheatsheets.py
│   ├── tasks.py
│   ├── study_plan.py
│   ├── analytics.py
│   └── profile.py
│
├── backend/                    # Business logic
│   ├── auth.py
│   ├── subject_manager.py
│   ├── module_generator.py
│   ├── assignment_generator.py
│   ├── cheatsheet_generator.py
│   ├── study_plan_generator.py
│   └── task_manager.py
│
├── database/                   # Database layer
│   ├── db_connection.py
│   └── schema.sql
│
├── ai_services/                # LLM integration
│   ├── ai_client.py
│   └── prompt_templates.py
│
├── analytics/                  # Charts & metrics
│   ├── progress_metrics.py
│   └── charts.py
│
├── utils/                      # Shared utilities
│   ├── helpers.py
│   └── constants.py
│
└── data_models/                # Data classes
    ├── user_model.py
    ├── subject_model.py
    └── task_model.py
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Streamlit |
| Backend | Python 3.11+ |
| Database | Supabase (PostgreSQL) |
| AI | OpenAI API (GPT-4o-mini) |
| Charts | Plotly |
| Auth | bcrypt |

---

## ⚡ Installation

### 1. Clone the Repository

```bash
git clone <repo-url>
cd student-learning-portal
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` and fill in your credentials:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-4o-mini
```

### 5. Set Up the Database

1. Go to your **Supabase Dashboard** → **SQL Editor**
2. Paste the contents of `database/schema.sql`
3. Click **Run** to create all tables and indexes

### 6. Run the Application

```bash
streamlit run app.py
```

Open your browser at **http://localhost:8501**.

---

## 📸 Screenshots

> _Add screenshots here after running the application._

| Page | Preview |
|------|---------|
| Dashboard | ![Dashboard](#) |
| Subjects | ![Subjects](#) |
| Modules & Videos | ![Modules](#) |
| Analytics | ![Analytics](#) |

---

## 🔮 Future Improvements

- [ ] OAuth integration (Google / GitHub login)
- [ ] PDF export for cheat sheets and study plans
- [ ] Spaced-repetition flashcard system
- [ ] Collaborative study groups
- [ ] Mobile-responsive PWA wrapper
- [ ] Real-time notifications for task deadlines
- [ ] Integration with Google Calendar
- [ ] Multi-language support
- [ ] Advanced AI tutor — interactive Q&A chat
- [ ] Performance leaderboard among students

---

## 📄 License

MIT License — feel free to use, modify, and distribute.

---

<p align="center">
  Built with ❤️ using Streamlit + Supabase + OpenAI
</p>
