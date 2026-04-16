"""
Task data-model helpers.
"""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Task:
    """Represents a study task."""
    task_id: str = ""
    user_id: str = ""
    subject_id: str = ""
    task_name: str = ""
    due_date: str = ""
    status: str = "Pending"
    estimated_hours: float = 1.0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        return cls(
            task_id=data.get("task_id", ""),
            user_id=data.get("user_id", ""),
            subject_id=data.get("subject_id", ""),
            task_name=data.get("task_name", ""),
            due_date=data.get("due_date", ""),
            status=data.get("status", "Pending"),
            estimated_hours=data.get("estimated_hours", 1.0),
            created_at=data.get("created_at", ""),
        )
