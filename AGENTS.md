# Agent Guide — weather-cli

This file provides instructions and conventions for agentic coding assistants (including Kilo agents, Claude Code, Cursor, Copilot) working in this repository.

## Project Overview

`weather-cli` is a Python command-line tool that fetches weather data with automatic IP-based geolocation. It uses:
- **uv** for dependency management and virtual envs
- **ruff** for linting and formatting (line length 88)
- **pytest** for testing
- **hatchling** as the build backend (PEP 517)
- **src layout**: `src/weather_cli/__init__.py` → package `weather_cli`
- Console script: `weather` → `weather_cli:main`

## Quick Start

```bash
# Install dependencies
make install          # or: uv sync --all-extras

# Run the tool
make run              # auto-detect location
make run ARGS="Tokyo" # explicit city

# Lint and format
make lint
make format

# Clean artifacts
make clean
```

## Build Commands

| Task | Command |
|------|---------|
| Install deps | `uv sync --all-extras` or `make install` |
| Create venv | `uv venv` (auto-created on first sync) |
| Build wheel | `uv build` (outputs to `dist/`) |
| Install in editable mode | `uv pip install -e .` |
| Run module directly | `uv run python -m weather_cli` |
| Run installed script | `uv run weather` (uses console script) |

## Lint & Format

```bash
# Lint only (fails on issues)
uv run ruff check .

# Auto-fix lint issues
uv run ruff check . --fix

# Format code
uv run ruff format .

# Check formatting without changing
uv run ruff format . --check

# Combine: format then lint
uv run ruff format . && uv run ruff check .
```

**Ruff config** (in `pyproject.toml`):
- Line length: 88
- Rules: E (pycodestyle), F (pyflakes), W (warning), I (isort), UP (pyupgrade), B (flake8-bugbear), C4 (comprehensions)

## Testing

```bash
# Run all tests
uv run pytest tests/ -v

# Run a single test file
uv run pytest tests/test_weather.py -v

# Run a single test function
uv run pytest tests/test_weather.py::test_get_weather_success -v

# Run with pattern matching
uv run pytest -k "test_retry" -v

# Stop on first failure
uv run pytest -x

# Show print statements
uv run pytest -s
```

**Test discovery:** `pytest` looks in `tests/` directory. Test files must be named `test_*.py` or `*_test.py`.

## Code Style Guidelines

### Imports
Standard library → third-party → local. Within each group, alphabetized. Use `ruff` (I rule) to sort automatically.

```python
import argparse
import json
import sys
import urllib.error
import urllib.request
```

Never use `from module import *`. Prefer explicit imports.

### Formatting
- **Line length:** 88 characters (ruff default)
- **Quotes:** Double quotes for strings (`"`), single for chars (`'`)
- **Indentation:** 4 spaces — no tabs
- **Trailing commas:** Use in multi-line collections
- **String concatenation:** Use parentheses, not backslashes
```python
msg = (
    "First line\n"
    "Second line"
)
```

### Type Hints
- Use type hints for all public function signatures
- Use built-in generics (`list[str]`, `dict[str, int]`) — requires Python 3.9+
- Return type: always annotate
- No `Any` unless truly dynamic
- Mutable defaults: never use mutable default arguments

```python
def get_weather(city: str) -> dict:
    ...

def main() -> None:
    ...
```

### Naming Conventions
- **Modules/Packages:** `snake_case` (`weather_cli`, `config_utils`)
- **Functions/Variables:** `snake_case` (`get_city_from_ip`, `max_retries`)
- **Classes:** `PascalCase` (`RetryConfig`, `FavoritesManager`)
- **Constants:** `UPPER_SNAKE_CASE` (`MAX_RETRIES`, `DEFAULT_DELAY`)
- **Private members:** leading underscore (`_internal_func`, `_cache`)

### Error Handling
- Catch specific exceptions, not bare `except:`
- Print user-friendly messages to `stderr` for errors (use `file=sys.stderr` if needed)
- Exit with non-zero status on unrecoverable errors (`sys.exit(1)`)
- Log retry attempts to `stderr` (not stdout)
- Do not expose raw tracebacks to end users unless `--debug` flag added

```python
try:
    response = urllib.request.urlopen(url, timeout=5)
except urllib.error.URLError as e:
    print(f"Error: Could not reach service ({e.reason})")
    sys.exit(1)
```

### Docstrings
- All public functions and classes must have docstrings
- Use concise one-line summary, optionally followed by description
- No strict style enforced (neither Google nor NumPy required), but be consistent

```python
def get_city_from_ip() -> str | None:
    """Detect user's city from external IP using ip-api.com."""
    ...
```

### CLI Arguments (argparse)
- Positional arguments for required inputs (city name is optional positional)
- Optional flags start with `--`, single-letter aliases with `-`
- Mutually exclusive groups for conflicting options
- Default to helpful error messages (`parser.error()`)
- Keep help text concise (< 88 chars where possible)

```python
parser = argparse.ArgumentParser(description="...")
parser.add_argument("city", nargs="?", default=None, help="...")
parser.add_argument("--auto", action="store_true", help="...")
args = parser.parse_args()
```

### Configuration Files
- Store in platform-appropriate config directory:
  - Linux/macOS: `~/.config/weather-cli/` (XDG)
  - Fallback: `~/.weather_cli/`
- JSON format only
- On write, use atomic temp file + rename if possible
- On read, handle missing/corrupt files by returning defaults

```json
{
  "retry": {"max_attempts": 3, "base_delay": 1.0, "max_delay": 30.0},
  "favorites": ["Daly City", "Mountain View"]
}
```

### Module Structure
- Place code in `src/weather_cli/` package
- `__init__.py` exports `main()` as the console script entry point
- Keep module-level variables minimal; wrap in functions if needed
- `if __name__ == "__main__":` block should simply call `main()`

### OpenSpec Integration
- `openspec/` directory contains change proposals with artifacts
- Tasks in `tasks.md` are checked with `- [ ]` / `- [x]` — update immediately after completing each task
- Before implementing, read all context files from `openspec status --json` apply instructions
- After completing all tasks in a change, artifacts should be marked done

## Common Workflows for Agents

When asked to "enhance", "fix", or "add feature":
1. Read `pyproject.toml` to understand project config
2. Check `Makefile` for available targets
3. Search `src/weather_cli/` for related code
4. Run `make lint` before committing changes
5. Keep changes minimal and scoped
6. Update `openspec` tasks with checkboxes if working on a change

## Makefile Targets

| Target | Purpose |
|--------|---------|
| `make install` | Install deps via `uv sync` |
| `make run` | Run with auto-detection |
| `make run ARGS="City"` | Run for specific city |
| `make test` | Run `pytest` |
| `make lint` | Run `ruff check .` |
| `make format` | Run `ruff format .` |
| `make clean` | Remove caches, venv, build artifacts |

## Pitfalls to Avoid

- Do not commit `.venv/`, `__pycache__/`, `.pytest_cache/`
- Do not hard-code API keys or secrets (none needed here)
- Keep network timeout values reasonable (< 30s)
- Respect rate limits: ip-api.com allows ~45 req/day from single IP
- Never block on user input in `get_weather()` or `get_city_from_ip()` — only in CLI flow
- When adding new CLI flags, update `main()` argument parser and help text

## Existing Rules

No Cursor or Copilot rule files found in this repository. Follow the above guidelines.

---

**Last updated:** 2026-04-29  
**Python:** ≥3.10  
**License:** MIT
