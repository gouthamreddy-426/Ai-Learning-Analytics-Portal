"""
Plotly chart builders for the analytics dashboard.
All functions return a Plotly figure ready for st.plotly_chart().
"""

import plotly.graph_objects as go
import plotly.express as px
from utils.constants import COLORS


def _base_layout(fig: go.Figure, title: str = "") -> go.Figure:
    """Apply consistent dark theme styling to a Plotly figure."""
    fig.update_layout(
        title=dict(text=title, font=dict(size=18, color=COLORS["text"])),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=COLORS["text_muted"], size=12),
        margin=dict(l=40, r=40, t=60, b=40),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color=COLORS["text_muted"]),
        ),
    )
    return fig


# ── Pie Chart: Task Completion ────────────────────────────────

def task_completion_pie(completed: int, pending: int) -> go.Figure:
    """Donut chart showing completed vs pending tasks."""
    fig = go.Figure(
        go.Pie(
            labels=["Completed", "Pending"],
            values=[completed, pending],
            hole=0.55,
            marker=dict(colors=[COLORS["success"], COLORS["warning"]]),
            textinfo="label+percent",
            textfont=dict(size=13),
        )
    )
    return _base_layout(fig, "Task Completion")


# ── Bar Chart: Subject Progress ───────────────────────────────

def subject_progress_bar(subjects: list[str], percentages: list[float]) -> go.Figure:
    """Horizontal bar chart showing per-subject completion %."""
    fig = go.Figure(
        go.Bar(
            x=percentages,
            y=subjects,
            orientation="h",
            marker=dict(
                color=percentages,
                colorscale=[
                    [0, COLORS["error"]],
                    [0.5, COLORS["warning"]],
                    [1, COLORS["success"]],
                ],
                line=dict(width=0),
            ),
            text=[f"{p:.0f}%" for p in percentages],
            textposition="auto",
        )
    )
    fig.update_xaxes(range=[0, 100], showgrid=False)
    fig.update_yaxes(showgrid=False)
    return _base_layout(fig, "Subject Progress")


# ── Line Chart: Weekly Learning Trend ─────────────────────────

def weekly_trend_line(days: list[str], tasks_completed: list[int]) -> go.Figure:
    """Line chart showing daily task completion over the week."""
    fig = go.Figure(
        go.Scatter(
            x=days,
            y=tasks_completed,
            mode="lines+markers",
            line=dict(color=COLORS["primary"], width=3),
            marker=dict(size=10, color=COLORS["primary"]),
            fill="tozeroy",
            fillcolor="rgba(108, 99, 255, 0.15)",
        )
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor="rgba(255,255,255,0.05)")
    return _base_layout(fig, "Weekly Learning Trend")


# ── Gauge: Overall Progress ───────────────────────────────────

def overall_progress_gauge(value: float) -> go.Figure:
    """Gauge indicating overall learning completion."""
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=value,
            number=dict(suffix="%", font=dict(size=36, color=COLORS["text"])),
            gauge=dict(
                axis=dict(range=[0, 100], tickcolor=COLORS["text_muted"]),
                bar=dict(color=COLORS["primary"]),
                bgcolor=COLORS["surface"],
                bordercolor=COLORS["surface_light"],
                steps=[
                    dict(range=[0, 33], color="rgba(255,61,113,0.2)"),
                    dict(range=[33, 66], color="rgba(255,170,0,0.2)"),
                    dict(range=[66, 100], color="rgba(0,214,143,0.2)"),
                ],
            ),
        )
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color=COLORS["text_muted"]),
        margin=dict(l=30, r=30, t=30, b=10),
        height=250,
    )
    return fig


# ── Bar Chart: Module Completion per Subject ──────────────────

def module_completion_grouped(progress_data: list[dict]) -> go.Figure:
    """Grouped bar chart: completed vs total modules per subject."""
    subjects = [p["subject_name"] for p in progress_data]
    completed = [p["completed_modules"] for p in progress_data]
    total = [p["total_modules"] for p in progress_data]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Completed",
        x=subjects, y=completed,
        marker_color=COLORS["success"],
    ))
    fig.add_trace(go.Bar(
        name="Total",
        x=subjects, y=total,
        marker_color=COLORS["surface_light"],
    ))
    fig.update_layout(barmode="group")
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor="rgba(255,255,255,0.05)")
    return _base_layout(fig, "Module Completion by Subject")
