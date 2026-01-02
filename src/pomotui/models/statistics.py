"""Statistics models and calculations."""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Dict, Optional

from pomotui.models import Task, Session


@dataclass
class DailyStats:
    """Statistics for a single day."""

    date: datetime
    total_pomodoros: int = 0
    total_duration: int = 0  # in seconds
    work_sessions: int = 0
    break_sessions: int = 0
    completed_sessions: int = 0
    tasks_worked_on: int = 0

    @property
    def total_minutes(self) -> int:
        """Get total duration in minutes."""
        return self.total_duration // 60

    @property
    def total_hours(self) -> float:
        """Get total duration in hours."""
        return self.total_duration / 3600


@dataclass
class TaskStats:
    """Statistics for a single task."""

    task: Task
    total_sessions: int = 0
    total_duration: int = 0  # in seconds
    first_session: Optional[datetime] = None
    last_session: Optional[datetime] = None

    @property
    def total_minutes(self) -> int:
        """Get total duration in minutes."""
        return self.total_duration // 60

    @property
    def average_session_duration(self) -> int:
        """Get average session duration in seconds."""
        if self.total_sessions == 0:
            return 0
        return self.total_duration // self.total_sessions


@dataclass
class PeriodStats:
    """Statistics for a time period."""

    start_date: datetime
    end_date: datetime
    total_pomodoros: int = 0
    total_duration: int = 0  # in seconds
    work_sessions: int = 0
    break_sessions: int = 0
    completed_sessions: int = 0
    daily_stats: List[DailyStats] = None
    task_stats: List[TaskStats] = None

    def __post_init__(self) -> None:
        """Initialize lists."""
        if self.daily_stats is None:
            self.daily_stats = []
        if self.task_stats is None:
            self.task_stats = []

    @property
    def total_minutes(self) -> int:
        """Get total duration in minutes."""
        return self.total_duration // 60

    @property
    def total_hours(self) -> float:
        """Get total duration in hours."""
        return self.total_duration / 3600

    @property
    def average_pomodoros_per_day(self) -> float:
        """Get average pomodoros per day."""
        days = (self.end_date - self.start_date).days + 1
        if days == 0:
            return 0
        return self.total_pomodoros / days

    @property
    def most_productive_day(self) -> Optional[DailyStats]:
        """Get the most productive day."""
        if not self.daily_stats:
            return None
        return max(self.daily_stats, key=lambda d: d.total_pomodoros)

    @property
    def top_tasks(self) -> List[TaskStats]:
        """Get top 5 tasks by pomodoro count."""
        if not self.task_stats:
            return []
        return sorted(
            self.task_stats, key=lambda t: t.task.pomodoro_count, reverse=True
        )[:5]


class StatisticsCalculator:
    """Calculate statistics from sessions and tasks."""

    @staticmethod
    def calculate_daily_stats(
        sessions: List[Session], date: datetime
    ) -> DailyStats:
        """Calculate statistics for a specific day.

        Args:
            sessions: List of all sessions
            date: Date to calculate stats for

        Returns:
            DailyStats for the specified date
        """
        stats = DailyStats(date=date)

        # Filter sessions for this day
        day_start = datetime(date.year, date.month, date.day, 0, 0, 0)
        day_end = datetime(date.year, date.month, date.day, 23, 59, 59)

        day_sessions = [
            s
            for s in sessions
            if day_start <= s.start_time <= day_end
        ]

        task_ids = set()
        for session in day_sessions:
            stats.total_duration += session.duration

            if session.session_type == "work":
                stats.work_sessions += 1
                stats.total_pomodoros += 1
                if session.task_id:
                    task_ids.add(session.task_id)
            else:
                stats.break_sessions += 1

            if session.completed:
                stats.completed_sessions += 1

        stats.tasks_worked_on = len(task_ids)
        return stats

    @staticmethod
    def calculate_period_stats(
        sessions: List[Session],
        tasks: List[Task],
        start_date: datetime,
        end_date: datetime,
    ) -> PeriodStats:
        """Calculate statistics for a time period.

        Args:
            sessions: List of all sessions
            tasks: List of all tasks
            start_date: Start of period
            end_date: End of period

        Returns:
            PeriodStats for the specified period
        """
        stats = PeriodStats(start_date=start_date, end_date=end_date)

        # Filter sessions for this period
        period_sessions = [
            s
            for s in sessions
            if start_date <= s.start_time <= end_date
        ]

        # Calculate overall stats
        for session in period_sessions:
            stats.total_duration += session.duration

            if session.session_type == "work":
                stats.work_sessions += 1
                stats.total_pomodoros += 1
            else:
                stats.break_sessions += 1

            if session.completed:
                stats.completed_sessions += 1

        # Calculate daily stats
        current_date = start_date
        while current_date <= end_date:
            daily = StatisticsCalculator.calculate_daily_stats(
                period_sessions, current_date
            )
            stats.daily_stats.append(daily)
            current_date += timedelta(days=1)

        # Calculate task stats
        task_sessions: Dict[int, List[Session]] = {}
        for session in period_sessions:
            if session.task_id and session.session_type == "work":
                if session.task_id not in task_sessions:
                    task_sessions[session.task_id] = []
                task_sessions[session.task_id].append(session)

        for task in tasks:
            if task.id in task_sessions:
                task_session_list = task_sessions[task.id]
                task_stat = TaskStats(
                    task=task,
                    total_sessions=len(task_session_list),
                    total_duration=sum(s.duration for s in task_session_list),
                    first_session=min(s.start_time for s in task_session_list),
                    last_session=max(s.start_time for s in task_session_list),
                )
                stats.task_stats.append(task_stat)

        return stats

    @staticmethod
    def get_today_stats(sessions: List[Session]) -> DailyStats:
        """Get statistics for today.

        Args:
            sessions: List of all sessions

        Returns:
            DailyStats for today
        """
        return StatisticsCalculator.calculate_daily_stats(sessions, datetime.now())

    @staticmethod
    def get_week_stats(
        sessions: List[Session], tasks: List[Task]
    ) -> PeriodStats:
        """Get statistics for the current week.

        Args:
            sessions: List of all sessions
            tasks: List of all tasks

        Returns:
            PeriodStats for current week
        """
        today = datetime.now()
        start_of_week = today - timedelta(days=today.weekday())
        start_of_week = datetime(
            start_of_week.year, start_of_week.month, start_of_week.day, 0, 0, 0
        )
        end_of_week = start_of_week + timedelta(days=6, hours=23, minutes=59, seconds=59)

        return StatisticsCalculator.calculate_period_stats(
            sessions, tasks, start_of_week, end_of_week
        )

    @staticmethod
    def get_month_stats(
        sessions: List[Session], tasks: List[Task]
    ) -> PeriodStats:
        """Get statistics for the current month.

        Args:
            sessions: List of all sessions
            tasks: List of all tasks

        Returns:
            PeriodStats for current month
        """
        today = datetime.now()
        start_of_month = datetime(today.year, today.month, 1, 0, 0, 0)

        # Get last day of month
        if today.month == 12:
            end_of_month = datetime(today.year, 12, 31, 23, 59, 59)
        else:
            next_month = datetime(today.year, today.month + 1, 1, 0, 0, 0)
            end_of_month = next_month - timedelta(seconds=1)

        return StatisticsCalculator.calculate_period_stats(
            sessions, tasks, start_of_month, end_of_month
        )
