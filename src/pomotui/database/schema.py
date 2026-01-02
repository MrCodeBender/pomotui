"""Database schema definitions."""

import sqlite3
from pathlib import Path
from typing import Optional


SCHEMA_VERSION = 1


TASKS_TABLE = """
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT DEFAULT '',
    created_at TEXT NOT NULL,
    completed_at TEXT,
    color TEXT DEFAULT 'blue',
    pomodoro_count INTEGER DEFAULT 0
);
"""

SESSIONS_TABLE = """
CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER,
    start_time TEXT NOT NULL,
    end_time TEXT,
    duration INTEGER NOT NULL,
    completed BOOLEAN DEFAULT 0,
    session_type TEXT NOT NULL,
    FOREIGN KEY (task_id) REFERENCES tasks (id) ON DELETE SET NULL
);
"""

SETTINGS_TABLE = """
CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
"""

SCHEMA_VERSION_TABLE = """
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY
);
"""


def get_default_db_path() -> Path:
    """Get the default database path."""
    config_dir = Path.home() / ".config" / "pomotui"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / "pomotui.db"


def initialize_database(db_path: Optional[Path] = None) -> sqlite3.Connection:
    """Initialize the database with the schema.

    Args:
        db_path: Path to database file. If None, uses default path.

    Returns:
        Database connection
    """
    if db_path is None:
        db_path = get_default_db_path()

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row

    # Enable foreign keys
    conn.execute("PRAGMA foreign_keys = ON;")

    # Create tables
    conn.execute(TASKS_TABLE)
    conn.execute(SESSIONS_TABLE)
    conn.execute(SETTINGS_TABLE)
    conn.execute(SCHEMA_VERSION_TABLE)

    # Set schema version if not set
    cursor = conn.execute("SELECT version FROM schema_version LIMIT 1;")
    if cursor.fetchone() is None:
        conn.execute("INSERT INTO schema_version (version) VALUES (?);", (SCHEMA_VERSION,))

    conn.commit()
    return conn


def get_connection(db_path: Optional[Path] = None) -> sqlite3.Connection:
    """Get a database connection.

    Args:
        db_path: Path to database file. If None, uses default path.

    Returns:
        Database connection
    """
    if db_path is None:
        db_path = get_default_db_path()

    if not db_path.exists():
        return initialize_database(db_path)

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn
