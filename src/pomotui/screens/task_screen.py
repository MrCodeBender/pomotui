"""Task management screen."""

from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.screen import Screen
from textual.widgets import Button, Input, Label, Static

from pomotui.models import Task


class TaskScreen(Screen):
    """Screen for creating a new task."""

    BINDINGS = [
        ("escape", "cancel", "Cancel"),
    ]

    CSS = """
    TaskScreen {
        align: center middle;
    }

    TaskScreen > Container {
        width: 60;
        height: auto;
        border: solid $primary;
        padding: 2;
    }

    TaskScreen Label {
        margin-bottom: 1;
        text-style: bold;
    }

    TaskScreen Input {
        margin-bottom: 1;
    }

    TaskScreen Button {
        width: 100%;
        margin-top: 1;
    }
    """

    def __init__(self, *args, **kwargs) -> None:
        """Initialize task screen."""
        super().__init__(*args, **kwargs)
        self.task_name = ""
        self.task_description = ""

    def action_cancel(self) -> None:
        """Cancel and dismiss the screen."""
        self.dismiss(False)

    def compose(self) -> ComposeResult:
        """Compose the task screen."""
        with Container():
            yield Static("Create New Task", classes="title")
            yield Label("Task Name:")
            yield Input(placeholder="Enter task name...", id="task-name")
            yield Label("Description (optional):")
            yield Input(placeholder="Enter description...", id="task-description")
            with Vertical():
                yield Button("Create Task", variant="primary", id="create-btn")
                yield Button("Cancel (ESC)", variant="default", id="cancel-btn")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        if event.button.id == "create-btn":
            name_input = self.query_one("#task-name", Input)
            desc_input = self.query_one("#task-description", Input)

            if not name_input.value.strip():
                self.notify("Task name is required", severity="error")
                return

            self.task_name = name_input.value.strip()
            self.task_description = desc_input.value.strip()
            self.dismiss(True)
        elif event.button.id == "cancel-btn":
            self.dismiss(False)
