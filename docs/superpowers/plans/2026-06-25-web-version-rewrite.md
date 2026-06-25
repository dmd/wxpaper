# wxpaper Web Version Rewrite Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rewrite the browser "web version" of the wxpaper display with clean, responsive, semantic HTML/CSS — no bitmapped fonts, crisp PNG weather icons — while keeping the e-ink look and the existing `/api/forecast` JSON contract.

**Architecture:** Backend stays a Python stdlib HTTP server (`webversion.py`) serving static files plus a `/api/forecast` JSON endpoint; only the special-event countdown becomes env-configurable. Frontend is rewritten as three small files — semantic `index.html`, a CSS-variable/Grid stylesheet using `clamp()` typography, and a minimal `app.js` that fetches the JSON and fills text nodes. Weather icons become PNGs downloaded from iconsdb.

**Tech Stack:** Python 3 standard library (http.server, `unittest`); plain HTML/CSS/JavaScript (no framework, no build step); iconsdb black weather PNGs.

## Global Constraints

- Run Python with `python3`. Backend and tests use only the standard library — no new dependencies.
- Keep the `/api/forecast` JSON field names exactly as they are today (`tempNow`, `tempHigh`, `tempLow`, `uv`, `condition`, `summary`, `lastUpdate`, `nextUpdate`, `weekday`, `date`, `allowance`).
- Aesthetic: clean e-ink — black ink on white paper, high contrast, heavy bold numerals. No color accents.
- Typography: bold **system font stack** only. No downloaded/self-hosted font files.
- The current temperature is the dominant element; high/low render at ~half its size, stacked immediately to its right (high on top).
- No bitmapped fonts/digits. Old digit BMPs (`imgs/165_*`, `200_*`, `300_*`) are left in place, unused.
- Temp display rules: `>= 100` → `"HI"`, `< 0` → `"LO"`. UV `> 9` → `"X"`. Unknown `condition` → cloud icon.

---

### Task 1: Backend — env-configurable event countdown

Replace the hardcoded `datetime(2024, 6, 20)` special-event date with two pure, tested helpers driven by env vars, and wire them into the JSON builders.

**Files:**
- Modify: `webversion.py` (imports near line 7; replace `days_until_special_event` at lines 73-75; update `fetch_forecast` lines 55-56,69 and `fallback_data` lines 92-93,105)
- Test: `test_webversion.py` (create)

**Interfaces:**
- Produces:
  - `event_countdown(today: datetime.date, event_date_str: Optional[str], label: Optional[str]) -> Optional[str]` — returns `"N days"`, or `"N days until <label>"` when label given; returns `None` when the date is unset, invalid, or in the past.
  - `compose_allowance(allowance_text: str, countdown: Optional[str]) -> str` — returns `"{allowance_text}, {countdown}"` when countdown is truthy, else just `allowance_text`.
  - `build_allowance(today: datetime.date) -> str` — reads `WX_EVENT_DATE`/`WX_EVENT_LABEL` from env, calls `allowance()` (network), and composes the final string. Not unit-tested (does I/O); the two helpers above carry the logic.

- [ ] **Step 1: Write the failing tests**

Create `test_webversion.py`:

```python
import unittest
from datetime import date

import webversion


class EventCountdownTests(unittest.TestCase):
    def test_future_date_no_label(self):
        self.assertEqual(
            webversion.event_countdown(date(2026, 6, 25), "2026-07-05", None),
            "10 days",
        )

    def test_future_date_with_label(self):
        self.assertEqual(
            webversion.event_countdown(date(2026, 6, 25), "2026-07-05", "vacation"),
            "10 days until vacation",
        )

    def test_today_is_zero_days(self):
        self.assertEqual(
            webversion.event_countdown(date(2026, 6, 25), "2026-06-25", None),
            "0 days",
        )

    def test_past_date_returns_none(self):
        self.assertIsNone(
            webversion.event_countdown(date(2026, 6, 25), "2024-06-20", None)
        )

    def test_unset_returns_none(self):
        self.assertIsNone(webversion.event_countdown(date(2026, 6, 25), None, None))
        self.assertIsNone(webversion.event_countdown(date(2026, 6, 25), "", None))

    def test_invalid_returns_none(self):
        self.assertIsNone(
            webversion.event_countdown(date(2026, 6, 25), "not-a-date", None)
        )


class ComposeAllowanceTests(unittest.TestCase):
    def test_with_countdown(self):
        self.assertEqual(
            webversion.compose_allowance("$469.93", "10 days"),
            "$469.93, 10 days",
        )

    def test_without_countdown(self):
        self.assertEqual(webversion.compose_allowance("$469.93", None), "$469.93")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m unittest test_webversion -v`
Expected: FAIL — `AttributeError: module 'webversion' has no attribute 'event_countdown'`.

- [ ] **Step 3: Add the `date` and `Optional` imports**

