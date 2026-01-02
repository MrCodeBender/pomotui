"""Database manager for tasks and sessions."""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from pomotui.database.schema import get_connection
from pomotui.models import Task, Session


class DatabaseManager:
    """Manages database operations for tasks and sessions."""

    def __init__(self, db_path: Optional[Path] = None) -> None:
        """Initialize the database manager.

        Args:
            db_path: Path to database file. If None, uses default path.
        """
        self.db_path = db_path
        self._conn: Optional[sqlite3.Connection] = None

    @property
    def conn(self) -> sqlite3.Connection:
        """Get database connection, creating it if necessary."""
        if self._conn is None:
            self._conn = get_connection(self.db_path)
        return self._conn

    def close(self) -> None:
        """Close database connection."""
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    # Task operations

    def create_task(self, name: str, description: str = "", color: str = "blue") -> Task:
        """Create a new task.

        Args:
            name: Task name
            description: Task description
            color: Task color

        Returns:
            Created task with ID
        """
        created_at = datetime.now()
        cursor = self.conn.execute(
            """
            INSERT INTO tasks (name, description, created_at, color)
            VALUES (?, ?, ?, ?);
            """,
            (name, description, created_at.isoformat(), color),
        )
        self.conn.commit()

        task = Task(
            id=cursor.lastrowid,
            name=name,
            description=description,
            created_at=created_at,
            color=color,
        )
        return task

    def get_task(self, task_id: int) -> Optional[Task]:
        """Get a task by ID.

        Args:
            task_id: Task ID

        Returns:
            Task if found, None otherwise
        """
        cursor = self.conn.execute(
            "SELECT * FROM tasks WHERE id = ?;",
            (task_id,),
        )
        row = cursor.fetchone()
        if row is None:
            return None

        return Task.from_dict(dict(row))

    def get_all_tasks(self, include_completed: bool = True) -> List[Task]:
        """Get all tasks.

        Args:
            include_completed: Whether to include completed tasks

        Returns:
            List of tasks
        """
        query = "SELECT * FROM tasks"
        if not include_completed:
            query += " WHERE completed_at IS NULL"
        query += " ORDER BY created_at DESC;"

        cursor = self.conn.execute(query)
        tasks = [Task.from_dict(dict(row)) for row in cursor.fetchall()]
        return tasks

    def update_task(self, task: Task) -> None:
        """Update a task.

        Args:
            task: Task to update
        """
        if task.id is None:
            raise ValueError("Cannot update task without ID")

        self.conn.execute(
            """
            UPDATE tasks
            SET name = ?, description = ?, completed_at = ?, color = ?, pomodoro_count = ?
            WHERE id = ?;
            """,
            (
                task.name,
                task.description,
                task.completed_at.isoformat() if task.completed_at else None,
                task.color,
                task.pomodoro_count,
                task.id,
            ),
        )
        self.conn.commit()

    def delete_task(self, task_id: int) -> None:
        """Delete a task.

        Args:
            task_id: Task ID
        """
        self.conn.execute("DELETE FROM tasks WHERE id = ?;", (task_id,))
        self.conn.commit()

    def increment_task_pomodoros(self, task_id: int) -> None:
        """Increment pomodoro count for a task.

        Args:
            task_id: Task ID
        """
        self.conn.execute(
            "UPDATE tasks SET pomodoro_count = pomodoro_count + 1 WHERE id = ?;",
            (task_id,),
        )
        self.conn.commit()

    # Session operations

    def create_session(
        self,
        task_id: Optional[int],
        duration: int,
        session_type: str,
        completed: bool = True,
    ) -> Session:
        """Create a new session.

        Args:
            task_id: Associated task ID (can be None)
            duration: Session duration in seconds
            session_type: Type of session (work, short_break, long_break)
            completed: Whether session was completed

        Returns:
            Created session with ID
        """
        start_time = datetime.now()
        end_time = datetime.now() if completed else None

        cursor = self.conn.execute(
            """
            INSERT INTO sessions (task_id, start_time, end_time, duration, completed, session_type)
            VALUES (?, ?, ?, ?, ?, ?);
            """,
            (
                task_id,
                start_time.isoformat(),
                end_time.isoformat() if end_time else None,
                duration,
                completed,
                session_type,
            ),
        )
        self.conn.commit()

        session = Session(
            id=cursor.lastrowid,
            task_id=task_id,
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            completed=completed,
            session_type=session_type,
        )
        return session

    def get_session(self, session_id: int) -> Optional[Session]:
        """Get a session by ID.

        Args:
            session_id: Session ID

        Returns:
            Session if found, None otherwise
        """
        cursor = self.conn.execute(
            "SELECT * FROM sessions WHERE id = ?;",
            (session_id,),
        )
        row = cursor.fetchone()
        if row is None:
            return None

        return Session.from_dict(dict(row))

    def get_sessions_for_task(self, task_id: int) -> List[Session]:
        """Get all sessions for a task.

        Args:
            task_id: Task ID

        Returns:
            List of sessions
        """
        cursor = self.conn.execute(
            "SELECT * FROM sessions WHERE task_id = ? ORDER BY start_time DESC;",
            (task_id,),
        )
        sessions = [Session.from_dict(dict(row)) for row in cursor.fetchall()]
        return sessions

    def get_all_sessions(self, limit: Optional[int] = None) -> List[Session]:
        """Get all sessions.

        Args:
            limit: Maximum number of sessions to return

        Returns:
            List of sessions
        """
        query = "SELECT * FROM sessions ORDER BY start_time DESC"
        if limit:
            query += f" LIMIT {limit}"
        query += ";"

        cursor = self.conn.execute(query)
        sessions = [Session.from_dict(dict(row)) for row in cursor.fetchall()]
        return sessions

    def get_session_stats(self) -> dict:
        """Get session statistics.

        Returns:
            Dictionary with session statistics
        """
        cursor = self.conn.execute(
            """
            SELECT
                COUNT(*) as total_sessions,
                SUM(CASE WHEN session_type = 'work' THEN 1 ELSE 0 END) as work_sessions,
                SUM(CASE WHEN completed = 1 THEN 1 ELSE 0 END) as completed_sessions,
                SUM(duration) as total_duration
            FROM sessions;
            """
        )
        row = cursor.fetchone()
        return dict(row) if row else {}

    # Settings operations

    def get_setting(self, key: str) -> Optional[str]:
        """Get a setting value.

        Args:
            key: Setting key

        Returns:
            Setting value if found, None otherwise
        """
        cursor = self.conn.execute(
            "SELECT value FROM settings WHERE key = ?;",
            (key,),
        )
        row = cursor.fetchone()
        return row["value"] if row else None

    def set_setting(self, key: str, value: str) -> None:
        """Set a setting value.

        Args:
            key: Setting key
            value: Setting value
        """
        self.conn.execute(
            """
            INSERT INTO settings (key, value)
            VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET value = excluded.value;
            """,
            (key, value),
        )
        self.conn.commit()
