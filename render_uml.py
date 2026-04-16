"""Render Mermaid diagrams to PNG files using mermaid.ink API."""
import base64, requests, os

DIAGRAMS = {
    "class_diagram_entities": """classDiagram
    direction TB
    class User {
        +UUID user_id
        +String name
        +String email
        +String password_hash
        +DateTime created_at
    }
    class Subject {
        +UUID subject_id
        +UUID user_id
        +String subject_name
        +String difficulty_level
        +Date exam_date
        +DateTime created_at
    }
    class SubjectModule {
        +UUID module_id
        +UUID subject_id
        +String module_title
        +Int module_order
        +String difficulty_level
        +Boolean is_completed
        +DateTime completed_at
    }
    class ModuleVideo {
        +UUID video_id
        +UUID module_id
        +String video_title
        +String video_url
    }
    class ModuleTest {
        +UUID test_id
        +UUID module_id
        +JSON questions
    }
    class TestResult {
        +UUID result_id
        +UUID test_id
        +UUID user_id
        +Int score
        +Int total
        +JSON answers
    }
    class CheatSheet {
        +UUID cheatsheet_id
        +UUID subject_id
        +UUID module_id
        +String content
    }
    class Assignment {
        +UUID assignment_id
        +UUID subject_id
        +String assignment_text
    }
    class Task {
        +UUID task_id
        +UUID user_id
        +UUID subject_id
        +String task_name
        +Date due_date
        +String status
        +Float estimated_hours
    }
    class StudyPlan {
        +UUID plan_id
        +UUID user_id
        +Text plan_content
        +DateTime generated_date
    }
    class FinalExam {
        +UUID exam_id
        +UUID user_id
        +UUID subject_id
        +String status
        +JSON questions
        +JSON user_answers
        +Float raw_score
        +Float penalty_pct
        +Float final_score
        +Boolean certificate
    }
    User "1" --> "*" Subject : enrolls
    User "1" --> "*" Task : owns
    User "1" --> "*" StudyPlan : generates
    User "1" --> "*" FinalExam : attempts
    User "1" --> "*" TestResult : records
    Subject "1" --> "*" SubjectModule : contains
    Subject "1" --> "*" Assignment : has
    Subject "1" --> "*" CheatSheet : has
    Subject "1" --> "0..1" FinalExam : has
    SubjectModule "1" --> "*" ModuleVideo : has
    SubjectModule "1" --> "0..1" ModuleTest : has
    SubjectModule "1" --> "*" CheatSheet : has
    ModuleTest "1" --> "*" TestResult : produces
    Subject "1" --> "*" Task : linked to
""",

    "class_diagram_services": """classDiagram
    direction TB
    class DBConnection {
        -Client _supabase_client
        +get_supabase_client() Client
    }
    class AuthService {
        +hash_password(password) String
        +verify_password(password, hashed) Boolean
        +signup(name, email, password) dict
        +login(email, password) dict
        +get_user_profile(user_id) dict
        +update_user_name(user_id, name) Boolean
    }
    class SubjectManager {
        +enroll_subject(user_id, name, difficulty, exam_date) dict
        +get_subjects(user_id) list
        +get_subject_by_id(subject_id) dict
        +delete_subject(subject_id) Boolean
    }
    class ModuleGenerator {
        +generate_and_save_modules(subject_id, name, difficulty) list
        +get_modules(subject_id) list
        +mark_module_complete(module_id) Boolean
        +generate_youtube_videos(module_id, subject, title) list
        +generate_module_test(module_id, subject, title) dict
    }
    class TaskManager {
        +create_task(user_id, subject_id, name, due_date, hours) dict
        +get_tasks(user_id) list
        +get_pending_tasks(user_id) list
        +update_task_status(task_id, status) Boolean
        +delete_task(task_id) Boolean
        +auto_adjust_overdue_tasks(user_id) Int
    }
    class StudyPlanGenerator {
        +generate_and_save_plan(user_id, study_hours) dict
        +get_latest_plan(user_id) dict
    }
    class AssignmentGenerator {
        +generate_and_save_assignment(subject_id, name) dict
        +get_assignments(subject_id) list
        +delete_assignment(assignment_id) Boolean
    }
    class CheatSheetGenerator {
        +generate_and_save_cheatsheet(subject_id, name, module_id, title) dict
        +get_cheatsheets(subject_id) list
    }
    class ExamManager {
        +Float PENALTY_PER_DAY
        +get_exam(user_id, subject_id) dict
        +get_all_exams(user_id) list
        +compute_exam_status(exam_date, record) tuple
        +generate_exam(user_id, subject_id, name, modules, difficulty) dict
        +submit_exam(exam_id, answers, questions, penalty) dict
    }
    class AIClient {
        -Client _client
        -String _provider
        +get_model() String
        +ask_llm(prompt, temperature, max_tokens) String
        +ask_llm_json(prompt, temperature, max_tokens) dict
    }
    class PromptTemplates {
        +study_modules_prompt(subject, difficulty) String
        +youtube_videos_prompt(subject, module) String
        +module_test_prompt(subject, module) String
        +cheatsheet_prompt(subject) String
        +assignment_prompt(subject) String
        +study_plan_prompt(...) String
        +final_exam_prompt(subject, modules, difficulty) String
    }
    class ProgressMetrics {
        +get_subject_progress(user_id) list
        +get_task_stats(user_id) dict
        +get_weekly_task_stats(user_id) dict
        +get_overall_progress(user_id) Float
    }
    class Charts {
        +task_completion_pie(completed, pending) Figure
        +subject_progress_bar(subjects, pcts) Figure
        +overall_progress_gauge(value) Figure
        +module_completion_grouped(progress) Figure
    }
    class SessionManager {
        -Path _SESSION_FILE
        +save_session(user) void
        +load_session() dict
        +clear_session() void
    }
    AuthService ..> DBConnection : uses
    SubjectManager ..> DBConnection : uses
    ModuleGenerator ..> DBConnection : uses
    ModuleGenerator ..> AIClient : calls
    ModuleGenerator ..> PromptTemplates : uses
    TaskManager ..> DBConnection : uses
    StudyPlanGenerator ..> DBConnection : uses
    StudyPlanGenerator ..> AIClient : calls
    AssignmentGenerator ..> DBConnection : uses
    AssignmentGenerator ..> AIClient : calls
    CheatSheetGenerator ..> DBConnection : uses
    CheatSheetGenerator ..> AIClient : calls
    ExamManager ..> DBConnection : uses
    ExamManager ..> AIClient : calls
    ExamManager ..> PromptTemplates : uses
    ProgressMetrics ..> SubjectManager : uses
    ProgressMetrics ..> ModuleGenerator : uses
    ProgressMetrics ..> TaskManager : uses
""",

    "class_diagram_views": """classDiagram
    direction TB
    class App {
        +main()
        -_load_css()
        -_render_sidebar()
        -_route_page(selected)
    }
    class LoginView {
        +render()
    }
    class DashboardView {
        +render()
    }
    class SubjectsView {
        +render()
    }
    class ModulesView {
        +render()
    }
    class StudyPlanView {
        +render()
    }
    class ExamsView {
        +render()
        -_take_exam(exam_rec, penalty, subject)
        -_show_results(exam_rec, subject)
    }
    class TasksView {
        +render()
    }
    class CheatSheetsView {
        +render()
    }
    class AssignmentsView {
        +render()
    }
    class AnalyticsView {
        +render()
    }
    class ProfileView {
        +render()
        -_logout()
    }
    App --> LoginView : auth gate
    App --> DashboardView : routes
    App --> SubjectsView : routes
    App --> ModulesView : routes
    App --> StudyPlanView : routes
    App --> ExamsView : routes
    App --> TasksView : routes
    App --> CheatSheetsView : routes
    App --> AssignmentsView : routes
    App --> AnalyticsView : routes
    App --> ProfileView : routes
"""
}

OUT_DIR = r"d:\IOMP\student-learning-portal\uml_diagrams"
os.makedirs(OUT_DIR, exist_ok=True)

for name, code in DIAGRAMS.items():
    encoded = base64.urlsafe_b64encode(code.encode("utf-8")).decode("utf-8")
    url = f"https://mermaid.ink/img/{encoded}?type=png&bgColor=!white&theme=default&width=1400"
    print(f"Downloading {name}...")
    try:
        resp = requests.get(url, timeout=60)
        if resp.status_code == 200 and len(resp.content) > 1000:
            path = os.path.join(OUT_DIR, f"{name}.png")
            with open(path, "wb") as f:
                f.write(resp.content)
            print(f"  OK -> {path} ({len(resp.content):,} bytes)")
        else:
            print(f"  FAIL: HTTP {resp.status_code}, {len(resp.content)} bytes")
    except Exception as e:
        print(f"  ERROR: {e}")

print("\nDone!")
