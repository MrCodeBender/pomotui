"""Tests for sound notifications."""

from unittest.mock import Mock

from pomotui.notifications import SoundNotificationManager


def test_sound_manager_initialization() -> None:
    """Test sound manager initialization."""
    app_mock = Mock()
    manager = SoundNotificationManager(app_mock)

    assert manager.is_enabled() is True
    assert manager.app is app_mock


def test_enable_disable_sound() -> None:
    """Test enabling and disabling sound."""
    app_mock = Mock()
    manager = SoundNotificationManager(app_mock)

    # Initially enabled
    assert manager.is_enabled() is True

    # Disable
    manager.disable()
    assert manager.is_enabled() is False

    # Enable
    manager.enable()
    assert manager.is_enabled() is True


def test_play_work_complete_when_enabled() -> None:
    """Test playing work complete sound when enabled."""
    app_mock = Mock()
    manager = SoundNotificationManager(app_mock)

    manager.play_work_complete()

    # Should call bell 3 times for work complete
    assert app_mock.bell.call_count == 3


def test_play_break_complete_when_enabled() -> None:
    """Test playing break complete sound when enabled."""
    app_mock = Mock()
    manager = SoundNotificationManager(app_mock)

    manager.play_break_complete()

    # Should call bell 1 time for break complete
    assert app_mock.bell.call_count == 1


def test_play_session_start_when_enabled() -> None:
    """Test playing session start sound when enabled."""
    app_mock = Mock()
    manager = SoundNotificationManager(app_mock)

    manager.play_session_start()

    # Should call bell 2 times for session start
    assert app_mock.bell.call_count == 2


def test_no_sound_when_disabled() -> None:
    """Test that no sound plays when disabled."""
    app_mock = Mock()
    manager = SoundNotificationManager(app_mock)

    # Disable sound
    manager.disable()

    # Try to play sounds
    manager.play_work_complete()
    manager.play_break_complete()
    manager.play_session_start()

    # Bell should not be called
    app_mock.bell.assert_not_called()


def test_enable_after_playing_disabled() -> None:
    """Test enabling sound after playing while disabled."""
    app_mock = Mock()
    manager = SoundNotificationManager(app_mock)

    # Disable and try to play
    manager.disable()
    manager.play_work_complete()
    assert app_mock.bell.call_count == 0

    # Enable and play
    manager.enable()
    manager.play_work_complete()
    assert app_mock.bell.call_count == 3
