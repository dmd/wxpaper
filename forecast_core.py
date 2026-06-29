#!/usr/bin/env python3
"""Weather + allowance data for the wxpaper display.

Shared by webversion.py (local dev server) and web/forecast.py (CGI on 3e.org).
Standard library only, so it runs unchanged under DreamHost's system python.
"""
from pathlib import Path
from urllib.request import urlopen
from urllib.error import URLError
from datetime import date, datetime
from typing import Optional
from zoneinfo import ZoneInfo
import json
import os
import re

ROOT = Path(__file__).resolve().parent
ALLOWANCE_URL = "https://3e.org/private/allowance-capy-retrieve.py"
TZ = ZoneInfo("America/New_York")


def format_time(when: datetime) -> str:
    """12-hour am/pm time, e.g. '3:05 pm', with no leading zero on the hour."""
    return when.strftime("%I:%M %p").lstrip("0").lower()


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

    now = datetime.now(TZ)
    allowance_value = build_allowance(now.date())

    return {
        "tempNow": currently.get("temperature", 0),
        "tempHigh": today.get("temperatureHigh", 0),
        "tempLow": today.get("temperatureLow", 0),
        "uv": today.get("uvIndex", 0),
        "condition": today.get("icon", "cloudy"),
        "summary": today.get("summary", ""),
        "lastUpdate": format_time(now),
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

    today = datetime.now(TZ).date().isoformat()
    cached_date, cached_value = _read_allowance_cache()
    if cached_value is not None and cached_date == today:
        return cached_value

    try:
        with urlopen(ALLOWANCE_URL, timeout=5) as response:
            value = response.read().decode("utf-8").strip()
    except URLError:
        # Network failed: keep showing the last known value if we have one.
        return cached_value if cached_value is not None else "Allowance unavailable"

    _write_allowance_cache(today, value)
    return value


def _allowance_cache_path() -> Path:
    override = os.getenv("WX_ALLOWANCE_CACHE")
    if override:
        return Path(override)
    return Path.home() / ".wxpaper-allowance-cache"


def _read_allowance_cache() -> "tuple[Optional[str], Optional[str]]":
    try:
        obj = json.loads(_allowance_cache_path().read_text())
        return obj.get("date"), obj.get("allowance")
    except (OSError, ValueError):
        return None, None


def _write_allowance_cache(today: str, value: str) -> None:
    path = _allowance_cache_path()
    tmp = path.with_name(path.name + ".tmp")
    try:
        tmp.write_text(json.dumps({"date": today, "allowance": value}))
        tmp.replace(path)  # atomic on POSIX
    except OSError:
        pass


def fallback_data(reason: str) -> dict:
    now = datetime.now(TZ)
    allowance_value = build_allowance(now.date())
    return {
        "tempNow": 0,
        "tempHigh": 0,
        "tempLow": 0,
        "uv": 0,
        "condition": "partly-cloudy-day",
        "summary": reason,
        "lastUpdate": format_time(now),
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
