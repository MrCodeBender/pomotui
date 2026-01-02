"""Task model for tracking work items."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Task:
    """Represents a task that can be tracked with Pomodoros."""

    id: Optional[int] = None
    name: str = ""
    description: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    color: str = "blue"
    pomodoro_count: int = 0

    @property
    def is_completed(self) -> bool:
        """Check if task is completed."""
        return self.completed_at is not None

    def complete(self) -> None:
        """Mark task as completed."""
        if not self.is_completed:
            self.completed_at = datetime.now()

    def uncomplete(self) -> None:
        """Mark task as not completed."""
        self.completed_at = None

    def increment_pomodoros(self) -> None:
        """Increment the pomodoro count for this task."""
        self.pomodoro_count += 1

    def to_dict(self) -> dict:
        """Convert task to dictionary for database storage."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "color": self.color,
            "pomodoro_count": self.pomodoro_count,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        """Create task from dictionary."""
        return cls(
            id=data.get("id"),
            name=data.get("name", ""),
            description=data.get("description", ""),
            created_at=datetime.fromisoformat(data["created_at"])
            if isinstance(data.get("created_at"), str)
            else data.get("created_at", datetime.now()),
            completed_at=datetime.fromisoformat(data["completed_at"])
            if data.get("completed_at")
            else None,
            color=data.get("color", "blue"),
            pomodoro_count=data.get("pomodoro_count", 0),
        )


@dataclass
class Session:
    """Represents a completed Pomodoro session."""

    id: Optional[int] = None
    task_id: Optional[int] = None
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    duration: int = 0  # Duration in seconds
    completed: bool = False
    session_type: str = "work"  # work, short_break, long_break

    @property
    def actual_duration(self) -> int:
        """Calculate actual duration if end_time is set."""
        if self.end_time and self.start_time:
            return int((self.end_time - self.start_time).total_seconds())
        return self.duration

    def to_dict(self) -> dict:
        """Convert session to dictionary for database storage."""
        return {
            "id": self.id,
            "task_id": self.task_id,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration": self.duration,
            "completed": self.completed,
            "session_type": self.session_type,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Session":
        """Create session from dictionary."""
        return cls(
            id=data.get("id"),
            task_id=data.get("task_id"),
            start_time=datetime.fromisoformat(data["start_time"])
            if isinstance(data.get("start_time"), str)
            else data.get("start_time", datetime.now()),
            end_time=datetime.fromisoformat(data["end_time"])
            if data.get("end_time")
            else None,
            duration=data.get("duration", 0),
            completed=data.get("completed", False),
            session_type=data.get("session_type", "work"),
        )
