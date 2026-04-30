## ADDED Requirements

### Requirement: Network requests are automatically retried on transient failures
The system SHALL automatically retry failed network requests to weather and geolocation APIs using exponential backoff with jitter. The system SHALL NOT retry on permanent errors (HTTP 4xx except 429, invalid responses).

#### Scenario: Retry on transient network timeout
- **WHEN** a network request fails with a timeout or temporary connection error
- **THEN** the system waits using exponential backoff and retries the request
- **AND** the system prints a retry message to stderr showing attempt number and delay

#### Scenario: Retry on HTTP 5xx server errors
- **WHEN** the weather or geolocation API returns HTTP 5xx
- **THEN** the system retries with exponential backoff up to max attempts
- **AND** after exhausting retries, exits with error message

#### Scenario: Respect Retry-After header on HTTP 429
- **WHEN** the API responds with HTTP 429 (Too Many Requests) and includes a `Retry-After` header
- **THEN** the system waits for the specified duration before retrying
- **AND** the `Retry-After` duration overrides the calculated backoff delay

#### Scenario: Do NOT retry on HTTP 4xx (except 429)
- **WHEN** the API returns HTTP 404 (Not Found) or other 4xx error
- **THEN** the system fails immediately without retrying
- **AND** displays the error message to the user

#### Scenario: Retry configuration is respected
- **WHEN** network failures occur
- **THEN** the system retries at most `max_attempts` times (default 3)
- **AND** delays between retries follow: `delay = min(base_delay * 2^attempt + jitter, max_delay)`

#### Scenario: User can disable retries via config
- **WHEN** the config file sets `"max_attempts": 1`
- **THEN** the system makes exactly one attempt per request (no retries)

#### Scenario: Final failure after all retries
- **WHEN** all retry attempts are exhausted
- **THEN** the system prints an error message summarizing the failure
- **AND** exits with non-zero status