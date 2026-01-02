"""Task list widget."""

from typing import List

from textual import events
from textual.app import ComposeResult
from textual.containers import Container, VerticalScroll
from textual.message import Message
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Button, Label, Static

from pomotui.models import Task


class TaskItem(Static):
    """Widget representing a single task."""

    DEFAULT_CSS = """
    TaskItem {
        height: auto;
        border: solid $panel;
        padding: 1;
        margin-bottom: 1;
    }

    TaskItem:hover {
        border: solid $accent;
        background: $panel-lighten-1;
        cursor: pointer;
    }

    TaskItem.selected {
        border: solid $success;
        background: $success-darken-2;
    }

    TaskItem .task-name {
        text-style: bold;
    }

    TaskItem .task-info {
        color: $text-muted;
        text-style: italic;
    }
    """

    class Selected(Message):
        """Message sent when a task item is selected."""

        def __init__(self, task: Task) -> None:
            """Initialize the message.

            Args:
                task: The selected task
            """
            super().__init__()
            self.task = task

    def __init__(self, task: Task, is_selected: bool = False) -> None:
        """Initialize task item.

        Args:
            task: Task to display
            is_selected: Whether this task is currently selected
        """
        super().__init__()
        self._task_data = task
        self.is_selected = is_selected
        if is_selected:
            self.add_class("selected")

    def compose(self) -> ComposeResult:
        """Compose the task item."""
        status = "✓" if self._task_data.is_completed else "○"
        yield Label(f"{status} {self._task_data.name}", classes="task-name")
        if self._task_data.description:
            yield Static(self._task_data.description)
        yield Static(
            f"🍅 {self._task_data.pomodoro_count} pomodoros", classes="task-info"
        )

    def on_click(self, event: events.Click) -> None:
        """Handle click event."""
        event.stop()
        self.post_message(self.Selected(self._task_data))


class TaskList(Widget):
    """Widget to display and manage tasks."""

    tasks = reactive(list)
    selected_task_id = reactive(None)

    DEFAULT_CSS = """
    TaskList {
        height: auto;
        width: 100%;
    }

    TaskList > Container {
        height: auto;
        width: 100%;
        border: solid $primary;
        padding: 1;
    }

    TaskList .header {
        text-align: center;
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
    }

    TaskList .no-tasks {
        text-align: center;
        color: $text-muted;
        text-style: italic;
        padding: 2;
    }

    TaskList VerticalScroll {
        height: auto;
        max-height: 20;
    }

    TaskList Button {
        width: 100%;
        margin-top: 1;
    }
    """

    def __init__(self, tasks: List[Task] = None) -> None:
        """Initialize task list.

        Args:
            tasks: List of tasks to display
        """
        super().__init__()
        self.tasks = tasks or []

    def compose(self) -> ComposeResult:
        """Compose the task list."""
        with Container():
            yield Static("Tasks", classes="header")
            with VerticalScroll(id="task-scroll"):
                if not self.tasks:
                    yield Static(
                        "No tasks yet. Press 'T' to create one!", classes="no-tasks"
                    )
                else:
                    for task in self.tasks:
                        yield TaskItem(
                            task, is_selected=(task.id == self.selected_task_id)
                        )
            yield Button("New Task (T)", variant="primary", id="new-task-btn")

    def watch_tasks(self, tasks: List[Task]) -> None:
        """Update display when tasks change."""
        # Only update if widget is mounted
        try:
            scroll = self.query_one("#task-scroll", VerticalScroll)
            scroll.remove_children()

            if not tasks:
                scroll.mount(
                    Static("No tasks yet. Press 'T' to create one!", classes="no-tasks")
                )
            else:
                for task in tasks:
                    scroll.mount(TaskItem(task, is_selected=(task.id == self.selected_task_id)))
        except Exception:
            # Widget not yet composed, skip update
            pass

    def on_task_item_selected(self, message: TaskItem.Selected) -> None:
        """Handle task item selection."""
        # Update selected task ID
        self.selected_task_id = message.task.id
