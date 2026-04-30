import argparse
import json
import sys
import urllib.error
import urllib.request


def get_weather(city):
    encoded_city = city.replace(" ", "+")
    url = f"https://wttr.in/{encoded_city}?format=j1"
    try:
        with urllib.request.urlopen(url) as response:
            if response.status != 200:
                print(
                    f"Error: Could not fetch weather for '{city}'. "
                    f"Status: {response.status} {response.reason}"
                )
                sys.exit(1)
            data = json.loads(response.read())
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(
                f"Error: City '{city}' not found. "
                "Please check the city name and try again."
            )
        else:
            print(
                f"Error: HTTP {e.code} - {e.reason} when fetching weather for '{city}'"
            )
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Error: Could not reach weather service ({e.reason})")
        sys.exit(1)

    # Validate response structure
    if not data.get("current_condition"):
        print(
            f"Error: No weather data available for '{city}'. "
            "The city may not exist or data unavailable."
        )
        sys.exit(1)

    current = data["current_condition"][0]
    print(f"\n{city} Weather")
    print(f"Temp: {current['temp_C']}°C ({current['temp_F']}°F)")
    print(f"Feels Like: {current['FeelsLikeC']}°C")
    print(f"Condition: {current['weatherDesc'][0]['value']}")
    print(f"Humidity: {current['humidity']}%")
    print(f"Wind: {current['windspeedKmph']} km/h {current['winddir16Point']}")

    return data


def get_city_from_ip():
    """Query a geolocation API to detect city from external IP address."""
    url = "http://ip-api.com/json/"
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            data = json.loads(response.read())
        city = data.get("city")
        if city:
            return city
        else:
            print("Error: Geolocation API did not return a city name.")
            return None
    except urllib.error.URLError as e:
        print(f"Error: Could not reach geolocation service ({e.reason})")
        return None
    except (KeyError, json.JSONDecodeError) as e:
        print(f"Error: Invalid response from geolocation service ({e})")
        return None


def main():
    parser = argparse.ArgumentParser(
        description="Get current weather for a city using wttr.in"
    )
    parser.add_argument(
        "city",
        nargs="?",
        default=None,
        help=(
            "City name (optional, e.g., 'New York', 'London'). "
            "If not provided, location is auto-detected from IP"
        ),
    )
    parser.add_argument(
        "--auto",
        action="store_true",
        help=(
            "(Deprecated: auto-detection is now the default) "
            "Kept for backwards compatibility"
        ),
    )
    args = parser.parse_args()

    # Mutual exclusion: cannot provide both city and --auto
    # If --auto is provided with city, ignore --auto with a warning or error
    if args.city and args.auto:
        parser.error(
            "Cannot specify both city argument and --auto flag. Use one or the other."
        )

    # City resolution: explicit city overrides auto-detection
    if args.city:
        city = args.city.strip()
        if not city:
            print("Error: City name cannot be empty.")
            sys.exit(1)
    else:
        # No city provided → auto-detect from IP
        city = get_city_from_ip()
        if city is None:
            print(
                "Failed to detect location. Please provide a city name as an argument."
            )
            sys.exit(1)

    get_weather(city)


if __name__ == "__main__":
    main()
