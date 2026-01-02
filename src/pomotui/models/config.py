"""Configuration models."""

from dataclasses import dataclass


@dataclass
class TimerConfig:
    """Configuration for timer durations."""

    work_duration: int = 25  # minutes
    short_break_duration: int = 5  # minutes
    long_break_duration: int = 15  # minutes
    pomodoros_until_long_break: int = 4

    @classmethod
    def default(cls) -> "TimerConfig":
        """Create default configuration."""
        return cls()

    def validate(self) -> None:
        """Validate configuration values."""
        if self.work_duration < 1:
            raise ValueError("Work duration must be at least 1 minute")
        if self.short_break_duration < 1:
            raise ValueError("Short break duration must be at least 1 minute")
        if self.long_break_duration < 1:
            raise ValueError("Long break duration must be at least 1 minute")
        if self.pomodoros_until_long_break < 1:
            raise ValueError("Pomodoros until long break must be at least 1")
