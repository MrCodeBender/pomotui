"""Timer display widget."""

from textual.app import ComposeResult
from textual.containers import Container
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Label, ProgressBar, Static

from pomotui.timer import TimerState


class TimerDisplay(Widget):
    """Widget to display the Pomodoro timer."""

    time_text = reactive("25:00")
    session_text = reactive("Ready to focus")
    task_text = reactive("")
    progress_value = reactive(0.0)
    pomodoros_completed = reactive(0)

    DEFAULT_CSS = """
    TimerDisplay {
        height: auto;
        width: 100%;
        align: center middle;
    }

    TimerDisplay > Container {
        height: auto;
        width: 60;
        border: solid $primary;
        padding: 2;
    }

    TimerDisplay .session-type {
        text-align: center;
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
    }

    TimerDisplay .task-name {
        text-align: center;
        color: $text;
        margin-bottom: 1;
    }

    TimerDisplay .timer-text {
        text-align: center;
        text-style: bold;
        content-align: center middle;
        color: $text;
        height: 5;
    }

    TimerDisplay .timer-digits {
        text-style: bold;
        color: $success;
    }

    TimerDisplay .pomodoros-count {
        text-align: center;
        margin-top: 1;
        color: $text-muted;
    }

    TimerDisplay .controls-hint {
        text-align: center;
        margin-top: 1;
        color: $text-muted;
        text-style: italic;
    }
    """

    def compose(self) -> ComposeResult:
        """Compose the timer display."""
        with Container():
            yield Static(self.session_text, classes="session-type")
            yield Static(self.task_text, classes="task-name", id="task-name-display")
            yield Label(self.time_text, classes="timer-text timer-digits")
            yield ProgressBar(total=100, show_eta=False)
            yield Static(
                f"🍅 Completed: {self.pomodoros_completed}", classes="pomodoros-count"
            )
            yield Static(
                "[Space] Start/Pause  [R] Reset  [N] Next  [T] Task  [S] Stats  [M] Sound  [Q] Quit",
                classes="controls-hint"
            )

    def watch_time_text(self, new_time: str) -> None:
        """Update timer text when it changes."""
        try:
            label = self.query_one(".timer-digits", Label)
            label.update(new_time)
        except Exception:
            # Widget not yet composed
            pass

    def watch_session_text(self, new_text: str) -> None:
        """Update session text when it changes."""
        try:
            static = self.query_one(".session-type", Static)
            static.update(new_text)
        except Exception:
            # Widget not yet composed
            pass

    def watch_progress_value(self, new_value: float) -> None:
        """Update progress bar when value changes."""
        try:
            progress_bar = self.query_one(ProgressBar)
            progress_bar.update(progress=new_value)
        except Exception:
            # Widget not yet composed
            pass

    def watch_pomodoros_completed(self, count: int) -> None:
        """Update pomodoros count when it changes."""
        try:
            static = self.query_one(".pomodoros-count", Static)
            static.update(f"🍅 Completed: {count}")
        except Exception:
            # Widget not yet composed
            pass

    def watch_task_text(self, new_text: str) -> None:
        """Update task name when it changes."""
        try:
            static = self.query_one("#task-name-display", Static)
            static.update(new_text)
        except Exception:
            # Widget not yet composed
            pass

    def update_timer(
        self,
        time_str: str,
        state: TimerState,
        progress: float,
        pomodoros: int,
        task_name: str = "",
    ) -> None:
        """Update all timer display values.

        Args:
            time_str: Formatted time string (MM:SS)
            state: Current timer state
            progress: Progress percentage (0-100)
            pomodoros: Number of completed pomodoros
            task_name: Name of the current task (optional)
        """
        self.time_text = time_str
        self.progress_value = progress
        self.pomodoros_completed = pomodoros

        # Update task display
        if task_name:
            self.task_text = f"📋 {task_name}"
        else:
            self.task_text = ""

        # Update session text based on state
        if state == TimerState.IDLE:
            self.session_text = "Ready to focus"
        elif state == TimerState.WORKING:
            self.session_text = "🎯 Focus Time"
        elif state == TimerState.SHORT_BREAK:
            self.session_text = "☕ Short Break"
        elif state == TimerState.LONG_BREAK:
            self.session_text = "🌴 Long Break"
        elif state == TimerState.PAUSED:
            self.session_text = "⏸️  Paused"
