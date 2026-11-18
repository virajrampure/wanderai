"""Weather via Open-Meteo (free, no API key). Falls back gracefully when offline."""
import requests

CODES = {0: "clear", 1: "mostly clear", 2: "partly cloudy", 3: "overcast", 45: "fog", 51: "light drizzle",
         61: "rain", 63: "rain", 65: "heavy rain", 71: "snow", 80: "showers", 95: "thunderstorm"}


def forecast(lat, lon, days=3):
    try:
        r = requests.get("https://api.open-meteo.com/v1/forecast", timeout=5, params={
            "latitude": lat, "longitude": lon, "forecast_days": min(max(days, 1), 7), "timezone": "auto",
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max,weathercode"})
        r.raise_for_status()
        d = r.json()["daily"]
        return [{"date": d["time"][i], "max_c": d["temperature_2m_max"][i], "min_c": d["temperature_2m_min"][i],
                 "rain_pct": d["precipitation_probability_max"][i],
                 "summary": CODES.get(d["weathercode"][i], "mixed")} for i in range(len(d["time"]))]
    except Exception:
        return []  # offline or API error: planner continues without live weather
