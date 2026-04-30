## 1. Architecture Refactor — Core Module Split

- [ ] 1.1 Create `src/weather_cli/exceptions.py` with base `WeatherCLIError` and subclasses `WeatherError`, `GeolocationError`, `ConfigError`
- [ ] 1.2 Create `src/weather_cli/types.py` with type aliases (`CityName = str`) and `WeatherData` TypedDict matching wttr.in response structure
- [ ] 1.3 Create `src/weather_cli/weather.py`:
   - Move `fetch_weather(city)` logic from current `__init__.py`
   - Raise `WeatherError` on any failure (no `print`/`sys.exit`)
   - Add `display_weather(data, city)` to handle printing
- [ ] 1.4 Create `src/weather_cli/geolocation.py`:
   - Move `detect_city()` logic from current `__init__.py`
   - Raise `GeolocationError` on failure (no `print`/`sys.exit`)
- [ ] 1.5 Create `src/weather_cli/cli.py`:
   - Move `main()` from `__init__.py`
   - Set up argparse with all flags (existing + new: `--add`, `--remove`, `--list`, `--favorites`, `--no-retry`)
   - Implement city resolution and command dispatch
   - Wrap entire flow in `try/except (WeatherError, GeolocationError, ConfigError)` → print to stderr and `sys.exit(1)`
- [ ] 1.6 Update `src/weather_cli/__init__.py` to be minimal package marker (optional re-export of `main` or empty)
- [ ] 1.7 Verify baseline: `uv run weather` and `uv run weather "Tokyo"` work with identical behavior to pre-refactor (no retry yet)

## 2. Retry Mechanism (Custom Stdlib Implementation)

- [ ] 2.1 Create `src/weather_cli/retry.py` with `retryable()` decorator factory
- [ ] 2.2 Implement exponential backoff: `delay = min(base * 2^(attempt-1) + random.uniform(0, delay), max_delay)`
- [ ] 2.3 Detect transient exceptions: `urllib.error.URLError`, `http.client.HTTPError` (status 5xx or 429)
- [ ] 2.4 For HTTP 429, read `Retry-After` header (support both seconds and HTTP-date) and use that delay (overrides calculated backoff)
- [ ] 2.5 Print retry message to stderr: `"Retry {attempt}/{max} after {delay:.1f}s ({reason})"`
- [ ] 2.6 After final attempt, re-raise the last caught exception
- [ ] 2.7 Support `--no-retry`: decorator checks `config.settings.retry_disabled` at call time and bypasses if True
- [ ] 2.8 Make retry parameters configurable: read from `config.settings.retry` (max_attempts, base_delay, max_delay) at call time (not decoration)
- [ ] 2.9 Ensure `KeyboardInterrupt` propagates immediately (no retry wait)

## 3. Configuration & Favorites Management

- [ ] 3.1 Implement `config.get_config_dir()` with XDG-first resolution: `XDG_CONFIG_HOME/weather-cli`, then `~/.config/weather-cli`, then `~/.weather_cli`, finally `./.weather_cli`; create directory if needed
- [ ] 3.2 Define `RetryConfig` dataclass in `config.py` with defaults (3, 1.0, 30.0)
- [ ] 3.3 Create global `config.settings` object holding `retry: RetryConfig` and `retry_disabled: bool`
- [ ] 3.4 Implement `config.load_config()`: read JSON from `get_config_path()`, handle missing/corrupt by resetting to defaults and writing fresh file
- [ ] 3.5 Implement `config.save_config()`: atomic write via temp file + rename
- [ ] 3.6 Add `config.set_retry_disabled(flag)` and `config.is_retry_disabled()`
- [ ] 3.7 Create `favorites.py` with `get_favorites_path()` (same dir as config)
- [ ] 3.8 Implement `favorites.load_favorites()` → `list[CityName]` (empty list if missing/corrupt)
- [ ] 3.9 Implement `favorites.save_favorites(cities: list[CityName])` atomic write
- [ ] 3.10 Implement `add_favorite(city)`: append if not present, save, optionally update `last_used`
- [ ] 3.11 Implement `remove_favorite(city)`: remove if present, save, handle not-found gracefully
- [ ] 3.12 Implement `list_favorites()` → prints numbered list to stdout
- [ ] 3.13 Implement `pick_favorite()` interactive menu:
   - Show numbered list
   - Accept number or fuzzy prefix; re-prompt on invalid/ambiguous
   - Support Ctrl+C / empty input to cancel (return None)
   - Update `last_used` on successful selection

