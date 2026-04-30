## 1. Configuration and Favorites Management

- [ ] 1.1 Create `config.py` module with config directory detection (XDG compliant)
- [ ] 1.2 Implement `load_config()` that reads `~/.config/weather-cli/config.json` (or fallback)
- [ ] 1.3 Implement `save_config()` to write config with defaults if missing
- [ ] 1.4 Default config structure: `{"retry": {"max_attempts": 3, "base_delay": 1.0, "max_delay": 30.0}, "favorites": []}`
- [ ] 1.5 Implement `load_favorites()` and `save_favorites()` convenience functions
- [ ] 1.6 Handle file-not-found, permission errors, and JSON corruption gracefully (reset to defaults)

## 2. Retry Mechanism

- [ ] 2.1 Create `retry.py` module with `retryable()` decorator function
- [ ] 2.2 Implement exponential backoff: `delay = min(base * 2^attempt + random_jitter, max_delay)`
- [ ] 2.3 Detect transient errors: `URLError`, `HTTPError` with status 5xx or 429
- [ ] 2.4 For HTTP 429, read `Retry-After` header and use that delay (overrides backoff)
- [ ] 2.5 Print retry message to stderr: `"Retry {attempt}/{max} after {delay:.1f}s ({reason})"`
- [ ] 2.6 After final failure, re-raise the last exception for caller to handle
- [ ] 2.7 Add `--no-retry` CLI flag to bypass retry (for debugging)
- [ ] 2.8 Make retry parameters configurable via config file

## 3. Integrate Retry into Network Calls

- [ ] 3.1 Wrap `get_weather()` network call with `@retryable()` decorator (or explicit wrapper)
- [ ] 3.2 Wrap `get_city_from_ip()` network call with `@retryable()`
- [ ] 3.3 Ensure both functions respect the `--no-retry` flag (conditional decorator or wrapper check)
- [ ] 3.4 Verify that error messages after retry exhaustion are clear

## 4. CLI Extensions: Favorites Commands

- [ ] 4.1 Add `--add <city>` and `--add` (uses current city) arguments
- [ ] 4.2 Add `--remove <city>` argument
- [ ] 4.3 Add `--list` (`-l`) argument to display favorites
- [ ] 4.4 Add `--favorites` (`-f`) argument to trigger interactive selection
- [ ] 4.5 Ensure mutual exclusion: `--favorites`, `--list`, `--add`, `--remove` are exclusive with each other and with explicit city
- [ ] 4.6 Update help text to document all new flags

## 5. Interactive Favorites Picker

- [ ] 5.1 Implement `select_from_favorites()` function that loads favorites and displays numbered menu
- [ ] 5.2 Support fuzzy prefix matching: user can type "par" to match "Paris"
- [ ] 5.3 Validate selection input (number or partial name), re-prompt on invalid
- [ ] 5.4 Handle empty favorites list with friendly message and exit
- [ ] 5.5 Allow user to abort with Ctrl+C or empty input (exit gracefully)
- [ ] 5.6 Return selected city string to main flow

## 6. Main Flow Integration

- [ ] 6.1 Update `main()` to parse all new flags (`--add`, `--remove`, `--list`, `--favorites`, `--no-retry`)
- [ ] 6.2 Implement command dispatch: if `--add` → add_favorite_flow(); `--remove` → remove_favorite_flow(); etc.
- [ ] 6.3 For `--add` without argument: call `get_city_from_ip()` or use provided city to determine what to add
- [ ] 6.4 For `--favorites`: call interactive selector, then proceed to weather fetch
- [ ] 6.5 Ensure retry decorator respects `--no-retry` flag
- [ ] 6.6 Maintain existing behavior: plain invocation → auto-detect → retry → weather

## 7. Testing & Validation

- [ ] 7.1 Test retry logic: mock failing first request, success on second
- [ ] 7.2 Test max retry exhaustion: mock all requests failing, verify error message
- [ ] 7.3 Test 429 with Retry-After: mock 429 response, verify correct wait
- [ ] 7.4 Test favorites add/list/remove manually
- [ ] 7.5 Test interactive selector with multiple cities
- [ ] 7.6 Test `--no-retry` flag: immediate failure on first error
- [ ] 7.7 Verify config file creation on first run
- [ ] 7.8 Test corrupted favorites file recovery
- [ ] 7.9 Test mutual exclusion errors for conflicting flags
- [ ] 7.10 End-to-end: `python weather.py --add "Tokyo"` then `python weather.py --list` then `python weather.py --remove "Tokyo"`