## Why

Network requests to weather and geolocation APIs can fail transiently due to timeouts, rate limits, or temporary outages. Currently, a single failure causes the script to exit immediately, forcing users to manually retry. Additionally, users frequently check weather for the same set of cities (e.g., home, work), but must type them repeatedly. There's no way to save favorite cities for quick selection.

## What Changes

- Add retry logic with exponential backoff for both weather and geolocation API calls
- Make retry behavior configurable (max retries, initial delay, max delay)
- Add a persistent favorites file to store commonly used city names
- Add `--favorites` (`-f`) flag to pick from saved cities interactively
- Add `--list` (`-l`) flag to display saved favorite cities
- Add `--add` flag to add current city (or specified city) to favorites
- Add `--remove` flag to delete a city from favorites
- Store favorites in `~/.weather_cli/favorites.json` (or project-local)
- **BREAKING**: Default behavior changes: network failures now retry (3x) before failing, adding slight delay on errors

## Capabilities

### New Capabilities

- `network-retry`: Retry failed network requests with exponential backoff and jitter
- `city-favorites`: Persistently store and manage a list of favorite cities for quick selection
- `cli-interactive`: Interactive city selection from favorites via terminal menu

### Modified Capabilities

*(none)*

## Impact

- `weather.py` → `src/weather_cli/__init__.py`: Major refactor to add retry wrapper, favorites management, config handling
- New config directory: `~/.config/weather-cli/` (or `~/.weather_cli/`) for favorites and settings
- External dependencies: potentially `questionary` or `inquirer` for interactive selection (or use simple `input()` loop)
- CLI changes: new flags `-f/--favorites`, `-l/--list`, `--add`, `--remove`
- Behavior change: automatic retries on failure (user-visible as waiting before final error)
- No change to return value structure
