## Why

The current `weather.py` script has a hardcoded default city and requires code modification to check weather for different locations. Users need the ability to dynamically specify a city via command-line arguments, and to automatically detect their location based on their gateway's external IP address. This enhances usability and makes the tool more practical for everyday use.

## What Changes

- Add command-line argument parsing (`argparse`) to accept city name as an optional positional parameter
- Remove hard-coded default "Daly City"; auto-detection is now the default behavior
- Implement IP geolocation using a public IP geolocation API to detect city from external IP
- Update the main block to: use explicit city if provided, otherwise auto-detect
- Add error handling for network failures and invalid locations
- Maintain backward compatibility with `--auto` flag (deprecated but accepted)

## Capabilities

### New Capabilities

- `cli-input`: Accept city name as command-line argument using argparse
- `ip-geolocation`: Automatically detect user's city from external IP address using a geolocation API

### Modified Capabilities

*(none)*

## Impact

- `weather.py` - Modified to support CLI arguments and IP-based location detection
- New external dependency: IP geolocation API (e.g., ip-api.com)
- CLI interface: `python weather.py [city]` (auto-detect by default when no city given)
- `--auto` flag retained for backward compatibility but is now a no-op
- Return value unchanged (still returns weather data dictionary)
