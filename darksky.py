#!/usr/bin/env python

from darksky.api import DarkSky, DarkSkyAsync
from darksky.types import languages, units, weather
API_KEY = open('darksky-secret').readline().rstrip()
darksky = DarkSky(API_KEY)
lat, lon = 42.417821,-71.177747

forecast = darksky.get_forecast(lat,lon,
                                exclude=[weather.MINUTELY, weather.ALERTS])

now = forecast.currently
today = forecast.daily.data[0]

def clamp(n, minn, maxn):
    return max(min(maxn, n), minn)

def two_dig(n, HILO=True):
    if HILO:
        if n >= 100:
            return 'HI'
        if n < 0:
            return 'LO'
    return '{:02d}'.format(int(clamp(n,0,99)))

def uv_one_dig(n):
    if n > 9:
        return '!'
    return '{:01d}'.format(int(n))

iconmap = {'clear-day': 'SUN',
          'clear-night': 'NIGHT',
          'cloudy': 'CLOUD',
          'partly-cloudy-day': 'CLDAY',
          'partly-cloudly-night': 'CLDNT'}

def icon(iconsize, condition):
    return f'{iconsize}' + iconmap.get(condition, condition.upper()) + '.PNG'

# current, high, low, current-icon, UV, worst-icon, precipprob, summary
payload = '|'.join(
        [two_dig(now.apparent_temperature),
 two_dig(today.apparent_temperature_high),
 two_dig(today.apparent_temperature_low),
 icon(3, now.icon),
 uv_one_dig(today.uv_index),
 icon(2, today.icon),
 two_dig(100 * today.precip_probability, HILO=False),
 today.summary
])
print(payload)
