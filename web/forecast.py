#!/usr/bin/python3
"""CGI endpoint: emits the wxpaper forecast JSON.

Deployed to ~/3e.org/wxpaper/forecast.py on 3e.org (DreamHost). The shared data
logic lives in forecast_core.py in the home directory (above the web root, so it
is never served), and pirate-secret sits in the home directory too.
"""
import json
import os
import sys

sys.path.insert(0, os.environ.get("HOME", "/home/edges"))

import forecast_core  # noqa: E402

body = json.dumps(forecast_core.fetch_forecast())
print("Content-Type: application/json")
# trmnl fetches this from a null-origin (blank base) context, so allow CORS.
print("Access-Control-Allow-Origin: *")
print()
print(body)
