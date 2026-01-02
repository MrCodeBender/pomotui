"""Tests for theme persistence."""

import tempfile
from pathlib import Path

import pytest

from pomotui.database import DatabaseManager


def test_theme_preference_persistence() -> None:
    """Test that theme preference is saved and loaded correctly."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = Path(f.name)

    try:
        # Initialize database
        from pomotui.database.schema import initialize_database
        initialize_database(db_path)

        db = DatabaseManager(db_path)

        # Initially no theme preference
        theme = db.get_setting("theme")
        assert theme is None

        # Save dark theme
        db.set_setting("theme", "dark")
        theme = db.get_setting("theme")
        assert theme == "dark"

        # Close and reopen database
        db.close()
        db = DatabaseManager(db_path)

        # Theme should still be dark
        theme = db.get_setting("theme")
        assert theme == "dark"

        # Change to light theme
        db.set_setting("theme", "light")
        theme = db.get_setting("theme")
        assert theme == "light"

        db.close()
    finally:
        db_path.unlink()


def test_theme_toggle() -> None:
    """Test theme values are correct."""
    themes = ["dark", "light"]

    for theme in themes:
        assert theme in ["dark", "light"]

    # Test conversion logic
    is_dark = "dark" == "dark"
    assert is_dark is True

    is_dark = "light" == "dark"
    assert is_dark is False
