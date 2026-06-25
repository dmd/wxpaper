# wxpaper web version rewrite — design

**Date:** 2026-06-25
**Status:** Approved (pending spec review)

## Goal

Rewrite the browser-based "web version" of the wxpaper weather display so the
frontend is clean, semantic, and easily maintainable. Replace the bitmapped
fonts (per-digit `.BMP` images) with real web text, and replace the pixelated
weather `.BMP` icons with crisp PNGs sourced from iconsdb (the original icon
source).

Pixel-for-pixel fidelity with the physical e-ink device is **not** a goal. The
look should stay in the e-ink spirit — black on white, high contrast, big bold
numerals — but be a proper responsive web page.

## Priorities

The single most important UI element is the **current temperature**: very large
and unmistakable. The day's **high and low** sit immediately to its right at
roughly half the size (high on top, low below).

## Decisions (locked during brainstorming)

- **Aesthetic:** Clean e-ink style — black text on white, high contrast, heavy
  bold numerals. Not a colorful dashboard.
- **Layout approach:** Responsive semantic layout (CSS Grid/Flex + `clamp()`
  typography). No absolute pixel positioning, no per-digit image swapping.
- **Font:** Bold system font stack. No downloaded/self-hosted font asset.
- **Icons:** PNGs downloaded from iconsdb black weather icon set
  (`https://www.iconsdb.com/icons/download/black/<name>-512.png`) into `imgs/`.
- **Allowance / countdown line:** Keep the feature, but make the special-event
  date configurable via env var instead of a hardcoded past date.
- **Old bitmap assets:** Leave the unused digit/text BMPs (`165_*`, `200_*`,
  `300_*`) in place; they're harmless and the README references the device.

## Architecture

Two pieces, same split as today:

1. **Backend — `webversion.py`** (Python stdlib HTTP server)
   - Serves static files from the repo root and `web/`.
   - `GET /api/forecast` returns the JSON the frontend renders.
   - The JSON contract is unchanged except as noted below, so the frontend and
     backend stay loosely coupled.

2. **Frontend — `web/index.html`, `web/styles.css`, `web/app.js`**
   - `index.html`: semantic markup, one element per datum. No per-digit
     elements, no `paper-noise`/`date-box` scaffolding.
   - `styles.css`: full rewrite. CSS custom properties for the e-ink palette and
     a type scale; Grid/Flex layout; responsive `clamp()` typography so the
     current temperature stays huge but never overflows on small screens.
   - `app.js`: fetch `/api/forecast`, populate text nodes, set the icon `src`
     from a small `condition → filename` map, and show a graceful "offline"
     state on fetch failure. Substantially smaller than the current
     positioning-heavy script.

## Layout

Centered card, black-on-white. Temperature dominates the top.

```
┌─────────────────────────────────────────────┐
│  Last update 14:54          Next update 18:54 │
│                                               │
│       ┌──────┐   70°  ← high (half size)      │
│       │  66° │   62°  ← low                    │
│       └──────┘                  ☁  ← icon      │
│                                               │
│   UV 4        Tue · Jun 23                     │
│                                               │
│   Misty in the morning, light rain later.     │
│   $469.93 · 12 days until <event>             │
└─────────────────────────────────────────────┘
```

- **Current temp:** dominant focal point, `clamp()`-sized.
- **High / low:** stacked immediately right of current temp at ~half size, high
  on top.
- **Condition icon:** iconsdb PNG, right of the temperatures.
- **UV, date, summary, allowance:** smaller supporting rows beneath.

## Data contract (`/api/forecast`)

Unchanged fields consumed by the frontend:

| Field        | Meaning                                  |
|--------------|------------------------------------------|
| `tempNow`    | current temperature                      |
| `tempHigh`   | today's high                             |
| `tempLow`    | today's low                              |
| `uv`         | UV index                                 |
| `condition`  | Pirate Weather icon string               |
| `summary`    | text summary                             |
| `lastUpdate` | "HH:MM"                                  |
| `nextUpdate` | "HH:MM"                                  |
| `weekday`    | e.g. "Tue"                               |
| `date`       | e.g. "Jun 23"                            |
| `allowance`  | display string, e.g. "$469.93, 12 days"  |

Rendering rules carried over from the old frontend:
- Temperatures display as whole numbers. Out-of-range guards: `>= 100` → "HI",
  `< 0` → "LO" (now rendered as text, not a bitmap).
- UV `> 9` → "X".
- Unknown `condition` → default to a cloud icon.

## Icons

- Source: iconsdb black weather icons, 512px PNGs.
- Download mechanism verified: `GET
  https://www.iconsdb.com/icons/download/black/<name>-512.png` returns 200 for
  the needed icons (sun, cloud, clouds, moon, rain, snow, snowflake, sleet,
  hail, storm, sunglasses, thermometer, …).
- Saved into `imgs/` named by condition, e.g. `clear-day.png`, `clear-night.png`,
  `cloudy.png`, `partly-cloudy-day.png`, `partly-cloudy-night.png`, `rain.png`,
  `snow.png`, `sleet.png`, `hail.png`, `wind.png`, `fog.png`, plus `uv.png`
  (sunglasses).
- Condition → filename mapping covers all Pirate Weather `icon` values:
  `clear-day`, `clear-night`, `rain`, `snow`, `sleet`, `wind`, `fog`, `cloudy`,
  `partly-cloudy-day`, `partly-cloudy-night`, and also `hail`/`thunderstorm` if
  returned. Fallback for any unrecognized value → cloud icon.
- For conditions iconsdb lacks a dedicated slug for (e.g. wind, fog,
  partly-cloudy), pick the closest available icon at implementation time by
  probing alternate slugs; document the final chosen mapping in code.

## Backend changes (`webversion.py`)

Minimal:

- Replace the hardcoded `datetime(2024, 6, 20)` in
  `days_until_special_event()` with a value read from env:
  - `WX_EVENT_DATE` — ISO date (`YYYY-MM-DD`). **If unset or invalid, omit the
    countdown entirely** — the `allowance` field becomes just the allowance text
    (e.g. `"$469.93"`) with no ", N days" suffix. No stale default date.
  - `WX_EVENT_LABEL` — optional text appended to the countdown, e.g.
    `"12 days until vacation"`. If unset, the countdown reads `"12 days"` (current
    phrasing).
- The `allowance` field in the JSON keeps the same shape (a single display
  string) so the frontend needs no special handling.

## Error handling

- Frontend: on fetch failure or non-OK response, render the last known layout
  with an "Offline" summary message (as the current frontend does).
- Backend: existing `fallback_data()` behavior is retained — missing key or
  upstream failure returns a complete JSON payload with zeros and the reason in
  `summary`.

## Testing / verification

- Run `python3 webversion.py` and load `http://localhost:8000/` in a browser.
- Verify with live data that the current temperature is the dominant element and
  high/low render at ~half size to its right.
- Verify icon mapping for several conditions (manually exercise via the
  `condition` value, e.g. with `WX_*` overrides or sample data).
- Verify responsive behavior by resizing the window (temp scales, nothing
  overflows or clips — fixing the summary-clipping bug present in the old
  fixed-size layout).
- Verify the configurable event date: set `WX_EVENT_DATE` and confirm the
  countdown updates.

## Out of scope

- Changes to the physical-device path (`wxpaper.py`, `pushmeplease.py`,
  Particle/Dockerfile flow).
- The pre-existing `docker-compose.yml` port mismatch (publishes 33223; server
  binds 8000) and the lack of a Dockerfile for the web version — noted but not
  part of this rewrite unless requested.
- Removing the now-unused bitmap digit assets.
