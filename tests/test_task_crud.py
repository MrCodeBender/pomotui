"""Tests for task CRUD operations."""

import tempfile
from pathlib import Path
from datetime import datetime

from pomotui.database import DatabaseManager
from pomotui.models import Task


def test_update_task() -> None:
    """Test updating a task."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = Path(f.name)

    try:
        from pomotui.database.schema import initialize_database

        initialize_database(db_path)
        db = DatabaseManager(db_path)

        # Create a task
        task = db.create_task(name="Original Name", description="Original description")
        assert task.id is not None
        original_id = task.id

        # Update the task
        task.name = "Updated Name"
        task.description = "Updated description"
        task.complete()
        db.update_task(task)

        # Retrieve and verify
        updated_task = db.get_task(original_id)
        assert updated_task is not None
        assert updated_task.id == original_id
        assert updated_task.name == "Updated Name"
        assert updated_task.description == "Updated description"
        assert updated_task.is_completed is True

        db.close()
    finally:
        db_path.unlink()


def test_delete_task() -> None:
    """Test deleting a task."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = Path(f.name)

    try:
        from pomotui.database.schema import initialize_database

        initialize_database(db_path)
        db = DatabaseManager(db_path)

        # Create a task
        task = db.create_task(name="Task to Delete", description="Will be deleted")
        assert task.id is not None
        task_id = task.id

        # Verify it exists
        retrieved_task = db.get_task(task_id)
        assert retrieved_task is not None

        # Delete the task
        db.delete_task(task_id)

        # Verify it's deleted
        deleted_task = db.get_task(task_id)
        assert deleted_task is None

        db.close()
    finally:
        db_path.unlink()


def test_update_task_pomodoro_count() -> None:
    """Test updating task pomodoro count."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = Path(f.name)

    try:
        from pomotui.database.schema import initialize_database

        initialize_database(db_path)
        db = DatabaseManager(db_path)

        # Create a task
        task = db.create_task(name="Test Task")
        assert task.id is not None
        assert task.pomodoro_count == 0

        # Update pomodoro count
        task.pomodoro_count = 5
        db.update_task(task)

        # Retrieve and verify
        updated_task = db.get_task(task.id)
        assert updated_task is not None
        assert updated_task.pomodoro_count == 5

        db.close()
    finally:
        db_path.unlink()


def test_task_edit_screen_initialization() -> None:
    """Test TaskEditScreen initializes with task data."""
    from pomotui.screens import TaskEditScreen

    task = Task(
        id=1,
        name="Test Task",
        description="Test description",
        created_at=datetime.now(),
        pomodoro_count=3
    )

    screen = TaskEditScreen(task)

    assert screen._task == task
    assert screen.task_name == "Test Task"
    assert screen.task_description == "Test description"
    assert screen.should_complete is False


def test_confirm_dialog_initialization() -> None:
    """Test ConfirmDialog initializes with correct data."""
    from pomotui.screens import ConfirmDialog

    dialog = ConfirmDialog(
        title="Delete Task",
        message="Are you sure?"
    )

    assert dialog.title_text == "Delete Task"
    assert dialog.message_text == "Are you sure?"


def test_delete_task_with_sessions() -> None:
    """Test deleting a task also deletes associated sessions."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = Path(f.name)

    try:
        from pomotui.database.schema import initialize_database

        initialize_database(db_path)
        db = DatabaseManager(db_path)

        # Create a task
        task = db.create_task(name="Task with Sessions")
        assert task.id is not None

        # Create sessions for the task
        session1 = db.create_session(
            task_id=task.id,
            duration=1500,
            session_type="work",
            completed=True
        )
        session2 = db.create_session(
            task_id=task.id,
            duration=300,
            session_type="short_break",
            completed=True
        )

        # Verify sessions exist
        sessions = db.get_sessions_for_task(task.id)
        assert len(sessions) == 2

        # Delete the task
        db.delete_task(task.id)

        # Verify task is deleted
        deleted_task = db.get_task(task.id)
        assert deleted_task is None

        # Sessions are also deleted due to CASCADE
        sessions_after_delete = db.get_sessions_for_task(task.id)
        assert len(sessions_after_delete) == 0

        db.close()
    finally:
        db_path.unlink()


def test_update_task_completion_status() -> None:
    """Test marking a task as completed."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = Path(f.name)

    try:
        from pomotui.database.schema import initialize_database

        initialize_database(db_path)
        db = DatabaseManager(db_path)

        # Create a task
        task = db.create_task(name="Task to Complete")
        assert task.id is not None
        assert task.is_completed is False
        assert task.completed_at is None

        # Mark as completed
        task.complete()
        db.update_task(task)

        # Retrieve and verify
        completed_task = db.get_task(task.id)
        assert completed_task is not None
        assert completed_task.is_completed is True
        assert completed_task.completed_at is not None

        db.close()
    finally:
        db_path.unlink()
