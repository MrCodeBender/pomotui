"""Tests for database functionality."""

import tempfile
from pathlib import Path

import pytest

from pomotui.database import DatabaseManager
from pomotui.models import Task, Session


@pytest.fixture
def db() -> DatabaseManager:
    """Create a temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = Path(f.name)

    # Initialize database schema
    from pomotui.database.schema import initialize_database

    initialize_database(db_path)

    db = DatabaseManager(db_path)
    yield db
    db.close()
    db_path.unlink()


def test_create_task(db: DatabaseManager) -> None:
    """Test creating a task."""
    task = db.create_task("Test Task", "Test Description", "blue")

    assert task.id is not None
    assert task.name == "Test Task"
    assert task.description == "Test Description"
    assert task.color == "blue"
    assert task.pomodoro_count == 0


def test_get_task(db: DatabaseManager) -> None:
    """Test getting a task by ID."""
    created_task = db.create_task("Get Test")
    retrieved_task = db.get_task(created_task.id)

    assert retrieved_task is not None
    assert retrieved_task.id == created_task.id
    assert retrieved_task.name == created_task.name


def test_get_nonexistent_task(db: DatabaseManager) -> None:
    """Test getting a task that doesn't exist."""
    task = db.get_task(999)
    assert task is None


def test_get_all_tasks(db: DatabaseManager) -> None:
    """Test getting all tasks."""
    db.create_task("Task 1")
    db.create_task("Task 2")
    db.create_task("Task 3")

    tasks = db.get_all_tasks()
    assert len(tasks) == 3


def test_get_all_tasks_exclude_completed(db: DatabaseManager) -> None:
    """Test getting tasks excluding completed ones."""
    task1 = db.create_task("Task 1")
    task2 = db.create_task("Task 2")

    # Complete task1
    task1.complete()
    db.update_task(task1)

    active_tasks = db.get_all_tasks(include_completed=False)
    assert len(active_tasks) == 1
    assert active_tasks[0].id == task2.id


def test_update_task(db: DatabaseManager) -> None:
    """Test updating a task."""
    task = db.create_task("Original Name")
    task.name = "Updated Name"
    task.description = "Updated Description"

    db.update_task(task)

    retrieved_task = db.get_task(task.id)
    assert retrieved_task.name == "Updated Name"
    assert retrieved_task.description == "Updated Description"


def test_delete_task(db: DatabaseManager) -> None:
    """Test deleting a task."""
    task = db.create_task("To Delete")
    task_id = task.id

    db.delete_task(task_id)

    retrieved_task = db.get_task(task_id)
    assert retrieved_task is None


def test_increment_task_pomodoros(db: DatabaseManager) -> None:
    """Test incrementing task pomodoro count."""
    task = db.create_task("Pomodoro Task")
    assert task.pomodoro_count == 0

    db.increment_task_pomodoros(task.id)
    updated_task = db.get_task(task.id)
    assert updated_task.pomodoro_count == 1

    db.increment_task_pomodoros(task.id)
    updated_task = db.get_task(task.id)
    assert updated_task.pomodoro_count == 2


def test_create_session(db: DatabaseManager) -> None:
    """Test creating a session."""
    task = db.create_task("Session Task")
    session = db.create_session(
        task_id=task.id, duration=1500, session_type="work", completed=True
    )

    assert session.id is not None
    assert session.task_id == task.id
    assert session.duration == 1500
    assert session.session_type == "work"
    assert session.completed is True


def test_create_session_without_task(db: DatabaseManager) -> None:
    """Test creating a session without an associated task."""
    session = db.create_session(
        task_id=None, duration=300, session_type="short_break", completed=True
    )

    assert session.id is not None
    assert session.task_id is None
    assert session.session_type == "short_break"


def test_get_session(db: DatabaseManager) -> None:
    """Test getting a session by ID."""
    created_session = db.create_session(None, 1500, "work")
    retrieved_session = db.get_session(created_session.id)

    assert retrieved_session is not None
    assert retrieved_session.id == created_session.id
    assert retrieved_session.duration == 1500


def test_get_sessions_for_task(db: DatabaseManager) -> None:
    """Test getting all sessions for a specific task."""
    task = db.create_task("Multi Session Task")

    db.create_session(task.id, 1500, "work")
    db.create_session(task.id, 1500, "work")
    db.create_session(None, 300, "short_break")  # Different task

    sessions = db.get_sessions_for_task(task.id)
    assert len(sessions) == 2


def test_get_all_sessions(db: DatabaseManager) -> None:
    """Test getting all sessions."""
    db.create_session(None, 1500, "work")
    db.create_session(None, 300, "short_break")
    db.create_session(None, 900, "long_break")

    sessions = db.get_all_sessions()
    assert len(sessions) == 3


def test_get_session_stats(db: DatabaseManager) -> None:
    """Test getting session statistics."""
    db.create_session(None, 1500, "work", completed=True)
    db.create_session(None, 1500, "work", completed=True)
    db.create_session(None, 300, "short_break", completed=True)
    db.create_session(None, 1500, "work", completed=False)

    stats = db.get_session_stats()
    assert stats["total_sessions"] == 4
    assert stats["work_sessions"] == 3
    assert stats["completed_sessions"] == 3
    assert stats["total_duration"] == 4800


def test_settings(db: DatabaseManager) -> None:
    """Test setting and getting settings."""
    db.set_setting("test_key", "test_value")
    value = db.get_setting("test_key")
    assert value == "test_value"

    db.set_setting("test_key", "updated_value")
    value = db.get_setting("test_key")
    assert value == "updated_value"


def test_get_nonexistent_setting(db: DatabaseManager) -> None:
    """Test getting a setting that doesn't exist."""
    value = db.get_setting("nonexistent")
    assert value is None
