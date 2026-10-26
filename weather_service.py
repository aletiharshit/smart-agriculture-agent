"""
Weather Service for Smart Agriculture Agent.
Fetches real-time agro-meteorological observations from Open-Meteo (100% free, no API key or paid tokens required).
Gracefully falls back to regional benchmark data if network is unavailable or request times out.
Clearly flags whether data is 'live' or 'benchmark/manual'.
"""

import json
import urllib.request
import urllib.error
from typing import Dict, Any, Optional

DEFAULT_LAT = 16.3067   # Guntur / Andhra Pradesh Agricultural Zone benchmark
DEFAULT_LON = 80.4365


def get_weather_forecast(
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    district_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Fetches real-time and 7-day forecast data from Open-Meteo API.
    Does not require any API key or subscription.
    Handles network failures gracefully by returning benchmark data with clear labels.
    """
    lat = latitude if latitude is not None else DEFAULT_LAT
    lon = longitude if longitude is not None else DEFAULT_LON

    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat:.4f}&longitude={lon:.4f}&"
        f"current=temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m,weather_code&"
        f"daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max&"
        f"timezone=auto"
    )

    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "SmartAgriAgent/1.0 (Educational/AgTech)"}
        )
        with urllib.request.urlopen(req, timeout=4) as response:
            data = json.loads(response.read().decode("utf-8"))
            current = data.get("current", {})
            daily = data.get("daily", {})

            return {
                "source": "live",
                "source_label": "Live Meteorological Feed (Open-Meteo, No API Key Required)",
                "temperature": float(current.get("temperature_2m", 28.0)),
                "humidity": float(current.get("relative_humidity_2m", 65.0)),
                "precipitation": float(current.get("precipitation", 0.0)),
                "wind_speed": float(current.get("wind_speed_10m", 5.0)),
                "rain_prob_today": float(daily.get("precipitation_probability_max", [20.0])[0]),
                "temp_max_today": float(daily.get("temperature_2m_max", [32.0])[0]),
                "temp_min_today": float(daily.get("temperature_2m_min", [22.0])[0]),
                "daily_dates": daily.get("time", [])[:7],
                "daily_rain_prob": daily.get("precipitation_probability_max", [])[:7],
                "daily_temp_max": daily.get("temperature_2m_max", [])[:7],
                "daily_temp_min": daily.get("temperature_2m_min", [])[:7],
                "location_name": district_name or "Local Farm Station"
            }

    except Exception:
        # Fallback to realistic regional agricultural benchmark data if offline
        return {
            "source": "benchmark",
            "source_label": "Offline Benchmark / Manual Fallback (Internet connection unavailable)",
            "temperature": 28.5,
            "humidity": 68.0,
            "precipitation": 0.0,
            "wind_speed": 6.2,
            "rain_prob_today": 15.0,
            "temp_max_today": 33.0,
            "temp_min_today": 23.0,
            "daily_dates": ["Today", "Day 2", "Day 3", "Day 4", "Day 5", "Day 6", "Day 7"],
            "daily_rain_prob": [15, 20, 45, 10, 5, 10, 25],
            "daily_temp_max": [33, 34, 31, 32, 33, 34, 33],
            "daily_temp_min": [23, 24, 22, 23, 23, 24, 23],
            "location_name": district_name or "Local Farm Station (Benchmark)"
        }