In `webversion.py`, change the datetime import (line 7) from:

```python
from datetime import datetime, timedelta
```

to:

```python
from datetime import date, datetime, timedelta
from typing import Optional
```

(`Optional` keeps the annotations valid on Python 3.9, which this project still targets — `str | None` syntax would raise at import time there.)

- [ ] **Step 4: Replace `days_until_special_event` with the new helpers**

Delete the existing function (lines 73-75):

```python
def days_until_special_event(now: datetime) -> int:
    target_date = datetime(2024, 6, 20)
    return (target_date - now).days
```

and replace it with:

```python
def event_countdown(today: date, event_date_str, label) -> Optional[str]:
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


def compose_allowance(allowance_text: str, countdown) -> str:
    if countdown:
        return f"{allowance_text}, {countdown}"
    return allowance_text


def build_allowance(today: date) -> str:
    countdown = event_countdown(
        today, os.getenv("WX_EVENT_DATE"), os.getenv("WX_EVENT_LABEL")
    )
    return compose_allowance(allowance(), countdown)
```

- [ ] **Step 5: Wire `build_allowance` into `fetch_forecast`**

In `fetch_forecast`, replace these lines (currently 55-56):

```python
    allowance_text = allowance()
    days_until = days_until_special_event(now)
```

with:

```python
    allowance_value = build_allowance(now.date())
```

Then in the returned dict, change the allowance line (currently line 69) from:

```python
        "allowance": f"{allowance_text}, {days_until} days",
```

to:

```python
        "allowance": allowance_value,
```

- [ ] **Step 6: Wire `build_allowance` into `fallback_data`**

In `fallback_data`, replace these lines (currently 92-93):

```python
    allowance_text = allowance()
    days_until = days_until_special_event(now)
```

with:

```python
    allowance_value = build_allowance(now.date())
```

Then in the returned dict, change the allowance line (currently line 105) from:

```python
        "allowance": f"{allowance_text}, {days_until} days",
```

to:

```python
        "allowance": allowance_value,
```

- [ ] **Step 7: Run tests to verify they pass**

Run: `python3 -m unittest test_webversion -v`
Expected: PASS — 8 tests OK.

- [ ] **Step 8: Commit**

```bash
git add webversion.py test_webversion.py
git commit -m "Make special-event countdown env-configurable, add tests"
```

---

### Task 2: Download iconsdb PNG weather icons

Fetch the black weather PNGs (512px) from iconsdb into `imgs/` under condition-friendly filenames. (User has authorized this download.)

**Files:**
- Create: `imgs/sun.png`, `imgs/moon.png`, `imgs/cloud.png`, `imgs/clouds.png`, `imgs/rain.png`, `imgs/snow.png`, `imgs/sleet.png`, `imgs/hail.png`, `imgs/storm.png`, `imgs/windmill.png`, `imgs/uv.png`

**Interfaces:**
- Produces: PNG files in `imgs/` consumed by Task 3's `app.js` icon map. Filename ↔ Pirate Weather `condition` mapping:
  - `clear-day` → `sun.png`, `clear-night` → `moon.png`
  - `cloudy` → `clouds.png`; `partly-cloudy-day`/`partly-cloudy-night`/`fog` → `cloud.png`
  - `rain` → `rain.png`, `snow` → `snow.png`, `sleet` → `sleet.png`, `hail` → `hail.png`
  - `thunderstorm` → `storm.png`, `wind` → `windmill.png`
  - UV indicator → `uv.png` (sunglasses)
  - default/unknown → `cloud.png`

- [ ] **Step 1: Download the icons**

Run:

```bash
/bin/bash -c '
set -e
cd imgs
for pair in "sun:sun" "moon:moon" "cloud:cloud" "clouds:clouds" "rain:rain" "snow:snow" "sleet:sleet" "hail:hail" "storm:storm" "windmill:windmill" "sunglasses:uv"; do
  slug="${pair%%:*}"; out="${pair##*:}"
  curl -fsS -A "Mozilla/5.0" -o "$out.png" "https://www.iconsdb.com/icons/download/black/$slug-512.png"
done
'
```

- [ ] **Step 2: Verify the downloads are valid PNGs**

Run:

```bash
/bin/bash -c 'cd imgs && file sun.png moon.png cloud.png clouds.png rain.png snow.png sleet.png hail.png storm.png windmill.png uv.png'
```

Expected: every line reports `PNG image data, 512 x 512, ...`. If any file reports HTML/empty, the slug failed — re-probe that icon's slug on iconsdb and re-download.

- [ ] **Step 3: Commit**

```bash
git add imgs/sun.png imgs/moon.png imgs/cloud.png imgs/clouds.png imgs/rain.png imgs/snow.png imgs/sleet.png imgs/hail.png imgs/storm.png imgs/windmill.png imgs/uv.png
git commit -m "Add iconsdb PNG weather icons for web version"
```

