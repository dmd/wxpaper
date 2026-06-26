#!/usr/bin/env python3
"""Weather + allowance data for the wxpaper display.

Shared by webversion.py (local dev server) and web/forecast.py (CGI on 3e.org).
Standard library only, so it runs unchanged under DreamHost's system python.
"""
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
    event_date, event_label = event_config()
    countdown = event_countdown(today, event_date, event_label)
    return compose_allowance(round_dollars(allowance()), countdown)


def event_config() -> "tuple[Optional[str], Optional[str]]":
    """Return (EVENT_DATE, EVENT_LABEL).

    Environment wins (local dev, docker). On the CGI deployment Apache's SetEnv
    does not reach CGI scripts, so we fall back to a ``wxpaper-event`` file of
    ``KEY=VALUE`` lines (checked in the home dir, then beside this module).
    """
    date_str = os.getenv("EVENT_DATE")
    label = os.getenv("EVENT_LABEL")
    if date_str:
        return date_str, label

    for candidate in (Path.home() / "wxpaper-event", ROOT / "wxpaper-event"):
        if not candidate.exists():
            continue
        try:
            values = {}
            for line in candidate.read_text().splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, value = line.partition("=")
                values[key.strip()] = value.strip()
            return values.get("EVENT_DATE"), values.get("EVENT_LABEL")
        except OSError:
            pass
    return None, None


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


def read_secret() -> str:
    value = os.getenv("PIRATE_SECRET")
    if value:
        return value.strip()
    candidates = (
        os.getenv("PIRATE_SECRET_FILE"),
        Path.home() / "pirate-secret",
        ROOT / "pirate-secret",
    )
    for candidate in candidates:
        if not candidate:
            continue
        path = Path(candidate)
        if path.exists():
            try:
                return path.read_text().strip()
            except OSError:
                pass
    return ""
