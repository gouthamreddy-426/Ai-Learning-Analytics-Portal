"""
Subject data-model helpers.
"""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Subject:
    """Represents an enrolled subject."""
    subject_id: str = ""
    user_id: str = ""
    subject_name: str = ""
    difficulty_level: str = "Medium"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    @classmethod
    def from_dict(cls, data: dict) -> "Subject":
        return cls(
            subject_id=data.get("subject_id", ""),
            user_id=data.get("user_id", ""),
            subject_name=data.get("subject_name", ""),
            difficulty_level=data.get("difficulty_level", "Medium"),
            created_at=data.get("created_at", ""),
        )


@dataclass
class SubjectModule:
    """Represents a learning module inside a subject."""
    module_id: str = ""
    subject_id: str = ""
    module_title: str = ""
    module_order: int = 0
    difficulty_level: str = "Medium"
    is_completed: bool = False
    completed_at: str | None = None

    @classmethod
    def from_dict(cls, data: dict) -> "SubjectModule":
        return cls(
            module_id=data.get("module_id", ""),
            subject_id=data.get("subject_id", ""),
            module_title=data.get("module_title", ""),
            module_order=data.get("module_order", 0),
            difficulty_level=data.get("difficulty_level", "Medium"),
            is_completed=data.get("is_completed", False),
            completed_at=data.get("completed_at"),
        )
