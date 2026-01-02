"""Tests for statistics calculations."""

from datetime import datetime, timedelta

import pytest

from pomotui.models import Task, Session, StatisticsCalculator, DailyStats, PeriodStats


def create_test_session(
    task_id: int | None,
    start_time: datetime,
    duration: int = 1500,
    session_type: str = "work",
    completed: bool = True,
) -> Session:
    """Helper to create a test session."""
    return Session(
        task_id=task_id,
        start_time=start_time,
        end_time=start_time + timedelta(seconds=duration) if completed else None,
        duration=duration,
        completed=completed,
        session_type=session_type,
    )


def test_daily_stats_calculation() -> None:
    """Test calculating daily statistics."""
    today = datetime.now()
    yesterday = today - timedelta(days=1)

    sessions = [
        create_test_session(1, today, 1500, "work"),
        create_test_session(1, today, 300, "short_break"),
        create_test_session(2, today, 1500, "work"),
        create_test_session(None, yesterday, 1500, "work"),  # Should be excluded
    ]

    stats = StatisticsCalculator.calculate_daily_stats(sessions, today)

    assert stats.total_pomodoros == 2
    assert stats.work_sessions == 2
    assert stats.break_sessions == 1
    assert stats.completed_sessions == 3
    assert stats.tasks_worked_on == 2
    assert stats.total_duration == 3300  # 1500 + 300 + 1500


def test_daily_stats_properties() -> None:
    """Test daily stats property calculations."""
    stats = DailyStats(
        date=datetime.now(), total_duration=3600  # 1 hour in seconds
    )

    assert stats.total_minutes == 60
    assert stats.total_hours == 1.0


def test_period_stats_calculation() -> None:
    """Test calculating period statistics."""
    start_date = datetime(2024, 1, 1, 0, 0, 0)
    end_date = datetime(2024, 1, 7, 23, 59, 59)

    task1 = Task(id=1, name="Task 1", pomodoro_count=5)
    task2 = Task(id=2, name="Task 2", pomodoro_count=3)
    tasks = [task1, task2]

    sessions = [
        create_test_session(1, datetime(2024, 1, 1, 10, 0), 1500, "work"),
        create_test_session(1, datetime(2024, 1, 1, 11, 0), 1500, "work"),
        create_test_session(2, datetime(2024, 1, 2, 10, 0), 1500, "work"),
        create_test_session(None, datetime(2024, 1, 3, 10, 0), 300, "short_break"),
        create_test_session(1, datetime(2024, 1, 10, 10, 0), 1500, "work"),  # Excluded
    ]

    stats = StatisticsCalculator.calculate_period_stats(
        sessions, tasks, start_date, end_date
    )

    assert stats.total_pomodoros == 3
    assert stats.work_sessions == 3
    assert stats.break_sessions == 1
    assert stats.total_duration == 4800  # 3*1500 + 300
    assert len(stats.daily_stats) == 7  # 7 days


def test_period_stats_properties() -> None:
    """Test period stats property calculations."""
    start_date = datetime(2024, 1, 1, 0, 0, 0)
    end_date = datetime(2024, 1, 7, 23, 59, 59)

    stats = PeriodStats(
        start_date=start_date,
        end_date=end_date,
        total_pomodoros=14,
        total_duration=7200,  # 2 hours
    )

    assert stats.total_minutes == 120
    assert stats.total_hours == 2.0
    assert stats.average_pomodoros_per_day == 2.0  # 14 / 7


def test_most_productive_day() -> None:
    """Test finding the most productive day."""
    start_date = datetime(2024, 1, 1, 0, 0, 0)
    end_date = datetime(2024, 1, 3, 23, 59, 59)

    sessions = [
        create_test_session(1, datetime(2024, 1, 1, 10, 0), 1500, "work"),
        create_test_session(1, datetime(2024, 1, 2, 10, 0), 1500, "work"),
        create_test_session(1, datetime(2024, 1, 2, 11, 0), 1500, "work"),
        create_test_session(1, datetime(2024, 1, 2, 12, 0), 1500, "work"),
        create_test_session(1, datetime(2024, 1, 3, 10, 0), 1500, "work"),
    ]

    stats = StatisticsCalculator.calculate_period_stats(
        sessions, [], start_date, end_date
    )

    most_productive = stats.most_productive_day
    assert most_productive is not None
    assert most_productive.date.day == 2  # Jan 2nd had 3 pomodoros
    assert most_productive.total_pomodoros == 3


