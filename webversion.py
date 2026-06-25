#!/usr/bin/env python3
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.request import urlopen
from urllib.error import URLError
from datetime import date, datetime, timedelta
from typing import Optional
import json
import os
import re

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
    allowance_value = build_allowance(now.date())

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
        "allowance": allowance_value,
    }


def event_countdown(today: date, event_date_str: Optional[str], label: Optional[str]) -> Optional[str]:
    if not event_date_str:
        return None
    try:
        event_date = date.fromisoformat(event_date_str)
    except ValueError:
        return None
    days = (event_date - today).days
    if days < 0:
        return None
    base = f"{days} days"
    if label:
        return f"{base} until {label}"
    return base


def compose_allowance(allowance_text: str, countdown: Optional[str]) -> str:
    if countdown:
        return f"{allowance_text}, {countdown}"
    return allowance_text


def round_dollars(text: str) -> str:
    return re.sub(
        r"\$(\d+(?:\.\d+)?)", lambda m: f"${round(float(m.group(1)))}", text
    )


def build_allowance(today: date) -> str:
    countdown = event_countdown(
        today, os.getenv("WX_EVENT_DATE"), os.getenv("WX_EVENT_LABEL")
    )
    return compose_allowance(round_dollars(allowance()), countdown)


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
    allowance_value = build_allowance(now.date())
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
        "allowance": allowance_value,
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
