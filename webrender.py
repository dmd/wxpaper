#!/usr/bin/env python3
"""Render the wxpaper panel as a single self-contained HTML document.

Used by web/index.py (CGI on 3e.org) and webversion.py (local dev). The page
is fully server-rendered with inlined CSS and base64 images, so a screenshot
device like trmnl needs exactly one request and no client-side JS -- nothing
can race the screenshot or fail to load.
"""
from pathlib import Path
import base64
import html

ICONS = {
    "clear-day": "sun.png",
    "clear-night": "moon.png",
    "rain": "rain.png",
    "snow": "snow.png",
    "sleet": "sleet.png",
    "hail": "hail.png",
    "thunderstorm": "storm.png",
    "wind": "windmill.png",
    "cloudy": "clouds.png",
    "partly-cloudy-day": "partly-cloudy-day.png",
    "partly-cloudy-night": "partly-cloudy-night.png",
    "fog": "fog.png",
}
DEFAULT_ICON = "clouds.png"


def format_temp(value) -> str:
    try:
        value = float(value)
    except (TypeError, ValueError):
        return "--"
    if value >= 100:
        return "HI"
    if value < 0:
        return "LO"
    return str(round(value))


def format_uv(value) -> str:
    try:
        value = float(value)
    except (TypeError, ValueError):
        return "--"
    if value > 9:
        return "X"
    return str(round(value))


def _data_uri(path: Path) -> str:
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def render_page(data: dict, asset_dir) -> str:
    """Return a complete HTML document for the given forecast data.

    asset_dir holds styles.css and imgs/ (the wxpaper web bundle); the CSS is
    inlined and the two visible images are embedded as data URIs.
    """
    asset_dir = Path(asset_dir)
    css = (asset_dir / "styles.css").read_text()
    icon_name = ICONS.get(data.get("condition"), DEFAULT_ICON)
    icon_uri = _data_uri(asset_dir / "imgs" / icon_name)
    uv_uri = _data_uri(asset_dir / "imgs" / "uv.png")
    esc = html.escape

    def text(key: str) -> str:
        return esc(str(data.get(key, "")))

    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>wxpaper</title>
    <style>{css}</style>
  </head>
  <body>
    <main class="panel" data-state="ready">
      <header class="updates">
        <span>Last update {text("lastUpdate")}</span>
      </header>

      <section class="temps">
        <div class="temp-now"><span>{format_temp(data.get("tempNow"))}</span></div>
        <div class="temp-range">
          <div class="temp-high"><span>{format_temp(data.get("tempHigh"))}</span></div>
          <div class="temp-low"><span>{format_temp(data.get("tempLow"))}</span></div>
        </div>
        <div class="uv"><img class="uv-icon" src="{uv_uri}" alt="UV index" /><span>{format_uv(data.get("uv"))}</span></div>
        <img class="condition-icon" src="{icon_uri}" alt="{text("condition")}" />
      </section>

      <section class="meta">
        <div class="date"><span>{text("weekday")}</span><span>{text("date")}</span></div>
      </section>

      <footer class="info">
        <p class="summary">{text("summary")}</p>
        <p class="allowance">{text("allowance")}</p>
      </footer>
    </main>
  </body>
</html>
"""