---

### Task 3: Rewrite the frontend (HTML, CSS, JS)

Replace the three `web/` files with clean, semantic, responsive versions. This is a single deliverable — the three files are tightly coupled and only meaningful together. Verification is in-browser (the repo has no JS toolchain; introducing one is out of scope).

**Files:**
- Modify (full rewrite): `web/index.html`, `web/styles.css`, `web/app.js`

**Interfaces:**
- Consumes: `/api/forecast` JSON (Task 1 backend); PNG icons in `imgs/` (Task 2).

- [ ] **Step 1: Rewrite `web/index.html`**

Replace the entire contents of `web/index.html` with:

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>wxpaper</title>
    <link rel="stylesheet" href="/web/styles.css" />
  </head>
  <body>
    <main class="panel" id="panel" data-state="loading">
      <header class="updates">
        <span id="last-update">Last update --:--</span>
        <span id="next-update">Next update --:--</span>
      </header>

      <section class="temps">
        <div class="temp-now"><span id="temp-now">--</span><span class="deg">&deg;</span></div>
        <div class="temp-range">
          <div class="temp-high"><span id="temp-high">--</span><span class="deg">&deg;</span></div>
          <div class="temp-low"><span id="temp-low">--</span><span class="deg">&deg;</span></div>
        </div>
        <img class="condition-icon" id="condition-icon" alt="" />
      </section>

      <section class="meta">
        <div class="uv"><img class="uv-icon" src="/imgs/uv.png" alt="UV index" /><span id="uv">--</span></div>
        <div class="date"><span id="weekday">---</span><span class="date-sep">&middot;</span><span id="date">--- --</span></div>
      </section>

      <footer class="info">
        <p class="summary" id="summary">&mdash;</p>
        <p class="allowance" id="allowance">&mdash;</p>
      </footer>
    </main>
    <script src="/web/app.js"></script>
  </body>
</html>
```

- [ ] **Step 2: Rewrite `web/styles.css`**

Replace the entire contents of `web/styles.css` with:

```css
:root {
  color-scheme: only light;
  --ink: #111;
  --paper: #fff;
  --muted: #555;
  --rule: #ddd;
  --temp-now-size: clamp(6rem, 26vw, 16rem);
  --temp-range-size: clamp(3rem, 13vw, 8rem);
  --icon-size: clamp(4rem, 16vw, 9rem);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica,
    Arial, sans-serif;
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

html,
body {
  height: 100%;
}

body {
  background: var(--paper);
  color: var(--ink);
  display: flex;
  justify-content: center;
  align-items: center;
  padding: clamp(0.75rem, 3vw, 2rem);
}

.panel {
  width: min(100%, 60rem);
  border: 1px solid var(--rule);
  border-radius: 0.5rem;
  padding: clamp(1rem, 4vw, 2.5rem);
  display: grid;
  gap: clamp(0.75rem, 3vw, 1.75rem);
}

.updates {
  display: flex;
  justify-content: space-between;
  font-size: clamp(0.75rem, 2.2vw, 1rem);
  color: var(--muted);
  letter-spacing: 0.02em;
}

.temps {
  display: flex;
  align-items: center;
  gap: clamp(0.5rem, 3vw, 2rem);
}

.temp-now {
  display: flex;
  align-items: flex-start;
  font-size: var(--temp-now-size);
  font-weight: 800;
  line-height: 0.85;
}

.temp-now .deg {
  font-size: 0.4em;
  font-weight: 700;
}

.temp-range {
  display: flex;
  flex-direction: column;
  gap: 0.1em;
  font-size: var(--temp-range-size);
  font-weight: 700;
  line-height: 1;
}

.temp-range .deg {
  font-size: 0.45em;
}

.temp-high,
.temp-low {
  display: flex;
  align-items: flex-start;
}

.temp-low {
  color: var(--muted);
}

.condition-icon {
  margin-left: auto;
  width: var(--icon-size);
  height: var(--icon-size);
  object-fit: contain;
}

.meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: clamp(1rem, 4vw, 2rem);
  font-weight: 600;
}

.uv {
  display: flex;
  align-items: center;
  gap: 0.4em;
}

.uv-icon {
  height: 1em;
  width: auto;
}

.date {
  display: flex;
  align-items: baseline;
  gap: 0.4em;
}

.date-sep {
  color: var(--muted);
}

.info {
  display: grid;
  gap: 0.35rem;
}

.summary {
  font-size: clamp(0.95rem, 3vw, 1.4rem);
}

.allowance {
  font-size: clamp(0.85rem, 2.5vw, 1.2rem);
  color: var(--muted);
}

.panel[data-state="loading"] {
  opacity: 0;
}

