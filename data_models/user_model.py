"""
User data-model helpers.
"""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class User:
    """Represents a registered student."""
    user_id: str = ""
    name: str = ""
    email: str = ""
    password_hash: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    @classmethod
    def from_dict(cls, data: dict) -> "User":
        return cls(
            user_id=data.get("user_id", ""),
            name=data.get("name", ""),
            email=data.get("email", ""),
            password_hash=data.get("password_hash", ""),
            created_at=data.get("created_at", ""),
        )

    def to_display_dict(self) -> dict:
        return {
            "Name": self.name,
            "Email": self.email,
            "Member Since": self.created_at[:10] if self.created_at else "",
        }
