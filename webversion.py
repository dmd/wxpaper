#!/usr/bin/env python3
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.request import urlopen
from urllib.error import URLError
from datetime import datetime, timedelta
import json
import os

ROOT = Path(__file__).resolve().parent
SECONDS_BETWEEN_UPDATES = 4 * 60 * 60
ALLOWANCE_URL = "https://3e.org/private/allowance-capy-retrieve.py"


class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/api/forecast":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(fetch_forecast()).encode("utf-8"))
            return
        if self.path == "/":
            self.path = "/web/index.html"
        return super().do_GET()


def fetch_forecast() -> dict:
    api_key = read_secret()
    lat = os.getenv("WX_LAT", "42.417821")
    lon = os.getenv("WX_LON", "-71.177747")
    units = os.getenv("WX_UNITS", "us")

    if not api_key:
        return fallback_data("Missing PIRATE_SECRET")

    url = (
        "https://api.pirateweather.net/forecast/"
        f"{api_key}/{lat},{lon}?exclude=minutely,alerts&units={units}"
    )

    try:
        with urlopen(url, timeout=10) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except URLError as exc:
        return fallback_data(f"Fetch failed: {exc}")

    currently = payload.get("currently", {})
    daily = payload.get("daily", {}).get("data", [{}])
    today = daily[0] if daily else {}

    now = datetime.now()
    next_update = now + timedelta(seconds=SECONDS_BETWEEN_UPDATES)
    allowance_text = allowance()
    days_until = days_until_special_event(now)

    return {
        "tempNow": currently.get("temperature", 0),
        "tempHigh": today.get("temperatureHigh", 0),
        "tempLow": today.get("temperatureLow", 0),
        "uv": today.get("uvIndex", 0),
        "condition": today.get("icon", "cloudy"),
        "summary": today.get("summary", ""),
        "lastUpdate": now.strftime("%H:%M"),
        "nextUpdate": next_update.strftime("%H:%M"),
        "weekday": now.strftime("%a"),
        "date": now.strftime("%b %-d"),
        "allowance": f"{allowance_text}, {days_until} days",
    }


def days_until_special_event(now: datetime) -> int:
    target_date = datetime(2024, 6, 20)
    return (target_date - now).days


def allowance() -> str:
    override = os.getenv("WX_ALLOWANCE")
    if override:
        return override
    try:
        with urlopen(ALLOWANCE_URL, timeout=5) as response:
            return response.read().decode("utf-8").strip()
    except URLError:
        return "Allowance unavailable"


def fallback_data(reason: str) -> dict:
    now = datetime.now()
    next_update = now + timedelta(seconds=SECONDS_BETWEEN_UPDATES)
    allowance_text = allowance()
    days_until = days_until_special_event(now)
    return {
        "tempNow": 0,
        "tempHigh": 0,
        "tempLow": 0,
        "uv": 0,
        "condition": "partly-cloudy-day",
        "summary": reason,
        "lastUpdate": now.strftime("%H:%M"),
        "nextUpdate": next_update.strftime("%H:%M"),
        "weekday": now.strftime("%a"),
        "date": now.strftime("%b %-d"),
        "allowance": f"{allowance_text}, {days_until} days",
    }


def main() -> None:
    handler = partial(Handler, directory=str(ROOT))
    server = ThreadingHTTPServer(("", 8000), handler)
    print("Serving on http://localhost:8000")
    server.serve_forever()


def read_secret() -> str:
    secret_path = ROOT / "pirate-secret"
    try:
        return secret_path.read_text().strip()
    except OSError:
        return ""


if __name__ == "__main__":
    main()
