## Context

The current `weather-cli` tool makes singleattempt network calls to wttr.in and ip-api.com. When these calls fail due to transient issues (timeouts, rate limits, brief outages), users must manually re-run the command. There's no retry logic, leading to poor UX for flaky networks. Additionally, users cannot persist frequently-used cities—they must type them each time.

This change introduces resilience through automatic retries and a favorites system for quick city selection, improving reliability and convenience.

## Goals / Non-Goals

**Goals:**
- Implement retry logic with exponential backoff and jitter for ALL network calls (weather and geolocation)
- Make retry parameters configurable (max retries, base delay, max delay) via config file
- Add favorites management: save, list, add, remove cities persistently
- Provide interactive selection from favorites via `--favorites` flag
- Store favorites in a simple JSON file in user config directory
- Keep additional dependencies minimal (prefer stdlib; only add external if value clear)
- Ensure retries are transparent: users see progress (e.g., "Retry 1/3...")
- Allow disabling retries via config if user prefers

**Non-Goals:**
- Implementing a full configuration management system (key-value store); simple JSON is fine
- Caching weather responses (future enhancement)
- Syncing favorites across devices
- Supporting rich UI/colors (keep text-based)
- Adding other weather providers (stick to wttr.in)
- Changing the default behavior of auto-detection

## Decisions

### 1. Retry Strategy: Exponential Backoff with Full Jitter

**Decision**: Use exponential backoff: `delay = min(base * 2^attempt + random_jitter, max_delay)`. Retry on transient errors (timeouts, 5xx, rate-limit 429). Do NOT retry on 4xx client errors (except 429).

**Rationale**: Standard AWS retry pattern. Exponential gives increasing wait times; jitter prevents thundering herd. Full jitter: `random.uniform(0, delay)` makes retries less predictable and kinder to servers.

**Alternatives considered**:
- Fixed delay retries: Too aggressive, could exacerbate rate limiting
- Linear backoff: Slower to back off, less standard
- No jitter: Could cause synchronized retries from many clients

### 2. Retryable Errors

**Decision**: Retry on:
- `urllib.error.URLError` (timeout, network unreachable)
- `http.client.RemoteDisconnected`, `http.client.IncompleteRead`
- HTTP 5xx (Server Error)
- HTTP 429 (Too Many Requests) — with special handling: respect `Retry-After` header if present

Do NOT retry on:
- HTTP 4xx (except 429) — client error means request is invalid
- JSON decode errors after successful fetch (likely permanent bad response)

**Rationale**: Clear separation between transient (retry) vs permanent (fail fast) errors.

### 3. Config Location

**Decision**: Store config in platform-appropriate directory:
- Linux/macOS: `~/.config/weather-cli/config.json` (XDG) OR `~/.weather_cli/` (simpler)
- Windows: `%APPDATA%/weather-cli/config.json`

Fallback: project-local `.weather_cli/` if home dir not writable.

**Rationale**: Follows XDG spec on Unix; avoids cluttering home root. Simple JSON file is human-editable.

**Alternatives considered**:
- Environment variables only: Too limited for favorites list
- Single `.weather_cli` folder in home: Simpler but not XDG-compliant; still acceptable

### 4. Favorites Storage Format

**Decision**: JSON file at config dir: `favorites.json` with structure:
```json
{
  "cities": ["Daly City", "New York", "London"],
  "last_used": "London"
}
```
Optionally add metadata per city (nickname, region) later—keep flat array for now.

**Rationale**: Simple, readable, easily editable. Can extend to objects later if needed.

**Alternatives considered**:
- SQLite: Overkill for list of strings
- Plain text (one per line): Less structured; JSON is standard

### 5. Interactive Selection UI

**Decision**: Use simple numbered menu in terminal: print numbered list, prompt user to enter number. No external dependency. Support fuzzy search if user types partial match.

**Rationale**: Avoids external deps like `questionary`/`inquirer` which would require adding to pyproject. Keeps uv install simple.

**Alternatives considered**:
- `questionary` library: Nice UX but adds dependency and complexity
- `pick` library: Similar but still external
- Simple loop with `input()`: Zero deps, good enough

### 6. Configuring Retry Parameters

**Decision**: Add global settings in `config.json`:
```json
{
  "retry": {
    "max_attempts": 3,
    "base_delay": 1.0,   // seconds
    "max_delay": 30.0
  },
  "favorites": ["Daly City", "Mountain View"]
}
```
Allow per-request overrides via environment variables (rarely needed).

**Rationale**: Users can tune for their network conditions. Defaults (3 retries, 1s base) are reasonable.

### 7. Where to Apply Retries

**Decision**: Create a `retryable()` decorator/wrapper function that takes a callable and retries it. Apply to:
- `fetch_weather()` in `weather.py` (the urllib.urlopen block)
- `detect_city()` in `geolocation.py`

