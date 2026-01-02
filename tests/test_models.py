"""Tests for data models."""

import pytest

from pomotui.models import TimerConfig


def test_timer_config_default() -> None:
    """Test default timer configuration."""
    config = TimerConfig.default()

    assert config.work_duration == 25
    assert config.short_break_duration == 5
    assert config.long_break_duration == 15
    assert config.pomodoros_until_long_break == 4


def test_timer_config_custom() -> None:
    """Test custom timer configuration."""
    config = TimerConfig(
        work_duration=30,
        short_break_duration=10,
        long_break_duration=20,
        pomodoros_until_long_break=3,
    )

    assert config.work_duration == 30
    assert config.short_break_duration == 10
    assert config.long_break_duration == 20
    assert config.pomodoros_until_long_break == 3


def test_timer_config_validation() -> None:
    """Test timer configuration validation."""
    # Valid configuration
    config = TimerConfig.default()
    config.validate()  # Should not raise

    # Invalid work duration
    config = TimerConfig(work_duration=0)
    with pytest.raises(ValueError, match="Work duration must be at least 1 minute"):
        config.validate()

    # Invalid short break
    config = TimerConfig(short_break_duration=0)
    with pytest.raises(
        ValueError, match="Short break duration must be at least 1 minute"
    ):
        config.validate()

    # Invalid long break
    config = TimerConfig(long_break_duration=0)
    with pytest.raises(
        ValueError, match="Long break duration must be at least 1 minute"
    ):
        config.validate()

    # Invalid pomodoros count
    config = TimerConfig(pomodoros_until_long_break=0)
    with pytest.raises(
        ValueError, match="Pomodoros until long break must be at least 1"
    ):
        config.validate()
