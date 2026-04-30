## ADDED Requirements

### Requirement: User can specify city via command-line argument
The system SHALL accept an optional city name as a positional command-line argument. When provided, it overrides the auto-detection default.

#### Scenario: User provides city name as argument
- **WHEN** user runs `python weather.py "New York"`
- **THEN** the system displays weather for "New York"

#### Scenario: User provides city name with spaces
- **WHEN** user runs `python weather.py "San Francisco"`
- **THEN** the system displays weather for "San Francisco" (spaces handled correctly)

#### Scenario: No argument provided uses auto-detection
- **WHEN** user runs `python weather.py` with no arguments
- **THEN** the system auto-detects the city from the external IP address and displays weather for that city
