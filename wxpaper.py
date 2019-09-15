#!/usr/bin/env python3

from darksky.api import DarkSky, DarkSkyAsync
from darksky.types import languages, units, weather
from sh import particle
import datetime

particle_id = "3eink"

seconds_between_updates = 2 * 60


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


def icon(iconsize, condition):
    iconmap = {
        "clear-day": "SUN",
        "clear-night": "NIGHT",
        "cloudy": "CLOUD",
        "partly-cloudy-day": "CLDAY",
        "partly-cloudly-night": "CLDNT",
    }
    return str(iconsize) + iconmap.get(condition, condition.upper()) + ".BMP"


def paper_rect(x0, y0, x1, y1):
    particle(
        "function",
        "call",
        particle_id,
        "rect",
        "|".join((str(x0), str(y0), str(x1), str(y1))),
    )


def paper_image(bitmap, x, y):
    particle("function", "call", particle_id, "img", "|".join((bitmap, str(x), str(y))))


def paper_fontsize(s):
    particle("function", "call", particle_id, "fontsize", str(s))


def paper_bignum(n, x, y):
    paper_image("300_{}.BMP".format(n), x, y)


def paper_smallnum(n, x, y):
    paper_image("165_{}.BMP".format(n), x, y)


def paper_text(text, x, y):
    particle("function", "call", particle_id, "text", "|".join((text, str(x), str(y))))


def paper_cmd(cmd):
    particle("function", "call", particle_id, cmd)


def paper_deepsleep(seconds):
    particle("function", "call", particle_id, "deepsleep", str(seconds_between_updates))


def do_update():
    API_KEY = open("darksky-secret").readline().rstrip()
    darksky = DarkSky(API_KEY)
    lat, lon = 42.417821, -71.177747

    forecast = darksky.get_forecast(
        lat, lon, exclude=[weather.MINUTELY, weather.ALERTS]
    )

    now = forecast.currently
    today = forecast.daily.data[0]
    paper_cmd("wake")
    paper_cmd("clear")

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

    paper_fontsize(32)
    paper_text(today.summary, 20, 570)

    nowt = datetime.datetime.now()
    paper_text(nowt.strftime("Last update %H:%M"), 20, 5)
    paper_text(
        (nowt + datetime.timedelta(seconds=seconds_between_updates)).strftime(
            "Next update %H:%M"
        ),
        500,
        5,
    )

    # day of week and date
    paper_fontsize(64)
    paper_text(nowt.strftime("%a"), 310, 370)
    paper_text(nowt.strftime("%b %-d"), 280, 440)
    paper_rect(260, 360, 455, 520)

    paper_cmd("update")
    paper_cmd("stop")
    paper_deepsleep(seconds_between_updates)
    print("done")


if __name__ == "__main__":
    do_update()