## 4. Wire Retry into Network Layer

- [ ] 4.1 Apply `@retryable()` to `fetch_weather` in `weather.py`
- [ ] 4.2 Apply `@retryable()` to `detect_city` in `geolocation.py`
- [ ] 4.3 Verify that `WeatherError`/`GeolocationError` raised after final retry are caught by `cli.main()`
- [ ] 4.4 Confirm retry messages go to stderr and final error messages to stderr

## 5. CLI Extensions & Main Flow Integration

- [ ] 5.1 Add CLI arguments: `--add [city]` (optional arg), `--remove <city>`, `--list` (`-l`), `--favorites` (`-f`), `--no-retry`
- [ ] 5.2 Configure mutually exclusive groups: exactly one of [default get, `--favorites`, `--list`, `--add`, `--remove`] permitted
- [ ] 5.3 Implement `--add` path:
   - Determine city: if positional arg provided use it; else call `detect_city()`; if detection fails, error
   - Call `favorites.add_favorite(city)`, print confirmation
- [ ] 5.4 Implement `--remove` path:
   - Call `favorites.remove_favorite(city)`, print result (added/removed or not found)
- [ ] 5.5 Implement `--list` path:
   - Call `favorites.list_favorites()` and exit
- [ ] 5.6 Implement `--favorites` path:
   - Call `city = favorites.pick_favorite()`
   - If city is None (canceled), exit with code 0 quietly
   - Else proceed to fetch and display weather for selected city
- [ ] 5.7 Default path (no special flags):
   - Resolve city: if positional arg → use it; else → `detect_city()`
   - If detection fails, print error and exit 1
   - Fetch weather and display
- [ ] 5.8 Early flag processing: if `--no-retry` → `config.set_retry_disabled(True)`
- [ ] 5.9 Update argparse help text for all flags, keep descriptions < 88 chars where feasible

## 6. Testing & Validation

- [ ] 6.1 Create `tests/` directory with `conftest.py` (fixtures for temp config dir)
- [ ] 6.2 Unit test `retry.retryable`:
   - Mock function that fails twice then succeeds → verify 3 calls, appropriate delays
   - Mock function that always fails → verify max attempts reached, last exception raised
   - Mock HTTP 429 with `Retry-After` header → verify wait matches header
   - Test jitter within [0, delay] bounds
   - Test `--no-retry` bypass (single call)
- [ ] 6.3 Unit test `weather.fetch_weather`:
   - Mock successful wttr.in response → returns parsed dict
   - Mock 404 → raises `WeatherError` with "not found" message
   - Mock 500 → raises `WeatherError`
   - Mock network timeout → raises `WeatherError`
- [ ] 6.4 Unit test `weather.display_weather`:
   - Capture stdout, verify formatted output matches expected lines
- [ ] 6.5 Unit test `geolocation.detect_city`:
   - Mock successful ip-api response → returns city
   - Mock missing city field → returns None or raises? (per design: returns None)
   - Mock network failure → raises `GeolocationError`
- [ ] 6.6 Unit test `config` module:
   - Missing config file → defaults loaded
   - Corrupt JSON → resets to defaults and writes fresh file
   - Valid config → loads values correctly
   - Atomic write: verify temp file replaced
- [ ] 6.7 Unit test `favorites` module:
   - Add unique city → list grows
   - Add duplicate → no duplicate
   - Remove existing → removed
   - Remove missing → no error, list unchanged
   - Save/load round-trip
- [ ] 6.8 Unit test `favorites.pick_favorite` with mocked `input()`:
   - Valid number → returns city
   - Valid partial prefix → returns unique match
   - Ambiguous partial → re-prompts
   - Invalid number → re-prompts
   - Empty/Ctrl+C → returns None
- [ ] 6.9 Integration test: full flow `--add` → `--list` → `--remove` using temp dir
- [ ] 6.10 Integration test: `--favorites` interactive with mocked input
- [ ] 6.11 End-to-end: `uv run weather "London"` succeeds (mocking network)
- [ ] 6.12 End-to-end: `uv run weather` auto-detects (mock detect_city)
- [ ] 6.13 Test `--no-retry` with always-failing mock → verify single attempt only
- [ ] 6.14 Test mutual exclusion: `weather "Tokyo" --favorites` triggers argparse error
- [ ] 6.15 Run `make lint` and `make format`; ensure zero issues; fix if needed
- [ ] 6.16 Verify help text: `uv run weather --help` shows all flags concisely
