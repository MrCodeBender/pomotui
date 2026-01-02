"""Tests for task selection functionality."""

import tempfile
from pathlib import Path

from pomotui.database import DatabaseManager
from pomotui.models import Task


def test_current_task_persistence() -> None:
    """Test that current task is saved and loaded correctly."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = Path(f.name)

    try:
        # Initialize database
        from pomotui.database.schema import initialize_database

        initialize_database(db_path)

        db = DatabaseManager(db_path)

        # Create a task
        task = db.create_task(name="Test Task", description="Test description")
        assert task.id is not None

        # Save as current task
        db.set_setting("current_task_id", str(task.id))

        # Verify it was saved
        saved_id = db.get_setting("current_task_id")
        assert saved_id == str(task.id)

        # Close and reopen database
        db.close()
        db = DatabaseManager(db_path)

        # Load current task
        current_task_id_str = db.get_setting("current_task_id")
        assert current_task_id_str == str(task.id)

        # Verify we can retrieve the task
        loaded_task = db.get_task(int(current_task_id_str))
        assert loaded_task is not None
        assert loaded_task.name == "Test Task"
        assert loaded_task.description == "Test description"

        db.close()
    finally:
        db_path.unlink()


def test_clear_current_task() -> None:
    """Test clearing the current task."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = Path(f.name)

    try:
        from pomotui.database.schema import initialize_database

        initialize_database(db_path)

        db = DatabaseManager(db_path)

        # Create a task
        task = db.create_task(name="Test Task")
        db.set_setting("current_task_id", str(task.id))

        # Verify it's set
        assert db.get_setting("current_task_id") == str(task.id)

        # Clear it
        db.set_setting("current_task_id", "")

        # Verify it's cleared
        current_id = db.get_setting("current_task_id")
        assert current_id == ""

        db.close()
    finally:
        db_path.unlink()


def test_task_display_with_name() -> None:
    """Test that task name is included in timer display update."""
    from pomotui.widgets import TimerDisplay
    from pomotui.timer import TimerState

    display = TimerDisplay()

    # Update with no task
    display.update_timer(
        time_str="25:00", state=TimerState.WORKING, progress=0.0, pomodoros=0, task_name=""
    )
    assert display.task_text == ""

    # Update with task
    display.update_timer(
        time_str="24:30",
        state=TimerState.WORKING,
        progress=10.0,
        pomodoros=0,
        task_name="My Task",
    )
    assert display.task_text == "📋 My Task"


def test_task_item_has_task_data() -> None:
    """Test that TaskItem stores task data correctly."""
    from pomotui.widgets.task_list import TaskItem
    from pomotui.models import Task

    task = Task(id=1, name="Test Task", pomodoro_count=3)
    item = TaskItem(task, is_selected=False)

    # Verify task data is stored
    assert item._task_data.id == 1
    assert item._task_data.name == "Test Task"
    assert item._task_data.pomodoro_count == 3

    # Test selected state
    item_selected = TaskItem(task, is_selected=True)
    assert item_selected.is_selected is True
    assert "selected" in item_selected.classes


def test_task_list_updates_selection() -> None:
    """Test that TaskList updates selected_task_id when task is selected."""
    from pomotui.widgets import TaskList
    from pomotui.widgets.task_list import TaskItem
    from pomotui.models import Task

    tasks = [
        Task(id=1, name="Task 1", pomodoro_count=0),
        Task(id=2, name="Task 2", pomodoro_count=0),
    ]

    task_list = TaskList(tasks)
    task_list.tasks = tasks

    # Initially no selection
    assert task_list.selected_task_id is None

    # Simulate task selection
    selected_message = TaskItem.Selected(tasks[1])
    task_list.on_task_item_selected(selected_message)

    # Verify selected_task_id was updated
    assert task_list.selected_task_id == 2
