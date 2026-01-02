"""Tests for the main application."""

import pytest
from textual.pilot import Pilot

from pomotui.app import PomodoroApp


@pytest.mark.asyncio
async def test_app_starts() -> None:
    """Test that the app starts successfully."""
    app = PomodoroApp()
    async with app.run_test() as pilot:
        assert app.is_running
        assert pilot.app is app


@pytest.mark.asyncio
async def test_quit_binding() -> None:
    """Test that the quit binding works."""
    app = PomodoroApp()
    async with app.run_test() as pilot:
        await pilot.press("q")
        await pilot.pause()
        assert not app.is_running
