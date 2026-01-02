"""Timer state definitions and enums."""

from enum import Enum, auto


class TimerState(Enum):
    """States for the Pomodoro timer."""

    IDLE = auto()
    WORKING = auto()
    SHORT_BREAK = auto()
    LONG_BREAK = auto()
    PAUSED = auto()

    def is_break(self) -> bool:
        """Check if current state is a break."""
        return self in (TimerState.SHORT_BREAK, TimerState.LONG_BREAK)

    def is_active(self) -> bool:
        """Check if timer is actively running."""
        return self in (TimerState.WORKING, TimerState.SHORT_BREAK, TimerState.LONG_BREAK)


class SessionType(Enum):
    """Types of pomodoro sessions."""

    WORK = "work"
    SHORT_BREAK = "short_break"
    LONG_BREAK = "long_break"

    @classmethod
    def from_state(cls, state: TimerState) -> "SessionType":
        """Convert a TimerState to SessionType."""
        if state == TimerState.WORKING:
            return cls.WORK
        elif state == TimerState.SHORT_BREAK:
            return cls.SHORT_BREAK
        elif state == TimerState.LONG_BREAK:
            return cls.LONG_BREAK
        raise ValueError(f"Cannot convert state {state} to SessionType")
