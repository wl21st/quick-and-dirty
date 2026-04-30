## 1. CLI Argument Parsing

- [x] 1.1 Import `argparse` module
- [x] 1.2 Create argument parser with description
- [x] 1.3 Add positional optional argument for city name
- [x] 1.4 Add `--auto` flag for IP-based geolocation
- [x] 1.5 Add `--help` automatically via argparse (standard behavior)
- [x] 1.6 Parse arguments in `if __name__ == "__main__"` block

## 2. IP Geolocation Implementation

- [x] 2.1 Create `get_city_from_ip()` function
- [x] 2.2 Query `http://ip-api.com/json/` to get location data
- [x] 2.3 Extract city name from JSON response
- [x] 2.4 Handle errors: network failures, missing city field, API errors
- [x] 2.5 Return city string or None on failure

## 3. Main Flow Integration

- [x] 3.1 Refactor `get_weather()` to accept explicit city parameter (already does)
- [x] 3.2 Implement decision logic in main: prioritize CLI arg, then `--auto`, then default
- [x] 3.3 Add mutual exclusion check: error if both city arg and `--auto` provided
- [x] 3.4 Call `get_city_from_ip()` when `--auto` flag is set
- [x] 3.5 Pass resolved city to `get_weather()`

## 4. Error Handling & UX

- [x] 4.1 Wrap IP geolocation call in try-except for `URLError`
- [x] 4.2 Validate city name before passing to wttr.in (if empty/invalid)
- [x] 4.3 Print clear error messages for failure modes:
  - Invalid city (HTTP error, city not found)
  - Network failure reaching geolocation API
  - Conflicting arguments (both city and --auto)
- [x] 4.4 Exit with non-zero status on errors

## 5. Testing & Validation

- [x] 5.1 Test with valid city: `python weather.py "London"`
- [x] 5.2 Test with no arguments (default city)
- [x] 5.3 Test with `--auto` flag (verify city detection)
- [x] 5.4 Test error case: invalid city name
- [x] 5.5 Test mutual exclusion: both city and `--auto`
- [x] 5.6 Verify error messages are user-friendly
