"""Tests for Task and Session models."""

from datetime import datetime

from pomotui.models import Task, Session


def test_task_creation() -> None:
    """Test creating a task."""
    task = Task(name="Test Task", description="Test Description")

    assert task.name == "Test Task"
    assert task.description == "Test Description"
    assert task.is_completed is False
    assert task.pomodoro_count == 0


def test_task_complete() -> None:
    """Test completing a task."""
    task = Task(name="Test Task")
    assert not task.is_completed

    task.complete()
    assert task.is_completed
    assert task.completed_at is not None


def test_task_uncomplete() -> None:
    """Test uncompleting a task."""
    task = Task(name="Test Task")
    task.complete()
    assert task.is_completed

    task.uncomplete()
    assert not task.is_completed
    assert task.completed_at is None


def test_task_increment_pomodoros() -> None:
    """Test incrementing pomodoro count."""
    task = Task(name="Test Task")
    assert task.pomodoro_count == 0

    task.increment_pomodoros()
    assert task.pomodoro_count == 1

    task.increment_pomodoros()
    assert task.pomodoro_count == 2


def test_task_to_dict() -> None:
    """Test converting task to dictionary."""
    task = Task(
        id=1,
        name="Test Task",
        description="Description",
        color="blue",
        pomodoro_count=5,
    )

    task_dict = task.to_dict()

    assert task_dict["id"] == 1
    assert task_dict["name"] == "Test Task"
    assert task_dict["description"] == "Description"
    assert task_dict["color"] == "blue"
    assert task_dict["pomodoro_count"] == 5


def test_task_from_dict() -> None:
    """Test creating task from dictionary."""
    created_at = datetime.now()
    task_dict = {
        "id": 1,
        "name": "Test Task",
        "description": "Description",
        "created_at": created_at.isoformat(),
        "completed_at": None,
        "color": "blue",
        "pomodoro_count": 3,
    }

    task = Task.from_dict(task_dict)

    assert task.id == 1
    assert task.name == "Test Task"
    assert task.description == "Description"
    assert task.color == "blue"
    assert task.pomodoro_count == 3
    assert not task.is_completed


def test_session_creation() -> None:
    """Test creating a session."""
    session = Session(task_id=1, duration=1500, session_type="work", completed=True)

    assert session.task_id == 1
    assert session.duration == 1500
    assert session.session_type == "work"
    assert session.completed is True


def test_session_actual_duration() -> None:
    """Test calculating actual duration."""
    from datetime import timedelta

    start = datetime.now()
    end = start + timedelta(seconds=100)

    session = Session(start_time=start, end_time=end, duration=1500)

    # Actual duration should be close to 100 seconds
    assert 95 <= session.actual_duration <= 105


def test_session_to_dict() -> None:
    """Test converting session to dictionary."""
    session = Session(
        id=1,
        task_id=2,
        duration=1500,
        completed=True,
        session_type="work",
    )

    session_dict = session.to_dict()

    assert session_dict["id"] == 1
    assert session_dict["task_id"] == 2
    assert session_dict["duration"] == 1500
    assert session_dict["completed"] is True
    assert session_dict["session_type"] == "work"


def test_session_from_dict() -> None:
    """Test creating session from dictionary."""
    start_time = datetime.now()
    session_dict = {
        "id": 1,
        "task_id": 5,
        "start_time": start_time.isoformat(),
        "end_time": None,
        "duration": 1500,
        "completed": False,
        "session_type": "work",
    }

    session = Session.from_dict(session_dict)

    assert session.id == 1
    assert session.task_id == 5
    assert session.duration == 1500
    assert session.completed is False
    assert session.session_type == "work"
