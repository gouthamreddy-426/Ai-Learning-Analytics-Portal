"""
Application-wide constants.
"""

# ── Application Meta ──────────────────────────────────────────
APP_TITLE = "🎓 Student Learning Portal"
APP_ICON = "🎓"
APP_LAYOUT = "wide"

# ── Difficulty Levels ─────────────────────────────────────────
DIFFICULTY_LEVELS = ["Easy", "Medium", "Hard"]

MODULE_COUNT_MAP = {
    "Easy": 3,
    "Medium": 5,
    "Hard": 7,
}

# ── Task Statuses ─────────────────────────────────────────────
TASK_STATUSES = ["Pending", "Completed"]

# ── Sidebar Navigation ───────────────────────────────────────
NAV_ITEMS = {
    "Dashboard":    "📊",
    "Subjects":     "📚",
    "Modules":      "📖",
    "Assignments":  "📝",
    "Cheat Sheets": "📋",
    "Tasks":        "✅",
    "Study Plan":   "🗓️",
    "Exams":        "🎓",
    "Analytics":    "📈",
    "Profile":      "👤",
}


# ── Theme Colors (Teal Professional) ─────────────────────────
COLORS = {
    "primary":       "#00C2A8",
    "secondary":     "#4CC9F0",
    "accent":        "#F59E0B",
    "background":    "#0E1117",
    "surface":       "#1C1F26",
    "surface_light": "#252B36",
    "text":          "#FAFAFA",
    "text_muted":    "#8B949E",
    "success":       "#00C2A8",
    "warning":       "#F59E0B",
    "error":         "#F85149",
    "chart_palette": ["#00C2A8", "#4CC9F0", "#F59E0B", "#F85149",
                      "#A8DADC", "#90E0EF", "#7B2D8B", "#0096C7"],
}
