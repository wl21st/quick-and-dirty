## ADDED Requirements

### Requirement: System auto-detects city from external IP by default
The system SHALL automatically detect the user's city from their external IP address when no explicit city is provided. Auto-detection SHALL be the default behavior. The `--auto` flag SHALL be accepted for backward compatibility but SHALL NOT change behavior.

#### Scenario: No city argument triggers auto-detection
- **WHEN** user runs `python weather.py` with no city argument
- **THEN** the system queries a geolocation API and displays weather for the detected city

#### Scenario: Explicit city overrides auto-detection
- **WHEN** user runs `python weather.py "Paris"`
- **THEN** the system displays weather for "Paris" without calling the geolocation API

#### Scenario: Geolocation API returns valid city on auto-detection
- **WHEN** the geolocation API successfully returns a city name during auto-detection
- **THEN** the system uses that city to fetch and display weather data

#### Scenario: Geolocation API fails during auto-detection
- **WHEN** the geolocation API request fails (network error, rate limit, or no city in response)
- **THEN** the system displays an informative error message and exits with non-zero status

#### Scenario: Mutual exclusion enforced for conflicting arguments
- **WHEN** user provides both a city argument and the `--auto` flag
- **THEN** the system displays a usage error and exits without making API calls

#### Scenario: `--auto` flag with no city behaves as auto-detection
- **WHEN** user runs `python weather.py --auto`
- **THEN** the system performs auto-detection identically to the no-argument case