.panel[data-state="ready"],
.panel[data-state="offline"] {
  opacity: 1;
  transition: opacity 0.2s ease;
}
```

- [ ] **Step 3: Rewrite `web/app.js`**

Replace the entire contents of `web/app.js` with:

```javascript
const ICONS = {
  "clear-day": "sun.png",
  "clear-night": "moon.png",
  rain: "rain.png",
  snow: "snow.png",
  sleet: "sleet.png",
  hail: "hail.png",
  thunderstorm: "storm.png",
  wind: "windmill.png",
  cloudy: "clouds.png",
  "partly-cloudy-day": "cloud.png",
  "partly-cloudy-night": "cloud.png",
  fog: "cloud.png",
};
const DEFAULT_ICON = "cloud.png";

const OFFLINE_DATA = {
  tempNow: 0,
  tempHigh: 0,
  tempLow: 0,
  uv: 0,
  condition: "cloudy",
  summary: "",
  allowance: "—",
  weekday: "---",
  date: "--- --",
  lastUpdate: "--:--",
  nextUpdate: "--:--",
};

function formatTemp(value) {
  if (value >= 100) return "HI";
  if (value < 0) return "LO";
  return String(Math.round(value));
}

function formatUv(value) {
  if (value > 9) return "X";
  return String(Math.round(value));
}

function iconFor(condition) {
  return ICONS[condition] || DEFAULT_ICON;
}

function setText(id, text) {
  document.getElementById(id).textContent = text;
}

function render(data) {
  setText("temp-now", formatTemp(data.tempNow));
  setText("temp-high", formatTemp(data.tempHigh));
  setText("temp-low", formatTemp(data.tempLow));
  setText("uv", formatUv(data.uv));
  setText("weekday", data.weekday);
  setText("date", data.date);
  setText("summary", data.summary);
  setText("allowance", data.allowance);
  setText("last-update", `Last update ${data.lastUpdate}`);
  setText("next-update", `Next update ${data.nextUpdate}`);

  const icon = document.getElementById("condition-icon");
  icon.src = `/imgs/${iconFor(data.condition)}`;
  icon.alt = data.condition || "";
}

async function load() {
  const panel = document.getElementById("panel");
  try {
    const res = await fetch("/api/forecast");
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    render(await res.json());
    panel.dataset.state = "ready";
  } catch (err) {
    render({ ...OFFLINE_DATA, summary: `Offline: ${err.message}` });
    panel.dataset.state = "offline";
  }
}

load();
```

- [ ] **Step 4: Verify in the browser**

Run the server: `python3 webversion.py` (serves on http://localhost:8000).
Load `http://localhost:8000/` and confirm:
- Current temperature is the large dominant element; high (top) and low (below) sit immediately to its right at roughly half size.
- The condition icon (a crisp PNG, not pixelated) shows to the right; UV row shows the sunglasses PNG + number.
- Weekday/date, summary, and allowance all render; nothing is clipped.
- Resize the window narrow → wide: the temperature scales via `clamp()`, and no element overflows or clips (this fixes the old summary-clipping bug).

- [ ] **Step 5: Commit**

```bash
git add web/index.html web/styles.css web/app.js
git commit -m "Rewrite web frontend: semantic responsive layout, no bitmap fonts"
```

---

### Task 4: End-to-end verification & event-date check

Confirm the full stack works together and the new env-configurable countdown behaves per spec.

**Files:** none (verification only)

- [ ] **Step 1: Verify live forecast end to end**

Start the server (`python3 webversion.py`), then in another shell:

Run: `curl -s http://localhost:8000/api/forecast`
Expected: JSON with all fields populated; `allowance` is just the dollar amount with **no** ", N days" suffix (since `WX_EVENT_DATE` is unset).

- [ ] **Step 2: Verify the countdown appears when configured**

Stop the server, then start it with an event date set:

Run: `WX_EVENT_DATE=2026-12-25 WX_EVENT_LABEL=holiday python3 webversion.py`
In another shell: `curl -s http://localhost:8000/api/forecast`
Expected: `allowance` ends with `, N days until holiday` (N > 0).

- [ ] **Step 3: Verify icon mapping breadth**

In the browser at `http://localhost:8000/`, confirm the rendered icon matches the live `condition` from the `/api/forecast` JSON, and that it is a smooth (non-pixelated) PNG.

- [ ] **Step 4: Stop the server**

Stop the background/foreground `python3 webversion.py` process.

---

## Notes for the implementer

- The `/api/forecast` payload is always complete (both `fetch_forecast` and `fallback_data` return every field), so `render()` never needs to merge in defaults — the offline branch supplies its own full object.
- Do not touch the physical-device path (`wxpaper.py`, `pushmeplease.py`, Particle/Dockerfile). Out of scope.
- The `docker-compose.yml` port mismatch (publishes 33223; server binds 8000) is a known pre-existing issue, out of scope for this plan.
