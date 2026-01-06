"""Confirmation dialog screen."""

from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.screen import Screen
from textual.widgets import Button, Static


class ConfirmDialog(Screen):
    """A confirmation dialog screen."""

    BINDINGS = [
        ("escape", "cancel", "Cancel"),
    ]

    CSS = """
    ConfirmDialog {
        align: center middle;
    }

    ConfirmDialog > Container {
        width: 50;
        height: auto;
        border: solid $warning;
        padding: 2;
        background: $panel;
    }

    ConfirmDialog Static {
        width: 100%;
        text-align: center;
        margin-bottom: 2;
    }

    ConfirmDialog .title {
        text-style: bold;
        color: $warning;
    }

    ConfirmDialog .message {
        color: $text;
    }

    ConfirmDialog Horizontal {
        width: 100%;
        height: auto;
        align: center middle;
    }

    ConfirmDialog Button {
        margin: 0 1;
    }
    """

    def __init__(self, title: str, message: str, *args, **kwargs) -> None:
        """Initialize confirmation dialog.

        Args:
            title: Dialog title
            message: Dialog message
        """
        super().__init__(*args, **kwargs)
        self.title_text = title
        self.message_text = message

    def action_cancel(self) -> None:
        """Cancel and dismiss the dialog."""
        self.dismiss(False)

    def compose(self) -> ComposeResult:
        """Compose the confirmation dialog."""
        with Container():
            yield Static(self.title_text, classes="title")
            yield Static(self.message_text, classes="message")
            with Horizontal():
                yield Button("Yes", variant="error", id="yes-btn")
                yield Button("No", variant="default", id="no-btn")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        if event.button.id == "yes-btn":
            self.dismiss(True)
        elif event.button.id == "no-btn":
            self.dismiss(False)
