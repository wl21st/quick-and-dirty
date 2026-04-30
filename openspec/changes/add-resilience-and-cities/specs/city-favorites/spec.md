## ADDED Requirements

### Requirement: Persistently store and manage a list of favorite cities
The system SHALL maintain a persistent list of favorite cities across sessions. The system SHALL provide commands to list, add, and remove cities from this list. Favorites SHALL be stored in a JSON file in the user's config directory.

#### Scenario: Add a city to favorites
- **WHEN** user runs `python weather.py --add "Paris"`
- **THEN** "Paris" is appended to the favorites list (if not already present)
- **AND** the system saves the updated list to the favorites file
- **AND** prints confirmation message

#### Scenario: Add current auto-detected city to favorites (no arg)
- **WHEN** user runs `python weather.py --add` with no city argument
- **THEN** the system determines the current city (via auto-detection or explicit)
- **AND** adds that city to favorites
- **AND** prints confirmation with the city name

#### Scenario: List all favorite cities
- **WHEN** user runs `python weather.py --list` (or `-l`)
- **THEN** the system reads the favorites file and prints each city, one per line
- **AND** optionally shows an indicator for the last used city

#### Scenario: Remove a city from favorites
- **WHEN** user runs `python weather.py --remove "Tokyo"`
- **THEN** "Tokyo" is removed from the favorites list if present
- **AND** the file is updated
- **AND** prints confirmation or "not found" message

#### Scenario: Selecting from favorites interactively
- **WHEN** user runs `python weather.py --favorites` (or `-f`)
- **THEN** the system displays a numbered list of saved cities
- **AND** prompts the user to select a number (or type a partial name for fuzzy match)
- **AND** fetches and displays weather for the selected city

#### Scenario: Favorites file does not exist initially
- **WHEN** the favorites file is missing (first run)
- **THEN** the system creates an empty favorites list in memory
- **AND** operations like `--list` show empty list without error
- **AND** `--add` creates the file on disk

#### Scenario: Favorites file is corrupted or unreadable
- **WHEN** the favorites JSON file cannot be parsed
- **THEN** the system warns the user and resets to empty favorites
- **AND** creates a fresh valid favorites file

#### Scenario: Adding duplicate city to favorites
- **WHEN** user runs `--add` for a city already in favorites
- **THEN** the system does NOT duplicate the entry
- **AND** prints a message that city is already saved

#### Scenario: Removing non-existent city
- **WHEN** user runs `--remove` for a city not in favorites
- **THEN** the system prints "city not found in favorites" without error