Both functions will raise custom exceptions (`WeatherError`, `GeolocationError`) on failure rather than calling `sys.exit()`. The decorator will catch transient exceptions and retry; after exhausting retries it re-raises the last exception for `cli.py` to handle (print + exit).

Do NOT wrap argument parsing or city resolution logic — only network I/O.

**Rationale**: Clean separation; easily testable; reusable. Centralized exit handling in `cli.main()` improves testability of core logic.

### 8. Visibility into Retries

**Decision**: Print informative messages to stderr on retries:
```
Weather request failed (Timeout), retrying in 2s... (1/3)
```
On final failure, print error as before.

**Rationale**: Users understand what's happening; not silent.

### 9. Module Architecture — Full Package Split

**Decision**: Refactor from single-file monolith into a multi-module package with clear separation of concerns:

```
src/weather_cli/
├── __init__.py      # package marker (minimal)
├── cli.py           # main(), argparse, orchestration, exit handling
├── weather.py       # fetch_weather(city) → WeatherData; display_weather(data, city)
├── geolocation.py   # detect_city() → str | None
├── retry.py         # @retryable decorator (custom, stdlib only)
├── config.py        # load_config(), save_config(), get_retry_config(), get_favorites_path(), global settings
├── favorites.py     # load/save/add/remove/pick
├── exceptions.py    # WeatherError, GeolocationError, ConfigError (base WeatherCLIError)
└── types.py         # TypedDicts and type aliases (WeatherData, CityName)
```

Each module ≤ 80 lines. Dependencies flow inward: `cli` → (`weather`, `geolocation`, `favorites`, `config`); `weather`/`geolocation` → `retry`; `retry` → (optional lazy `config`); `favorites` → `config`; `config` → `exceptions`.

**Rationale**:
- Testability: Each module can be unit-tested in isolation (mock network, filesystem, input)
- Single responsibility: Each file has one clear purpose
- Maintainability: Easier to locate and modify behavior
- Aligns with design's explicit instruction to "Create config.py module", "Create retry.py module"

**Alternatives considered**:
- Monolith + helpers (`retry.py`, `config.py` only): Keeps weather/geolocation in `__init__.py`; lower initial churn but poor cohesion, harder to test
- Sub-packages: Overkill for ~400 total lines

**Implementation approach**:
1. Create `exceptions.py` and `types.py` (no dependencies)
2. Create `weather.py`: move `fetch_weather` (network + error → raise `WeatherError`) and `display_weather` (printing)
3. Create `geolocation.py`: move `detect_city` (raise `GeolocationError` on failure)
4. Create `retry.py`: custom decorator with exponential backoff + jitter
5. Create `config.py`: XDG directory resolution, atomic JSON load/save, global `settings` object
6. Create `favorites.py`: CRUD + interactive `pick_favorite()`
7. Rename `__init__.py` → `cli.py`: host `main()`, wire everything together, centralized `try/except` → `sys.exit(1)`
8. Update `pyproject.toml` if needed (no new runtime deps)

**Error handling shift**: Functions in `weather.py` and `geolocation.py` raise exceptions instead of calling `sys.exit()`. `cli.py` is the only module that exits.

## Risks / Trade-offs

**Risk**: Retries increase total time on failure, potentially frustrating users who want fast failure.
- **Mitigation**: Default retry count is low (3), backoff is quick (1s base). Users can set `max_attempts=1` to disable.

**Risk**: Too many retries could hammer the weather API during extended outage.
- **Mitigation**: Cap max_delay at 30s; total retry duration bounded. Respect 429 Retry-After header.

**Risk**: Favorites file may not be writable (permissions, read-only filesystem).
- **Mitigation**: Gracefully fall back to in-memory only; warn user. Don't crash.

**Trade-off**: Adding retry logic increases code complexity (~30 extra lines).
- Acceptable for improved reliability.

**Trade-off**: Interactive selection with simple numbered menu is less user-friendly than searchable UI.
- Mitigate by supporting fuzzy prefix matching: user can type "new" to match "New York".

## Migration Plan

1. Release new version with retry and favorites as opt-in via flags (`--favorites`, `--list`, `--add`). Auto-detection and explicit city remain default.
2. No breaking changes to default usage: `python weather.py` still works (now with silent retries)
3. Favorites file created on first use
4. Document new flags in help text (`-h`) and README
5. Users who dislike retries can set `"max_attempts": 1` in config
6. Rollback: remove new code or set config to disable features

## Open Questions

- Should retry apply to geolocation API too? **Decision**: Yes, same logic, separate retry config if needed but shared.
- Should we add a `--no-retry` flag to override config per invocation? **Decision**: Yes, for debugging.
- How to handle keyboard interrupt during retry wait? **Decision**: Let `KeyboardInterrupt` exit immediately.
- Should favorites support aliases/nicknames? **Decision**: Out of scope; can extend later.
