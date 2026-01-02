"""Statistics and reports screen."""

from datetime import datetime

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import Button, DataTable, Label, Sparkline, Static, TabbedContent, TabPane

from pomotui.database import DatabaseManager
from pomotui.models import StatisticsCalculator, PeriodStats, DailyStats


class StatsScreen(Screen):
    """Screen for displaying statistics and reports."""

    BINDINGS = [
        ("escape", "dismiss_screen", "Back"),
        ("q", "dismiss_screen", "Back"),
    ]

    CSS = """
    StatsScreen {
        align: center top;
    }

    StatsScreen > Container {
        width: 90%;
        height: 90%;
        border: solid $primary;
        padding: 1;
    }

    StatsScreen .title {
        text-align: center;
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
    }

    StatsScreen .stat-card {
        border: solid $panel;
        padding: 1;
        margin: 1;
        height: auto;
    }

    StatsScreen .stat-label {
        color: $text-muted;
        text-style: italic;
    }

    StatsScreen .stat-value {
        text-style: bold;
        color: $success;
    }

    StatsScreen Button {
        width: 100%;
        margin-top: 1;
    }

    StatsScreen DataTable {
        height: auto;
        margin: 1;
    }

    StatsScreen Sparkline {
        height: 5;
        margin: 1;
    }
    """

    def __init__(self, db: DatabaseManager, *args, **kwargs) -> None:
        """Initialize statistics screen.

        Args:
            db: Database manager instance
        """
        super().__init__(*args, **kwargs)
        self.db = db

    def compose(self) -> ComposeResult:
        """Compose the statistics screen."""
        with Container():
            yield Static("📊 Statistics & Reports", classes="title")

            with TabbedContent():
                with TabPane("Today"):
                    with VerticalScroll():
                        yield from self._create_today_view()

                with TabPane("This Week"):
                    with VerticalScroll():
                        yield from self._create_week_view()

                with TabPane("This Month"):
                    with VerticalScroll():
                        yield from self._create_month_view()

                with TabPane("All Tasks"):
                    with VerticalScroll():
                        yield from self._create_tasks_view()

            with Horizontal():
                yield Button("Export CSV", variant="primary", id="export-csv-btn")
                yield Button("Export JSON", variant="default", id="export-json-btn")
                yield Button("Close (ESC)", variant="default", id="close-btn")

    def _create_today_view(self) -> ComposeResult:
        """Create today's statistics view."""
        sessions = self.db.get_all_sessions()
        today_stats = StatisticsCalculator.get_today_stats(sessions)

        with Horizontal():
            with Container(classes="stat-card"):
                yield Label("🍅 Pomodoros Today", classes="stat-label")
                yield Static(
                    str(today_stats.total_pomodoros), classes="stat-value"
                )

            with Container(classes="stat-card"):
                yield Label("⏱️ Total Time", classes="stat-label")
                yield Static(
                    f"{today_stats.total_minutes} min", classes="stat-value"
                )

            with Container(classes="stat-card"):
                yield Label("✅ Completed", classes="stat-label")
                yield Static(
                    str(today_stats.completed_sessions), classes="stat-value"
                )

        with Container(classes="stat-card"):
            yield Label("📋 Tasks Worked On", classes="stat-label")
            yield Static(str(today_stats.tasks_worked_on), classes="stat-value")

    def _create_week_view(self) -> ComposeResult:
        """Create week statistics view."""
        sessions = self.db.get_all_sessions()
        tasks = self.db.get_all_tasks()
        week_stats = StatisticsCalculator.get_week_stats(sessions, tasks)

        with Horizontal():
            with Container(classes="stat-card"):
                yield Label("🍅 Total Pomodoros", classes="stat-label")
                yield Static(str(week_stats.total_pomodoros), classes="stat-value")

            with Container(classes="stat-card"):
                yield Label("⏱️ Total Time", classes="stat-label")
                yield Static(
                    f"{week_stats.total_hours:.1f} hrs", classes="stat-value"
                )

            with Container(classes="stat-card"):
                yield Label("📊 Daily Average", classes="stat-label")
                yield Static(
                    f"{week_stats.average_pomodoros_per_day:.1f}",
                    classes="stat-value",
                )

        # Daily sparkline
        yield Label("Daily Pomodoros This Week:")
        daily_values = [day.total_pomodoros for day in week_stats.daily_stats]
        if any(daily_values):
            yield Sparkline(daily_values, summary_function=max)
        else:
            yield Static("No data yet", classes="stat-label")

        # Top tasks
        if week_stats.top_tasks:
            yield Label("Top Tasks:")
            table = DataTable()
            table.add_columns("Task", "Pomodoros", "Time")
            for task_stat in week_stats.top_tasks:
                table.add_row(
                    task_stat.task.name,
                    str(task_stat.task.pomodoro_count),
                    f"{task_stat.total_minutes} min",
                )
            yield table

    def _create_month_view(self) -> ComposeResult:
        """Create month statistics view."""
        sessions = self.db.get_all_sessions()
        tasks = self.db.get_all_tasks()
        month_stats = StatisticsCalculator.get_month_stats(sessions, tasks)

        with Horizontal():
            with Container(classes="stat-card"):
                yield Label("🍅 Total Pomodoros", classes="stat-label")
                yield Static(str(month_stats.total_pomodoros), classes="stat-value")

            with Container(classes="stat-card"):
                yield Label("⏱️ Total Time", classes="stat-label")
                yield Static(
                    f"{month_stats.total_hours:.1f} hrs", classes="stat-value"
                )

            with Container(classes="stat-card"):
                yield Label("📊 Daily Average", classes="stat-label")
                yield Static(
                    f"{month_stats.average_pomodoros_per_day:.1f}",
                    classes="stat-value",
                )

        # Most productive day
        if month_stats.most_productive_day:
            with Container(classes="stat-card"):
                yield Label("🏆 Most Productive Day", classes="stat-label")
                day = month_stats.most_productive_day
                yield Static(
                    f"{day.date.strftime('%A, %b %d')}: {day.total_pomodoros} 🍅",
                    classes="stat-value",
                )

        # Daily trend (last 30 days)
        yield Label("Daily Trend (This Month):")
        daily_values = [day.total_pomodoros for day in month_stats.daily_stats]
        if any(daily_values):
            yield Sparkline(daily_values, summary_function=max)
        else:
            yield Static("No data yet", classes="stat-label")

    def _create_tasks_view(self) -> ComposeResult:
        """Create tasks statistics view."""
        tasks = self.db.get_all_tasks(include_completed=True)
        sessions = self.db.get_all_sessions()

        yield Label("All Tasks Performance:")

        if tasks:
            table = DataTable()
            table.add_columns("Task", "Status", "Pomodoros", "Sessions")

            for task in tasks:
                task_sessions = [
                    s for s in sessions if s.task_id == task.id
                ]
                status = "✓" if task.is_completed else "○"

                table.add_row(
                    task.name,
                    status,
                    str(task.pomodoro_count),
                    str(len(task_sessions)),
                )

            yield table
        else:
            yield Static("No tasks yet", classes="stat-label")

    def action_dismiss_screen(self) -> None:
        """Dismiss the screen and return to main."""
        self.dismiss()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        if event.button.id == "close-btn":
            self.dismiss()
        elif event.button.id == "export-csv-btn":
            self._export_csv()
        elif event.button.id == "export-json-btn":
            self._export_json()

    def _export_csv(self) -> None:
        """Export statistics to CSV."""
        import csv
        from pathlib import Path

        export_dir = Path.home() / "Documents"
        export_dir.mkdir(parents=True, exist_ok=True)
        filepath = export_dir / f"pomotui_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        sessions = self.db.get_all_sessions()
        tasks = self.db.get_all_tasks(include_completed=True)

        with open(filepath, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(
                ["Session ID", "Task", "Start Time", "Duration (min)", "Type", "Completed"]
            )

            for session in sessions:
                task_name = ""
                if session.task_id:
                    task = next((t for t in tasks if t.id == session.task_id), None)
                    if task:
                        task_name = task.name

                writer.writerow([
                    session.id,
                    task_name,
                    session.start_time.strftime("%Y-%m-%d %H:%M:%S"),
                    session.duration // 60,
                    session.session_type,
                    "Yes" if session.completed else "No",
                ])

        self.notify(f"Exported to {filepath}", severity="information", timeout=5)

    def _export_json(self) -> None:
        """Export statistics to JSON."""
        import json
        from pathlib import Path

        export_dir = Path.home() / "Documents"
        export_dir.mkdir(parents=True, exist_ok=True)
        filepath = export_dir / f"pomotui_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        sessions = self.db.get_all_sessions()
        tasks = self.db.get_all_tasks(include_completed=True)
        week_stats = StatisticsCalculator.get_week_stats(sessions, tasks)
        month_stats = StatisticsCalculator.get_month_stats(sessions, tasks)

        export_data = {
            "export_date": datetime.now().isoformat(),
            "summary": {
                "total_tasks": len(tasks),
                "total_sessions": len(sessions),
                "week_pomodoros": week_stats.total_pomodoros,
                "month_pomodoros": month_stats.total_pomodoros,
            },
            "tasks": [
                {
                    "id": task.id,
                    "name": task.name,
                    "description": task.description,
                    "pomodoros": task.pomodoro_count,
                    "completed": task.is_completed,
                    "created_at": task.created_at.isoformat(),
                }
                for task in tasks
            ],
            "sessions": [session.to_dict() for session in sessions],
        }

        with open(filepath, "w") as f:
            json.dump(export_data, f, indent=2)

        self.notify(f"Exported to {filepath}", severity="information", timeout=5)
