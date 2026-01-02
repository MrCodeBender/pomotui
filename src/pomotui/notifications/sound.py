"""Sound notification manager."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from textual.app import App


class SoundNotificationManager:
    """Manages sound notifications for the Pomodoro app.

    Uses Textual's built-in bell() method for terminal bell sounds,
    which works across all platforms without external dependencies.
    """

    def __init__(self, app: "App[None]") -> None:
        """Initialize the sound notification manager.

        Args:
            app: The Textual app instance
        """
        self.app = app
        self._enabled = True

    def enable(self) -> None:
        """Enable sound notifications."""
        self._enabled = True

    def disable(self) -> None:
        """Disable sound notifications."""
        self._enabled = False

    def is_enabled(self) -> bool:
        """Check if sound notifications are enabled.

        Returns:
            True if enabled, False otherwise
        """
        return self._enabled

    def play_work_complete(self) -> None:
        """Play notification for completed work session."""
        if self._enabled:
            # Triple bell for work session complete
            self.app.bell()
            self.app.bell()
            self.app.bell()

    def play_break_complete(self) -> None:
        """Play notification for completed break session."""
        if self._enabled:
            # Single bell for break complete
            self.app.bell()

    def play_session_start(self) -> None:
        """Play notification when a new session starts."""
        if self._enabled:
            # Double bell for session start
            self.app.bell()
            self.app.bell()
