# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**pomotui** is a Pomodoro TUI (Terminal User Interface) application built with Textual, featuring:
- ✅ Full Pomodoro timer with work/break cycles
- ✅ Task tracking and management
- ✅ Statistics and reports (daily/weekly/monthly)
- ✅ Data export (CSV/JSON)
- ✅ Theme persistence (Textual themes)
- ✅ Intuitive navigation with ESC key support
- 🔲 Sound notifications (planned)

## Technology Stack

- **TUI Framework**: Textual 0.47.0+ (modern reactive framework with CSS-like styling)
- **Package Manager**: uv (fast, modern Python package manager)
- **Database**: SQLite with standard library (sqlite3)
- **Storage Location**: `~/.config/pomotui/pomotui.db`
- **Testing**: pytest with 60 tests passing
- **Code Quality**: mypy, ruff for linting and formatting

## Development Commands

### Environment Setup
```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install project dependencies
uv pip install -e ".[dev]"
```

### Running the Application
```bash
# Run the TUI application
uv run pomotui

# Or after activating venv
python -m pomotui
```

### Development Tasks
```bash
# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=pomotui --cov-report=html

# Run a single test file
uv run pytest tests/test_timer.py

# Run a specific test
uv run pytest tests/test_timer.py::test_pomodoro_duration

# Type checking
uv run mypy pomotui

# Linting and formatting
uv run ruff check .
uv run ruff format .

# Run the app in development mode (with auto-reload if implemented)
uv run textual run --dev pomotui.app:app
```

## Project Architecture

### Actual Directory Structure
```
pomotui/
├── src/pomotui/
│   ├── __init__.py
│   ├── __main__.py          # Entry point for `python -m pomotui`
│   ├── app.py               # Main Textual App class (PomodoroApp)
│   ├── screens/
│   │   ├── __init__.py
│   │   ├── task_screen.py   # Task creation/editing screen
│   │   └── stats_screen.py  # Statistics and reports screen
│   ├── widgets/
│   │   ├── __init__.py
│   │   ├── timer_display.py # Timer display with progress bar
│   │   └── task_list.py     # Task list widget
│   ├── models/
│   │   ├── __init__.py
│   │   ├── config.py        # TimerConfig dataclass
│   │   ├── task.py          # Task and Session dataclasses
│   │   └── statistics.py    # Statistics calculation logic
│   ├── database/
│   │   ├── __init__.py
│   │   ├── schema.py        # Database schema and initialization
│   │   └── manager.py       # DatabaseManager class (CRUD operations)
│   └── timer/
│       ├── __init__.py
│       ├── state.py         # TimerState and SessionType enums
│       └── pomodoro.py      # PomodoroTimer class (state machine)
├── tests/
│   ├── test_app.py          # App integration tests
│   ├── test_database.py     # Database CRUD tests
│   ├── test_models.py       # Model tests (TimerConfig)
│   ├── test_statistics.py   # Statistics calculation tests
│   ├── test_task.py         # Task/Session model tests
│   ├── test_theme_persistence.py  # Theme persistence tests
│   └── test_timer.py        # Timer state machine tests
├── pyproject.toml           # Project configuration
├── README.md
├── CLAUDE.md
└── LICENSE
```

### Key Architectural Patterns

#### 1. Textual App Structure
- **PomodoroApp** (app.py): Main app inheriting from `textual.app.App`
- **Reactive system**: Uses `reactive()` for state management (time_text, session_text, progress_value)
- **Screens**: TaskScreen (modal), StatsScreen (modal with tabs)
- **Widgets**: TimerDisplay, TaskList (reusable components)
- **Navigation**: ESC key returns to main screen from all modal screens

#### 2. Timer State Machine (timer/pomodoro.py)
- **States** (TimerState enum): IDLE, WORKING, SHORT_BREAK, LONG_BREAK, PAUSED
- **Default timings**: 25min work, 5min short break, 15min long break
- **Cycle**: Long break after 4 completed pomodoros
- **Callbacks**: on_state_change, on_tick, on_session_complete
- **Features**: pause/resume, reset, next session, task tracking

#### 3. Database Schema (database/schema.py)
**Tasks table**:
```sql
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT DEFAULT '',
    created_at TEXT NOT NULL,
    completed_at TEXT,
    color TEXT DEFAULT 'blue',
    pomodoro_count INTEGER DEFAULT 0
)
```

**Sessions table**:
```sql
CREATE TABLE sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER,
    start_time TEXT NOT NULL,
    end_time TEXT,
    duration INTEGER NOT NULL,
    completed BOOLEAN DEFAULT 0,
    session_type TEXT NOT NULL,
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE SET NULL
)
```

**Settings table**:
```sql
CREATE TABLE settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
)
```

#### 4. Theme Persistence
- **watch_theme()**: Automatically saves theme when changed via command palette (Ctrl+\)
- **Storage**: Theme name stored in settings table
- **Loading**: Theme preference loaded on app initialization
- **Validation**: Checks theme exists in `self.available_themes` before applying

