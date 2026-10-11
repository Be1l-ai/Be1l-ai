"""Generates two SVG cards for the profile README:
  profile/weather.svg  - current weather (Open-Meteo, no API key needed)
  profile/now.svg      - a small "right now" card (edit the values below)
Runs inside GitHub Actions. Standard library only.
"""
import json
import os
import sys
import urllib.request
from datetime import datetime, timedelta, timezone
from xml.sax.saxutils import escape

# ---- edit these ------------------------------------------------------------
LABEL = "Dasmariñas, Cavite"          # what the card displays
LAT, LON = 14.3294, 120.9367          # used only to fetch the weather
BUILDING = "Study Bot"
LEARNING = "pandas · NumPy · SQL"
# ---------------------------------------------------------------------------

OUT_DIR = "profile"
FONT = "'Segoe UI', Ubuntu, 'Helvetica Neue', Sans-Serif"
BG, PINK, CYAN, YELLOW = "#141321", "#fe428e", "#a9fef7", "#f8d847"

WMO = {  # code: (description, icon kind)
    0: ("Clear sky", "sun"), 1: ("Mostly clear", "sun"), 2: ("Partly cloudy", "partly"),
    3: ("Overcast", "cloud"), 45: ("Foggy", "fog"), 48: ("Foggy", "fog"),
    51: ("Light drizzle", "rain"), 53: ("Drizzle", "rain"), 55: ("Heavy drizzle", "rain"),
    61: ("Light rain", "rain"), 63: ("Rain", "rain"), 65: ("Heavy rain", "rain"),
    80: ("Rain showers", "rain"), 81: ("Rain showers", "rain"), 82: ("Violent showers", "storm"),
    95: ("Thunderstorm", "storm"), 96: ("Thunderstorm", "storm"), 99: ("Thunderstorm", "storm"),
}

CLOUD = ('<circle cx="16" cy="34" r="11"/><circle cx="32" cy="26" r="15"/>'
         '<circle cx="48" cy="35" r="10"/><rect x="16" y="34" width="32" height="11"/>')
RAYS = "".join(
    f'<line x1="{30+15*c:.1f}" y1="{22+15*s_:.1f}" x2="{30+21*c:.1f}" y2="{22+21*s_:.1f}"/>'
    for c, s_ in [(1,0),(.71,.71),(0,1),(-.71,.71),(-1,0),(-.71,-.71),(0,-1),(.71,-.71)]
)


def icon(kind):
    sun = f'<g stroke="{YELLOW}" stroke-width="3" stroke-linecap="round" fill="{YELLOW}"><circle cx="30" cy="22" r="10" stroke="none"/>{RAYS}</g>'
    cloud = f'<g fill="#cfd3e6">{CLOUD}</g>'
    parts = {
        "sun": sun,
        "partly": f'<g transform="translate(-8 -8) scale(.75)">{sun}</g><g transform="translate(8 6) scale(.9)">{cloud}</g>',
        "cloud": cloud,
        "fog": f'<g transform="scale(.9)">{cloud}</g><g stroke="#8a8aa5" stroke-width="3" stroke-linecap="round"><line x1="8" y1="46" x2="52" y2="46"/><line x1="14" y1="53" x2="46" y2="53"/></g>',
        "rain": f'<g transform="scale(.9)">{cloud}</g><g stroke="{CYAN}" stroke-width="3" stroke-linecap="round"><line x1="16" y1="48" x2="12" y2="56"/><line x1="29" y1="48" x2="25" y2="56"/><line x1="42" y1="48" x2="38" y2="56"/></g>',
        "storm": f'<g transform="scale(.9)">{cloud}</g><polygon points="30,38 20,54 29,54 24,64 42,46 32,46 38,38" fill="{YELLOW}"/>',
    }
    return parts.get(kind, cloud)


def fetch():
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={LAT}&longitude={LON}"
        "&current=temperature_2m,relative_humidity_2m,apparent_temperature,"
        "weather_code,wind_speed_10m&timezone=Asia%2FManila"
    )
    with urllib.request.urlopen(url, timeout=20) as r:
        return json.load(r)["current"]


def card(width, height, body):
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">\n'
        f'<rect x="0.5" y="0.5" rx="4.5" width="{width-1}" height="{height-1}" fill="{BG}"/>\n'
        f"{body}\n</svg>\n"
    )


def weather_svg(c):
    desc, kind = WMO.get(c["weather_code"], ("Unknown", "cloud"))
    temp = round(c["temperature_2m"])
    feels = round(c["apparent_temperature"])
    hum = round(c["relative_humidity_2m"])
    wind = round(c["wind_speed_10m"])
    now = datetime.now(timezone(timedelta(hours=8))).strftime("%b %d, %I:%M %p PHT")
    body = f"""
<text x="25" y="35" font-family="{FONT}" font-size="18" font-weight="600" fill="{PINK}">{escape(LABEL)}</text>
<text x="25" y="100" font-family="{FONT}" font-size="52" font-weight="700" fill="{YELLOW}">{temp}°C</text>
<g transform="translate(255 52)">{icon(kind)}</g>
<text x="25" y="127" font-family="{FONT}" font-size="15" font-weight="600" fill="{CYAN}">{escape(desc)}</text>
<text x="25" y="152" font-family="{FONT}" font-size="12" fill="{CYAN}">Feels like {feels}°C  ·  Humidity {hum}%  ·  Wind {wind} km/h</text>
<text x="25" y="173" font-family="{FONT}" font-size="11" fill="#8a8aa5">Updated {now}</text>"""
    return card(340, 190, body)


def now_svg():
    rows = [("Building", BUILDING), ("Learning", LEARNING), ("Fuel", "Coffee")]
    body = f'<text x="25" y="35" font-family="{FONT}" font-size="18" font-weight="600" fill="{PINK}">Right now</text>\n'
    y = 70
    for k, v in rows:
        body += (
            f'<text x="25" y="{y}" font-family="{FONT}" font-size="14" font-weight="600" fill="{YELLOW}">{k}</text>\n'
            f'<text x="105" y="{y}" font-family="{FONT}" font-size="14" fill="{CYAN}">{escape(v)}</text>\n'
        )
        y += 30
    return card(340, 150, body)


def write(name, text):
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, name), "w", encoding="utf-8") as f:
        f.write(text)
    print("wrote", name)


def main():
    write("now.svg", now_svg())
    try:
        write("weather.svg", weather_svg(fetch()))
    except Exception as e:  # keep the previous weather card if the API is down
        print("WARNING: weather fetch failed, keeping old card:", e, file=sys.stderr)


if __name__ == "__main__":
    main()
