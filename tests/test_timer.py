"""Tests for timer functionality."""

import time
from datetime import datetime, timedelta

import pytest

from pomotui.timer import PomodoroTimer, TimerState, SessionType


def test_timer_initialization() -> None:
    """Test timer initializes with correct default values."""
    timer = PomodoroTimer()
    assert timer.state == TimerState.IDLE
    assert timer.completed_pomodoros == 0
    assert timer.time_remaining == 0
    assert timer.work_duration == 25 * 60
    assert timer.short_break_duration == 5 * 60
    assert timer.long_break_duration == 15 * 60


def test_timer_custom_durations() -> None:
    """Test timer with custom durations."""
    timer = PomodoroTimer(
        work_duration=30,
        short_break_duration=10,
        long_break_duration=20,
        pomodoros_until_long_break=3,
    )
    assert timer.work_duration == 30 * 60
    assert timer.short_break_duration == 10 * 60
    assert timer.long_break_duration == 20 * 60
    assert timer.pomodoros_until_long_break == 3


def test_start_work_session() -> None:
    """Test starting a work session."""
    timer = PomodoroTimer()
    timer.start_work_session()

    assert timer.state == TimerState.WORKING
    assert timer.time_remaining > 0
    assert timer.total_duration == 25 * 60


def test_start_break_sessions() -> None:
    """Test starting break sessions."""
    timer = PomodoroTimer()

    timer.start_short_break()
    assert timer.state == TimerState.SHORT_BREAK
    assert timer.total_duration == 5 * 60

    timer.start_long_break()
    assert timer.state == TimerState.LONG_BREAK
    assert timer.total_duration == 15 * 60


def test_pause_and_resume() -> None:
    """Test pausing and resuming the timer."""
    timer = PomodoroTimer(work_duration=1)
    timer.start_work_session()

    time.sleep(0.1)
    initial_remaining = timer.time_remaining
    timer.pause()

    assert timer.state == TimerState.PAUSED
    paused_remaining = timer.time_remaining

    time.sleep(0.2)
    assert timer.time_remaining == paused_remaining  # Should not change while paused

    timer.resume()
    assert timer.state == TimerState.WORKING


def test_toggle_pause() -> None:
    """Test toggle pause functionality."""
    timer = PomodoroTimer()
    timer.start_work_session()

    assert timer.state == TimerState.WORKING
    timer.toggle_pause()
    assert timer.state == TimerState.PAUSED
    timer.toggle_pause()
    assert timer.state == TimerState.WORKING


def test_stop_timer() -> None:
    """Test stopping the timer."""
    timer = PomodoroTimer()
    timer.start_work_session()
    timer.stop()

    assert timer.state == TimerState.IDLE
    assert timer.time_remaining == 0


def test_reset_timer() -> None:
    """Test resetting the timer."""
    timer = PomodoroTimer()
    timer.start_work_session()

    # Simulate completing a session
    timer._completed_pomodoros = 3

    timer.reset()

    assert timer.state == TimerState.IDLE
    assert timer.completed_pomodoros == 0
    assert timer.time_remaining == 0


def test_session_completion() -> None:
    """Test session completion callback."""
    timer = PomodoroTimer(work_duration=0)  # 0 minutes for instant completion
    completed_sessions = []

    def on_complete(session_type: SessionType, duration: int, task_id: int | None) -> None:
        completed_sessions.append((session_type, duration, task_id))

    timer.set_on_session_complete(on_complete)
    timer.start_work_session()
    timer.tick()

    assert len(completed_sessions) == 1
    assert completed_sessions[0][0] == SessionType.WORK
    assert completed_sessions[0][2] is None  # No task ID
    assert timer.completed_pomodoros == 1


def test_start_next_session_cycle() -> None:
    """Test the automatic session cycling."""
    timer = PomodoroTimer(pomodoros_until_long_break=2)

    # Start from idle -> work
    timer.start_next_session()
    assert timer.state == TimerState.WORKING

    # Complete work -> short break (pomodoro 1)
    timer._completed_pomodoros = 0
    timer._state = TimerState.WORKING
    timer.start_next_session()
    assert timer.state == TimerState.SHORT_BREAK

    # Complete short break -> work
    timer._state = TimerState.SHORT_BREAK
    timer.start_next_session()
    assert timer.state == TimerState.WORKING

    # Complete work -> long break (pomodoro 2)
    timer._completed_pomodoros = 1
    timer._state = TimerState.WORKING
    timer.start_next_session()
    assert timer.state == TimerState.LONG_BREAK


def test_state_change_callback() -> None:
    """Test state change callback."""
    timer = PomodoroTimer()
    states = []

    def on_state_change(state: TimerState) -> None:
        states.append(state)

    timer.set_on_state_change(on_state_change)
    timer.start_work_session()
    timer.pause()
    timer.stop()

    assert states == [TimerState.WORKING, TimerState.PAUSED, TimerState.IDLE]


def test_tick_callback() -> None:
    """Test tick callback."""
    timer = PomodoroTimer()
    ticks = []

    def on_tick(time_remaining: int) -> None:
        ticks.append(time_remaining)

    timer.set_on_tick(on_tick)
    timer.start_work_session()
    timer.tick()

    assert len(ticks) == 1
    assert ticks[0] > 0


def test_format_time() -> None:
    """Test time formatting."""
    timer = PomodoroTimer()

    assert timer.format_time(0) == "00:00"
    assert timer.format_time(59) == "00:59"
    assert timer.format_time(60) == "01:00"
    assert timer.format_time(125) == "02:05"
    assert timer.format_time(3599) == "59:59"
    assert timer.format_time(3661) == "61:01"


def test_timer_state_methods() -> None:
    """Test TimerState helper methods."""
    assert TimerState.SHORT_BREAK.is_break()
    assert TimerState.LONG_BREAK.is_break()
    assert not TimerState.WORKING.is_break()
    assert not TimerState.IDLE.is_break()

    assert TimerState.WORKING.is_active()
    assert TimerState.SHORT_BREAK.is_active()
    assert TimerState.LONG_BREAK.is_active()
    assert not TimerState.IDLE.is_active()
    assert not TimerState.PAUSED.is_active()


def test_session_type_from_state() -> None:
    """Test converting TimerState to SessionType."""
    assert SessionType.from_state(TimerState.WORKING) == SessionType.WORK
    assert SessionType.from_state(TimerState.SHORT_BREAK) == SessionType.SHORT_BREAK
    assert SessionType.from_state(TimerState.LONG_BREAK) == SessionType.LONG_BREAK

    with pytest.raises(ValueError):
        SessionType.from_state(TimerState.IDLE)