### Textual-Specific Patterns Used

- **Reactive properties**: `reactive()` with `watch_*` methods for automatic UI updates
- **CSS styling**: Inline CSS in DEFAULT_CSS class attributes
- **@work decorator**: Used for async operations (e.g., `action_new_task`)
- **Keyboard bindings**: Space (toggle), R (reset), N (next), T (task), S (stats), Q (quit)
- **Built-in widgets**: DataTable (stats), ProgressBar (timer), Sparkline (charts), TabbedContent (stats tabs)
- **ComposeResult**: Using `yield from` pattern for widget composition

### Implemented Features

#### ✅ Pomodoro Timer
- **Location**: `timer/pomodoro.py`
- Full state machine with IDLE, WORKING, SHORT_BREAK, LONG_BREAK, PAUSED states
- Configurable durations (default: 25/5/15 minutes)
- Pause/resume, reset, and next session controls
- Progress bar visualization
- Completed pomodoros counter

#### ✅ Task Tracking
- **Location**: `screens/task_screen.py`, `widgets/task_list.py`, `models/task.py`
- Create tasks with name and description
- Associate pomodoros with tasks
- Track pomodoro count per task
- Task completion tracking
- Task database persistence

#### ✅ Statistics & Reports
- **Location**: `screens/stats_screen.py`, `models/statistics.py`
- Daily/weekly/monthly statistics (DailyStats, PeriodStats models)
- Tabbed interface (Today, This Week, This Month, All Tasks)
- Sparkline charts for daily trends
- Most productive day tracking
- Top tasks by pomodoro count
- CSV export (to ~/Documents)
- JSON export with full data

#### ✅ Theme Persistence
- **Location**: `app.py` (`watch_theme`, `_load_theme_preference`, `_save_theme_preference`)
- Automatically saves theme changes from command palette (Ctrl+\)
- Persists theme to database settings table
- Loads saved theme on application startup
- Validates theme against available Textual themes

#### ✅ Navigation
- **Pattern**: Tree structure with ESC key navigation
- ESC key returns to main screen from all modal screens
- Consistent back button in all screens
- Command palette (Ctrl+\) for theme selection

#### 🔲 Sound Notifications (Planned)
- Play notification sounds on session completion
- Configurable sound preferences
- Non-blocking audio playback

## Testing Strategy

**Current Status**: 60 tests passing ✅

### Test Coverage
- **Timer tests** (test_timer.py): 18 tests for state machine, transitions, callbacks
- **Database tests** (test_database.py): 16 tests for CRUD operations, settings
- **Statistics tests** (test_statistics.py): 12 tests for daily/weekly/monthly calculations
- **Task model tests** (test_task.py): 10 tests for Task/Session models
- **App tests** (test_app.py): 2 integration tests
- **Theme tests** (test_theme_persistence.py): 2 tests for theme persistence

### Testing Patterns
- **Database**: Using temporary database files with fixtures
- **Timer**: Testing state transitions and callback execution
- **Statistics**: Testing aggregation logic with mock data
- **Models**: Testing dataclass methods and serialization

### Running Tests
```bash
# All tests
uv run pytest

# With coverage
uv run pytest --cov=pomotui --cov-report=html

# Specific test file
uv run pytest tests/test_timer.py

# Verbose output
uv run pytest -v
```

## Key Bindings

| Key | Action | Description |
|-----|--------|-------------|
| Space | Toggle Timer | Start/pause the current timer |
| R | Reset | Reset timer to initial state |
| N | Next Session | Skip to next session (break/work) |
| T | New Task | Open task creation screen |
| S | Statistics | Open statistics screen |
| Ctrl+\ | Command Palette | Open Textual command palette (theme selection) |
| ESC | Back | Return to main screen (from modals) |
| Q | Quit | Exit application |

## Database Access

**Location**: `~/.config/pomotui/pomotui.db`

Access using any SQLite browser/manager:
```bash
# CLI
sqlite3 ~/.config/pomotui/pomotui.db

# Or use GUI tools like:
# - DB Browser for SQLite
# - DBeaver
# - DataGrip
```

## Common Development Patterns

### Adding a New Screen
1. Create screen class in `src/pomotui/screens/`
2. Inherit from `textual.screen.Screen`
3. Add BINDINGS with ESC for navigation
4. Implement `compose()` method
5. Add action method to main app

### Adding Reactive State
1. Define reactive property: `my_state = reactive(default_value)`
2. Create watcher: `def watch_my_state(self, new_value): ...`
3. Update in methods: `self.my_state = new_value`

### Database Operations
1. Use `DatabaseManager` instance (self.db in app)
2. All operations return proper types (Task, Session objects)
3. Foreign keys handle task deletion gracefully (SET NULL)

### Async Operations
Use `@work` decorator for operations that might block:
```python
from textual import work

@work
async def action_my_action(self) -> None:
    result = await self.push_screen(MyScreen(), wait_for_dismiss=True)
    # Handle result
```

## License

MIT License - See LICENSE file for details.
