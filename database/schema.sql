-- ============================================================
-- Student Learning Analytics Portal — Database Schema
-- Run this SQL in your Supabase SQL Editor to create all tables.
-- ============================================================

-- 1. Users table
CREATE TABLE IF NOT EXISTS users (
    user_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name          TEXT NOT NULL,
    email         TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at    TIMESTAMPTZ DEFAULT now()
);

-- 2. Subjects table
CREATE TABLE IF NOT EXISTS subjects (
    subject_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id          UUID REFERENCES users(user_id) ON DELETE CASCADE,
    subject_name     TEXT NOT NULL,
    difficulty_level TEXT CHECK (difficulty_level IN ('Easy', 'Medium', 'Hard')) NOT NULL,
    exam_date        DATE,
    created_at       TIMESTAMPTZ DEFAULT now()
);

-- 3. Subject modules table
CREATE TABLE IF NOT EXISTS subject_modules (
    module_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    subject_id       UUID REFERENCES subjects(subject_id) ON DELETE CASCADE,
    module_title     TEXT NOT NULL,
    module_order     INT DEFAULT 0,
    difficulty_level TEXT CHECK (difficulty_level IN ('Easy', 'Medium', 'Hard')),
    is_completed     BOOLEAN DEFAULT FALSE,
    completed_at     TIMESTAMPTZ,
    created_at       TIMESTAMPTZ DEFAULT now()
);

-- 4. Module YouTube videos
CREATE TABLE IF NOT EXISTS module_videos (
    video_id    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    module_id   UUID REFERENCES subject_modules(module_id) ON DELETE CASCADE,
    video_title TEXT NOT NULL,
    video_url   TEXT NOT NULL,
    description TEXT,
    created_at  TIMESTAMPTZ DEFAULT now()
);

-- 5. Module quizzes / tests
CREATE TABLE IF NOT EXISTS module_tests (
    test_id      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    module_id    UUID REFERENCES subject_modules(module_id) ON DELETE CASCADE,
    questions    JSONB NOT NULL,          -- [{question, options, correct_answer, explanation}]
    created_at   TIMESTAMPTZ DEFAULT now()
);

-- 6. Test attempts / results
CREATE TABLE IF NOT EXISTS test_results (
    result_id   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    test_id     UUID REFERENCES module_tests(test_id) ON DELETE CASCADE,
    user_id     UUID REFERENCES users(user_id) ON DELETE CASCADE,
    score       INT NOT NULL,
    total       INT NOT NULL,
    answers     JSONB,                    -- user's answers
    completed_at TIMESTAMPTZ DEFAULT now()
);

-- 7. Cheatsheets table
CREATE TABLE IF NOT EXISTS cheatsheets (
    cheatsheet_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    subject_id    UUID REFERENCES subjects(subject_id) ON DELETE CASCADE,
    module_id     UUID REFERENCES subject_modules(module_id) ON DELETE CASCADE,  -- nullable: NULL = subject-level
    module_title  TEXT,                                                            -- cached for display
    content       TEXT NOT NULL,
    created_at    TIMESTAMPTZ DEFAULT now()
);

-- Run this if the table already exists (Supabase SQL Editor):
-- ALTER TABLE cheatsheets ADD COLUMN IF NOT EXISTS module_id UUID REFERENCES subject_modules(module_id) ON DELETE CASCADE;
-- ALTER TABLE cheatsheets ADD COLUMN IF NOT EXISTS module_title TEXT;


-- 8. Assignments table
CREATE TABLE IF NOT EXISTS assignments (
    assignment_id   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    subject_id      UUID REFERENCES subjects(subject_id) ON DELETE CASCADE,
    assignment_text TEXT NOT NULL,
    created_at      TIMESTAMPTZ DEFAULT now()
);

-- 9. Tasks table
CREATE TABLE IF NOT EXISTS tasks (
    task_id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID REFERENCES users(user_id) ON DELETE CASCADE,
    subject_id      UUID REFERENCES subjects(subject_id) ON DELETE CASCADE,
    task_name       TEXT NOT NULL,
    due_date        DATE,
    status          TEXT CHECK (status IN ('Pending', 'Completed')) DEFAULT 'Pending',
    estimated_hours FLOAT DEFAULT 1.0,
    created_at      TIMESTAMPTZ DEFAULT now()
);

-- 10. Study plans table
CREATE TABLE IF NOT EXISTS study_plans (
    plan_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id        UUID REFERENCES users(user_id) ON DELETE CASCADE,
    plan_content   TEXT NOT NULL,
    generated_date TIMESTAMPTZ DEFAULT now()
);

-- 11. Final Exams table
CREATE TABLE IF NOT EXISTS final_exams (
    exam_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id          UUID REFERENCES users(user_id) ON DELETE CASCADE,
    subject_id       UUID REFERENCES subjects(subject_id) ON DELETE CASCADE,
    status           TEXT DEFAULT 'not_ready',  -- not_ready | ready | completed | failed
    questions        JSONB,
    user_answers     JSONB,
    total_questions  INT DEFAULT 0,
    correct_answers  INT DEFAULT 0,
    raw_score        FLOAT DEFAULT 0,
    penalty_pct      FLOAT DEFAULT 0,
    final_score      FLOAT DEFAULT 0,
    certificate      BOOLEAN DEFAULT FALSE,
    attempted_at     TIMESTAMPTZ,
    created_at       TIMESTAMPTZ DEFAULT now()
);


-- Indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_subjects_user      ON subjects(user_id);
CREATE INDEX IF NOT EXISTS idx_modules_subject    ON subject_modules(subject_id);
CREATE INDEX IF NOT EXISTS idx_tasks_user         ON tasks(user_id);
CREATE INDEX IF NOT EXISTS idx_tasks_status       ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_study_plans_user   ON study_plans(user_id);
CREATE INDEX IF NOT EXISTS idx_assignments_subj   ON assignments(subject_id);
CREATE INDEX IF NOT EXISTS idx_cheatsheets_subj   ON cheatsheets(subject_id);
CREATE INDEX IF NOT EXISTS idx_module_videos_mod  ON module_videos(module_id);
CREATE INDEX IF NOT EXISTS idx_module_tests_mod   ON module_tests(module_id);
CREATE INDEX IF NOT EXISTS idx_test_results_user  ON test_results(user_id);
CREATE INDEX IF NOT EXISTS idx_final_exams_user   ON final_exams(user_id);
CREATE INDEX IF NOT EXISTS idx_final_exams_subj   ON final_exams(subject_id);
