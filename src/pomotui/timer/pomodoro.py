"""Core Pomodoro timer implementation."""

from datetime import datetime, timedelta
from typing import Callable, Optional

from pomotui.timer.state import TimerState, SessionType


class PomodoroTimer:
    """Manages Pomodoro timer state and logic."""

    def __init__(
        self,
        work_duration: int = 25,
        short_break_duration: int = 5,
        long_break_duration: int = 15,
        pomodoros_until_long_break: int = 4,
    ) -> None:
        """Initialize the Pomodoro timer.

        Args:
            work_duration: Work session duration in minutes (default: 25)
            short_break_duration: Short break duration in minutes (default: 5)
            long_break_duration: Long break duration in minutes (default: 15)
            pomodoros_until_long_break: Number of pomodoros before long break (default: 4)
        """
        self.work_duration = work_duration * 60  # Convert to seconds
        self.short_break_duration = short_break_duration * 60
        self.long_break_duration = long_break_duration * 60
        self.pomodoros_until_long_break = pomodoros_until_long_break

        self._state = TimerState.IDLE
        self._completed_pomodoros = 0
        self._time_remaining = 0
        self._session_start_time: Optional[datetime] = None
        self._paused_time_remaining: Optional[int] = None
        self._current_task_id: Optional[int] = None

        # Callbacks
        self._on_state_change: Optional[Callable[[TimerState], None]] = None
        self._on_tick: Optional[Callable[[int], None]] = None
        self._on_session_complete: Optional[Callable[[SessionType, int, Optional[int]], None]] = None

    @property
    def state(self) -> TimerState:
        """Get current timer state."""
        return self._state

    @property
    def time_remaining(self) -> int:
        """Get time remaining in seconds."""
        if self._state == TimerState.PAUSED:
            return self._paused_time_remaining or 0
        elif self._state == TimerState.IDLE:
            return 0
        elif self._session_start_time is None:
            return 0

        elapsed = (datetime.now() - self._session_start_time).total_seconds()
        remaining = max(0, self._time_remaining - int(elapsed))
        return remaining

    @property
    def completed_pomodoros(self) -> int:
        """Get number of completed pomodoros."""
        return self._completed_pomodoros

    @property
    def current_task_id(self) -> Optional[int]:
        """Get current task ID."""
        return self._current_task_id

    def set_current_task(self, task_id: Optional[int]) -> None:
        """Set the current task for pomodoro sessions.

        Args:
            task_id: Task ID to associate with sessions, or None for no task
        """
        self._current_task_id = task_id

    @property
    def total_duration(self) -> int:
        """Get total duration of current session in seconds."""
        if self._state == TimerState.WORKING:
            return self.work_duration
        elif self._state == TimerState.SHORT_BREAK:
            return self.short_break_duration
        elif self._state == TimerState.LONG_BREAK:
            return self.long_break_duration
        return 0

    def set_on_state_change(self, callback: Callable[[TimerState], None]) -> None:
        """Set callback for state changes."""
        self._on_state_change = callback

    def set_on_tick(self, callback: Callable[[int], None]) -> None:
        """Set callback for timer ticks."""
        self._on_tick = callback

    def set_on_session_complete(
        self, callback: Callable[[SessionType, int, Optional[int]], None]
    ) -> None:
        """Set callback for session completion.

        Callback receives: (session_type, duration, task_id)
        """
        self._on_session_complete = callback

    def start_work_session(self) -> None:
        """Start a work session."""
        self._start_session(TimerState.WORKING, self.work_duration)

    def start_short_break(self) -> None:
        """Start a short break."""
        self._start_session(TimerState.SHORT_BREAK, self.short_break_duration)

    def start_long_break(self) -> None:
        """Start a long break."""
        self._start_session(TimerState.LONG_BREAK, self.long_break_duration)

    def start_next_session(self) -> None:
        """Start the next appropriate session based on current state."""
        if self._state == TimerState.IDLE:
            self.start_work_session()
        elif self._state == TimerState.WORKING:
            # Check if it's time for a long break
            if (self._completed_pomodoros + 1) % self.pomodoros_until_long_break == 0:
                self.start_long_break()
            else:
                self.start_short_break()
        elif self._state in (TimerState.SHORT_BREAK, TimerState.LONG_BREAK):
            self.start_work_session()

    def pause(self) -> None:
        """Pause the current timer."""
        if self._state.is_active():
            self._paused_time_remaining = self.time_remaining
            self._change_state(TimerState.PAUSED)

    def resume(self) -> None:
        """Resume from paused state."""
        if self._state == TimerState.PAUSED and self._paused_time_remaining is not None:
            # Determine which state to resume to
            if self._completed_pomodoros == 0 or self._time_remaining <= self.work_duration:
                resume_state = TimerState.WORKING
            elif self._paused_time_remaining <= self.short_break_duration:
                resume_state = TimerState.SHORT_BREAK
            else:
                resume_state = TimerState.LONG_BREAK

            self._start_session(resume_state, self._paused_time_remaining)
            self._paused_time_remaining = None

    def toggle_pause(self) -> None:
        """Toggle between paused and running states."""
        if self._state == TimerState.PAUSED:
            self.resume()
        elif self._state.is_active():
            self.pause()

    def stop(self) -> None:
        """Stop the timer and return to idle."""
        self._session_start_time = None
        self._time_remaining = 0
        self._paused_time_remaining = None
        self._change_state(TimerState.IDLE)

    def reset(self) -> None:
        """Reset the timer completely."""
        self.stop()
        self._completed_pomodoros = 0

    def tick(self) -> bool:
        """Update the timer. Should be called every second.

        Returns:
            True if session is complete, False otherwise
        """
        if not self._state.is_active():
            return False

        remaining = self.time_remaining

        if self._on_tick:
            self._on_tick(remaining)

        if remaining <= 0:
            self._complete_session()
            return True

        return False

    def _start_session(self, state: TimerState, duration: int) -> None:
        """Start a new session with the given state and duration."""
        self._state = state
        self._time_remaining = duration
        self._session_start_time = datetime.now()
        self._change_state(state)

    def _complete_session(self) -> None:
        """Handle session completion."""
        session_type = SessionType.from_state(self._state)
        duration = self.total_duration
        task_id = self._current_task_id if self._state == TimerState.WORKING else None

        if self._state == TimerState.WORKING:
            self._completed_pomodoros += 1

        if self._on_session_complete:
            self._on_session_complete(session_type, duration, task_id)

        self.stop()

    def _change_state(self, new_state: TimerState) -> None:
        """Change state and trigger callback."""
        self._state = new_state
        if self._on_state_change:
            self._on_state_change(new_state)

    def format_time(self, seconds: Optional[int] = None) -> str:
        """Format time in MM:SS format.

        Args:
            seconds: Time to format. If None, uses time_remaining.

        Returns:
            Formatted time string
        """
        if seconds is None:
            seconds = self.time_remaining

        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes:02d}:{secs:02d}"
