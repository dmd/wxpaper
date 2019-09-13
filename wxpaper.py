#!/usr/bin/env python3

from darksky.api import DarkSky, DarkSkyAsync
from darksky.types import languages, units, weather
from sh import particle
from datetime import datetime

particle_id = "3eink"
API_KEY = open("darksky-secret").readline().rstrip()
darksky = DarkSky(API_KEY)
lat, lon = 42.417821, -71.177747

forecast = darksky.get_forecast(lat, lon, exclude=[weather.MINUTELY, weather.ALERTS])

now = forecast.currently
today = forecast.daily.data[0]


def clamp(n, minn, maxn):
    return max(min(maxn, n), minn)


def two_dig(n, HILO=True):
    if HILO:
        if n >= 100:
            return "HI"
        if n < 0:
            return "LO"
    return "{:02d}".format(int(clamp(n, 0, 99)))


def uv_one_dig(n):
    if n > 9:
        return "X"
    return "{:01d}".format(int(n))


iconmap = {
    "clear-day": "SUN",
    "clear-night": "NIGHT",
    "cloudy": "CLOUD",
    "partly-cloudy-day": "CLDAY",
    "partly-cloudly-night": "CLDNT",
}


def icon(iconsize, condition):
    return f"{iconsize}" + iconmap.get(condition, condition.upper()) + ".BMP"


def paper_image(bitmap, x, y):
    particle("function", "call", particle_id, "img", "|".join((bitmap, str(x), str(y))))


def paper_bignum(n, x, y):
    paper_image(f"300_{n}.BMP", x, y)


def paper_smallnum(n, x, y):
    paper_image(f"165_{n}.BMP", x, y)


def paper_text(text, x, y):
    particle("function", "call", particle_id, "text", "|".join((text, str(x), str(y))))


def paper_clear():
    particle("function", "call", particle_id, "clear")


def paper_update():
    particle("function", "call", particle_id, "update")


paper_clear()
temp_now = two_dig(now.apparent_temperature)
paper_bignum(temp_now[0], 20, 20)
paper_bignum(temp_now[1], 160, 20)

temp_hi = two_dig(today.apparent_temperature_high)
paper_smallnum(temp_hi[0], 310, 10)
paper_smallnum(temp_hi[1], 390, 10)

temp_low = two_dig(today.apparent_temperature_low)
paper_smallnum(temp_low[0], 310, 175)
paper_smallnum(temp_low[1], 390, 175)

paper_image(icon(3, now.icon), 500, 30)

paper_image(icon(3, today.icon), 500, 290)

paper_image("UV.BMP", 20, 470)
paper_smallnum(uv_one_dig(today.uv_index), 80, 310)

paper_text(today.summary, 20, 570)
paper_text(datetime.now().strftime("Updated %A %H:%M."), 20, 5)

paper_update()
