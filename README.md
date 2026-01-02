# 🍅 pomotui

A modern, feature-rich Pomodoro timer for the terminal, built with [Textual](https://textual.textualize.io/).

## ✨ Features

- **⏱️ Full Pomodoro Timer**: Classic 25/5/15 minute work/break cycles with visual progress
- **📋 Task Management**: Create and track tasks, associate pomodoros with your work
- **📊 Statistics & Reports**: Detailed daily, weekly, and monthly productivity analytics
- **💾 Data Export**: Export your productivity data to CSV or JSON formats
- **🎨 Theme Persistence**: Customize your terminal theme and save your preference
- **⌨️ Keyboard-Driven**: Efficient keyboard shortcuts for all actions
- **🗂️ SQLite Storage**: Reliable local database for all your data
- **🧪 Well-Tested**: 60+ tests ensuring reliability

## 📸 Preview

```
┌─────────────────────────────────────────────────────────┐
│                    🎯 Focus Time                        │
│                                                         │
│                      25:00                              │
│  ████████████████████░░░░░░░░░░░░░░░  60%             │
│                                                         │
│              🍅 Completed: 3                            │
│                                                         │
│  [Space] Start/Pause  [R] Reset  [N] Next             │
│  [T] Task  [S] Stats  [Ctrl+\] Palette  [Q] Quit      │
└─────────────────────────────────────────────────────────┘
```

## 🚀 Installation

### Prerequisites
- Python 3.10 or higher
- [uv](https://github.com/astral-sh/uv) package manager (recommended)

### Install with uv (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/pomotui.git
cd pomotui

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .
```

### Install with pip

```bash
# Clone the repository
git clone https://github.com/yourusername/pomotui.git
cd pomotui

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install the package
pip install -e .
```

## 🎮 Usage

### Running the Application

```bash
# Using uv
uv run pomotui

# Or directly after installation
pomotui
```

### Keyboard Shortcuts

| Key | Action | Description |
|-----|--------|-------------|
| `Space` | Toggle Timer | Start or pause the current timer |
| `R` | Reset | Reset the timer to its initial state |
| `N` | Next Session | Skip to the next session (work → break → work) |
| `T` | New Task | Open the task creation dialog |
| `S` | Statistics | View your productivity statistics |
| `Ctrl+\` | Command Palette | Open Textual's command palette (theme selection, etc.) |
| `ESC` | Back | Return to the main screen from any modal |
| `Q` | Quit | Exit the application |

### Workflow

1. **Start a Pomodoro**: Press `Space` to start your first work session (25 minutes)
2. **Create Tasks** (optional): Press `T` to create a task and associate your work
3. **Take Breaks**: After 25 minutes, the app will notify you. Press `N` to start a break
4. **Track Progress**: Press `S` anytime to view your statistics and productivity trends
5. **Customize Theme**: Press `Ctrl+\` and select your preferred theme (persists across sessions)

## 📊 Statistics & Reports

pomotui provides comprehensive analytics:

- **Today's Stats**: Real-time view of your current day's productivity
- **Weekly Overview**: Last 7 days with daily sparkline charts
- **Monthly Trends**: 30-day view with most productive day tracking
- **Task Performance**: See which tasks consumed the most pomodoros
- **Export Options**: Save your data as CSV or JSON for external analysis

Export location: `~/Documents/pomotui_stats_YYYYMMDD_HHMMSS.{csv,json}`

## 🗄️ Database

All data is stored locally in an SQLite database:

**Location**: `~/.config/pomotui/pomotui.db`

You can access the database directly using:
- **CLI**: `sqlite3 ~/.config/pomotui/pomotui.db`
- **GUI Tools**: DB Browser for SQLite, DBeaver, DataGrip, etc.

### Database Schema

The database contains three main tables:
- `tasks`: Task definitions with pomodoro counts
- `sessions`: Individual work/break sessions
- `settings`: Application preferences (theme, etc.)

## 🛠️ Development

### Setup Development Environment

```bash
# Install with development dependencies
uv pip install -e ".[dev]"

# Or with pip
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage report
uv run pytest --cov=pomotui --cov-report=html

# Run specific test file
uv run pytest tests/test_timer.py

# Verbose output
uv run pytest -v
```

### Code Quality

```bash
# Type checking
uv run mypy src/pomotui

# Linting
uv run ruff check .

# Formatting
uv run ruff format .
```

### Development Mode

Run the app with Textual's development features:

```bash
uv run textual run --dev src/pomotui/app.py:PomodoroApp
```

## 🎨 Customization

### Timer Durations

Default durations are configured in `src/pomotui/models/config.py`:
- Work session: 25 minutes
- Short break: 5 minutes
- Long break: 15 minutes
- Long break interval: Every 4 pomodoros

To customize, modify the `TimerConfig.default()` method.

### Themes

pomotui supports all Textual built-in themes:
- textual-dark (default)
- textual-light
- nord
- dracula
- monokai
- catppuccin
- And more!

Press `Ctrl+\` and type "theme" to browse available themes. Your selection is automatically saved.

## 🏗️ Architecture

```
src/pomotui/
├── app.py                 # Main application
├── screens/               # Modal screens (tasks, stats)
├── widgets/               # Reusable UI components
├── models/                # Data models and business logic
├── database/              # SQLite management
└── timer/                 # Pomodoro state machine
```

See [CLAUDE.md](CLAUDE.md) for detailed architectural documentation.

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`uv run pytest`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

Please ensure:
- All tests pass
- Code is formatted with `ruff`
- Type hints are included
- New features have tests

## 📝 Roadmap

- [x] Pomodoro timer with pause/resume
- [x] Task creation and management
- [x] Statistics and analytics
- [x] Data export (CSV/JSON)
- [x] Theme persistence
- [x] Comprehensive test coverage
- [ ] Sound notifications
- [ ] Custom timer durations (UI for configuration)
- [ ] Task editing and deletion
- [ ] More detailed task analytics
- [ ] Calendar view

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Textual](https://textual.textualize.io/) by Textualize
- Inspired by the [Pomodoro Technique](https://francescocirillo.com/pages/pomodoro-technique) by Francesco Cirillo
- Package management by [uv](https://github.com/astral-sh/uv) from Astral

## 📧 Contact

Found a bug? Have a feature request? Please open an issue on GitHub.

---

**Made with ❤️ and 🍅**
