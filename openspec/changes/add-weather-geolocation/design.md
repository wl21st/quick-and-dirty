## Context

The current `weather.py` script is a simple utility that fetches weather data from wttr.in with a hardcoded default city ("Daly City"). To check weather for other locations, users must manually edit the code. There is no command-line interface and no automatic location detection.

The enhancement will transform this into a more practical CLI tool that accepts city input and can auto-detect the user's location based on their external IP address.

## Goals / Non-Goals

**Goals:**
- Add command-line argument support using Python's `argparse` module
- Implement automatic city detection via IP geolocation using a free public API as the DEFAULT behavior
- Remove the hard-coded "Daly City" fallback; location is always resolved (explicit city or auto-detected)
- Maintain clean, readable code with proper error handling
- Keep the script standalone with minimal dependencies
- Retain `--auto` flag for backward compatibility (now a no-op when city is absent)
- Explicit city argument takes precedence over auto-detection

**Non-Goals:**
- Supporting multiple cities in a single request
- Caching location results (may be added later)
- Using paid/registered API services (stick to free, no-auth APIs)
- GUI or web interface (CLI only)
- Changing the output format or return value structure

## Decisions

### 1. Use `argparse` for CLI parsing

**Decision**: Use Python's built-in `argparse` module instead of `sys.argv` manual parsing.

**Rationale**: `argparse` provides automatic help generation (`-h`), type validation, and clear error messages. It's standard library, no external dependency. Supports optional positional argument for city name and optional flag for auto-detection mode.

**Alternatives considered**:
- `sys.argv` direct parsing: Too manual, no validation, reinventing the wheel
- `click` library: External dependency, overkill for this use case

### 2. Use ip-api.com for IP geolocation

**Decision**: Use `http://ip-api.com/json/` (no-key, free tier) to get location data from external IP.

**Rationale**: 
- No API key required, straightforward HTTP GET
- Returns JSON with city, region, country, lat/long
- Free tier allows ~45 requests/day from single IP (adequate for personal use)
- Simple, no authentication complexity

**Endpoint**: `http://ip-api.com/json/` returns JSON with `city` field

**Alternatives considered**:
- `ipinfo.io`: Requires token for >50k requests, but also free tier. Slightly more complex.
- `freegeoip.app`: Similar but less documentation
- `wttr.in` itself has location support but not for IP-to-city mapping

### 3. Fallback chain for city resolution

**Decision**: Implement a clear priority order:
1. If explicit city argument provided → use it
2. If `--auto` flag set → fetch from IP geolocation API
3. If neither → use default "Daly City"

**Rationale**: Ensures script always works, even if network/API fails. Explicit user input takes precedence. Auto-detection is opt-in via flag to avoid unnecessary network calls.

**Alternatives considered**:
- Auto-detect by default when no city given: Could surprise users, adds network call every run
- Always auto-detect and ignore CLI arg: Conflicts with explicit user intent

### 4. Use `requests` library vs `urllib`

**Decision**: Keep using `urllib.request` (already in use) for consistency.

**Rationale**: Already imported in existing code, no additional dependency. `urllib` is perfectly capable for both APIs. Adding `requests` would be an unnecessary external dependency.

**Alternatives considered**:
- Switch to `requests`: More ergonomic but external dependency

### 5. Error handling strategy

**Decision**: Wrap network calls in try/except blocks, print user-friendly error messages, and exit gracefully.

**Rationale**: Network failures happen. Users should understand what went wrong (timeout, invalid city, API failure). Script should not crash with unhandled exceptions.

**Specifics**:
- `urllib.error.URLError`: Network/API unreachable
- `KeyError`/`IndexError`: Unexpected API response format
- Fallback to default city only when appropriate (not when explicit city fails)

## Risks / Trade-offs

**Risk**: IP geolocation API rate limits or downtime
- **Mitigation**: Use fallback default city or allow explicit city input as workaround. Consider adding a `--no-auto` flag to skip geolocation even with `--auto` if persistent issues.

**Risk**: Inaccurate city detection (VPNs, corporate NAT, ISP-level location)
- **Mitigation**: Accept as limitation of public IP geolocation. User can always provide explicit city.

**Risk**: External API changes or deprecation
- **Mitigation**: The IP geolocation API (ip-api) is stable but if it fails, switch to alternative (ipinfo.io). Keep IP fetch logic isolated in `get_city_from_ip()` for easy replacement.

**Trade-off**: Using a free API means rate limits; not suitable for automated frequent use
- Document the limitation in comments or README

**Trade-off**: Auto-detection adds network latency (~200-500ms)
- Acceptable for CLI tool; could add `--no-auto` skip, but flag already opt-in

## Migration Plan

This change modifies existing default behavior (was: "Daly City" → now: auto-detect). Migration steps:

1. Deploy updated `weather.py` script with awareness that `python weather.py` (no args) now triggers IP-based auto-detection
2. Existing usage with no arguments will see a DIFFERENT default city (their IP-detected location) instead of "Daly City"
3. Users who relied on the "Daly City" default must now explicitly run `python weather.py "Daly City"`
4. New usage patterns:
   - `python weather.py "New York"` → explicit city (unchanged)
   - `python weather.py --auto` → explicit auto-detect (deprecated, same as no-arg behavior)
5. Communication: Update any scripts, documentation, or shared aliases that assumed "Daly City" default

Rollback: revert to previous script version to restore "Daly City" default.

## Open Questions

- Should `--auto` and explicit city be mutually exclusive? **Decision**: Yes, design prevents both being used simultaneously to avoid confusion.
- Should the script cache the detected city to avoid repeated API calls? **Decision**: Not initially; could be added later with `--cache` flag if needed.
- Should we add a `--list` or search feature for city names? **Decision**: Out of scope for this change.
