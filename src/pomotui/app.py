"""Main Textual application for pomotui."""

from typing import Optional

from textual import work
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Container
from textual.widgets import Header, Footer

from pomotui.database import DatabaseManager
from pomotui.models import TimerConfig, Task
from pomotui.screens import TaskScreen, StatsScreen
from pomotui.timer import PomodoroTimer, TimerState, SessionType
from pomotui.widgets import TimerDisplay, TaskList


class PomodoroApp(App):
    """A Textual app for Pomodoro time management."""

    CSS = """
    Screen {
        align: center middle;
    }

    Horizontal {
        width: 100%;
        height: auto;
        align: center middle;
    }

    #timer-container {
        width: 60%;
    }

    #task-container {
        width: 40%;
    }
    """

    BINDINGS = [
        ("space", "toggle_timer", "Start/Pause"),
        ("r", "reset_timer", "Reset"),
        ("n", "next_session", "Next Session"),
        ("t", "new_task", "New Task"),
        ("s", "show_stats", "Statistics"),
        ("q", "quit", "Quit"),
    ]

    def __init__(self) -> None:
        """Initialize the Pomodoro app."""
        super().__init__()
        config = TimerConfig.default()
        self.timer = PomodoroTimer(
            work_duration=config.work_duration,
            short_break_duration=config.short_break_duration,
            long_break_duration=config.long_break_duration,
            pomodoros_until_long_break=config.pomodoros_until_long_break,
        )
        self.timer.set_on_state_change(self._on_state_change)
        self.timer.set_on_tick(self._on_tick)
        self.timer.set_on_session_complete(self._on_session_complete)

        # Database
        self.db = DatabaseManager()
        self.current_task: Optional[Task] = None

        # Load theme preference
        self._load_theme_preference()

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        with Horizontal():
            with Container(id="timer-container"):
                yield TimerDisplay()
            with Container(id="task-container"):
                yield TaskList()
        yield Footer()

    def on_mount(self) -> None:
        """Set up the app when mounted."""
        # Set up periodic timer tick
        self.set_interval(1.0, self._tick_callback)
        # Update display with initial state
        self._update_display()
        # Load tasks
        self._load_tasks()

    def action_toggle_timer(self) -> None:
        """Toggle timer between running and paused."""
        if self.timer.state == TimerState.IDLE:
            self.timer.start_work_session()
        else:
            self.timer.toggle_pause()

    def action_reset_timer(self) -> None:
        """Reset the timer."""
        self.timer.reset()
        self._update_display()

    def action_next_session(self) -> None:
        """Start the next session."""
        self.timer.start_next_session()

    @work
    async def action_new_task(self) -> None:
        """Create a new task."""
        screen = TaskScreen()
        result = await self.push_screen(screen, wait_for_dismiss=True)

        if result:
            task = self.db.create_task(
                name=screen.task_name, description=screen.task_description
            )
            self.notify(f"Task '{task.name}' created!", severity="information")
            self._load_tasks()
            # Automatically select the new task
            self.current_task = task
            self.timer.set_current_task(task.id)

    def action_show_stats(self) -> None:
        """Show statistics screen."""
        self.push_screen(StatsScreen(self.db))

    def watch_theme(self, theme: str) -> None:
        """Watch for theme changes and save preference.

        This is called automatically when the theme changes
        (e.g., from the command palette).
        """
        self._save_theme_preference()

    def _tick_callback(self) -> None:
        """Called every second to update the timer."""
        if self.timer.state.is_active():
            self.timer.tick()
            self._update_display()

    def _on_state_change(self, state: TimerState) -> None:
        """Handle timer state changes."""
        self._update_display()

    def _on_tick(self, time_remaining: int) -> None:
        """Handle timer tick."""
        # Display is updated in _tick_callback
        pass

    def _on_session_complete(
        self, session_type: SessionType, duration: int, task_id: Optional[int]
    ) -> None:
        """Handle session completion."""
        # Save session to database
        self.db.create_session(
            task_id=task_id,
            duration=duration,
            session_type=session_type.value,
            completed=True,
        )

        # Increment task pomodoro count if this was a work session
        if session_type == SessionType.WORK and task_id:
            self.db.increment_task_pomodoros(task_id)
            if self.current_task and self.current_task.id == task_id:
                self.current_task.increment_pomodoros()

        self.notify(
            f"Session complete! Good job! 🎉",
            title=f"{session_type.value.replace('_', ' ').title()} Finished",
            severity="information",
            timeout=5,
        )
        self._update_display()

    def _update_display(self) -> None:
        """Update the timer display."""
        timer_display = self.query_one(TimerDisplay)

        # Calculate progress percentage
        total = self.timer.total_duration
        remaining = self.timer.time_remaining
        progress = 0.0 if total == 0 else ((total - remaining) / total) * 100

        timer_display.update_timer(
            time_str=self.timer.format_time(),
            state=self.timer.state,
            progress=progress,
            pomodoros=self.timer.completed_pomodoros,
        )

    def _load_tasks(self) -> None:
        """Load tasks from database."""
        tasks = self.db.get_all_tasks(include_completed=False)
        task_list = self.query_one(TaskList)
        task_list.tasks = tasks
        if self.current_task:
            task_list.selected_task_id = self.current_task.id

    def _load_theme_preference(self) -> None:
        """Load theme preference from database."""
        saved_theme = self.db.get_setting("theme")
        if saved_theme is not None and saved_theme in self.available_themes:
            self.theme = saved_theme

    def _save_theme_preference(self) -> None:
        """Save current theme to database."""
        self.db.set_setting("theme", self.theme)


if __name__ == "__main__":
    app = PomodoroApp()
    app.run()
