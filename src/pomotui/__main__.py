"""Entry point for running pomotui as a module."""

from pomotui.app import PomodoroApp


def main() -> None:
    """Main entry point for the application."""
    app = PomodoroApp()
    app.run()


if __name__ == "__main__":
    main()