def test_top_tasks() -> None:
    """Test getting top tasks."""
    task1 = Task(id=1, name="Task 1", pomodoro_count=10)
    task2 = Task(id=2, name="Task 2", pomodoro_count=5)
    task3 = Task(id=3, name="Task 3", pomodoro_count=15)
    task4 = Task(id=4, name="Task 4", pomodoro_count=3)
    tasks = [task1, task2, task3, task4]

    start_date = datetime(2024, 1, 1, 0, 0, 0)
    end_date = datetime(2024, 1, 31, 23, 59, 59)

    sessions = [
        create_test_session(1, datetime(2024, 1, 1, 10, 0), 1500, "work"),
        create_test_session(2, datetime(2024, 1, 2, 10, 0), 1500, "work"),
        create_test_session(3, datetime(2024, 1, 3, 10, 0), 1500, "work"),
        create_test_session(4, datetime(2024, 1, 4, 10, 0), 1500, "work"),
    ]

    stats = StatisticsCalculator.calculate_period_stats(
        sessions, tasks, start_date, end_date
    )

    top_tasks = stats.top_tasks
    assert len(top_tasks) <= 5
    assert top_tasks[0].task.name == "Task 3"  # 15 pomodoros
    assert top_tasks[1].task.name == "Task 1"  # 10 pomodoros


def test_get_today_stats() -> None:
    """Test getting today's statistics."""
    today = datetime.now()
    yesterday = today - timedelta(days=1)

    sessions = [
        create_test_session(1, today, 1500, "work"),
        create_test_session(1, today, 1500, "work"),
        create_test_session(None, yesterday, 1500, "work"),  # Should be excluded
    ]

    stats = StatisticsCalculator.get_today_stats(sessions)

    assert stats.total_pomodoros == 2
    assert stats.date.date() == today.date()


def test_get_week_stats() -> None:
    """Test getting week statistics."""
    today = datetime.now()
    start_of_week = today - timedelta(days=today.weekday())

    task = Task(id=1, name="Task 1", pomodoro_count=5)

    sessions = [
        create_test_session(1, start_of_week, 1500, "work"),
        create_test_session(1, start_of_week + timedelta(days=1), 1500, "work"),
        create_test_session(1, start_of_week - timedelta(days=8), 1500, "work"),  # Excluded
    ]

    stats = StatisticsCalculator.get_week_stats(sessions, [task])

    assert stats.total_pomodoros == 2
    assert len(stats.daily_stats) == 7


def test_get_month_stats() -> None:
    """Test getting month statistics."""
    today = datetime.now()
    start_of_month = datetime(today.year, today.month, 1, 0, 0, 0)

    task = Task(id=1, name="Task 1", pomodoro_count=10)

    sessions = [
        create_test_session(1, start_of_month, 1500, "work"),
        create_test_session(1, start_of_month + timedelta(days=5), 1500, "work"),
        create_test_session(1, start_of_month - timedelta(days=32), 1500, "work"),  # Excluded
    ]

    stats = StatisticsCalculator.get_month_stats(sessions, [task])

    assert stats.total_pomodoros == 2
    assert stats.start_date.month == today.month


def test_task_stats_properties() -> None:
    """Test task stats property calculations."""
    from pomotui.models import TaskStats

    task = Task(id=1, name="Test Task")
    task_stats = TaskStats(
        task=task,
        total_sessions=4,
        total_duration=6000,  # 100 minutes
    )

    assert task_stats.total_minutes == 100
    assert task_stats.average_session_duration == 1500  # 6000 / 4


def test_empty_statistics() -> None:
    """Test statistics with no sessions."""
    today = datetime.now()
    stats = StatisticsCalculator.calculate_daily_stats([], today)

    assert stats.total_pomodoros == 0
    assert stats.total_duration == 0
    assert stats.tasks_worked_on == 0


def test_incomplete_sessions() -> None:
    """Test handling incomplete sessions."""
    today = datetime.now()

    sessions = [
        create_test_session(1, today, 1500, "work", completed=True),
        create_test_session(1, today, 1500, "work", completed=False),
    ]

    stats = StatisticsCalculator.calculate_daily_stats(sessions, today)

    assert stats.total_pomodoros == 2  # Both count as pomodoros
    assert stats.completed_sessions == 1  # Only one completed
