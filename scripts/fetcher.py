import os
import json
import httpx
from datetime import datetime, timezone, timedelta

WAQI_TOKEN = os.environ.get("WAQI_TOKEN", "").strip()
CITIES = ["delhi", "noida", "gurgaon", "mumbai", "bangalore"]
IST = timezone(timedelta(hours=5, minutes=30))

def us_epa_to_raw_pm25(epa_aqi: float) -> float:
    """Inverts US-EPA PM2.5 AQI sub-index back to raw ug/m3 concentration."""
    breakpoints = [
        (0, 50, 0.0, 12.0),
        (51, 100, 12.1, 35.4),
        (101, 150, 35.5, 55.4),
        (151, 200, 55.5, 150.4),
        (201, 300, 150.5, 250.4),
        (301, 500, 250.5, 500.4),
    ]
    for i_low, i_high, c_low, c_high in breakpoints:
        if i_low <= epa_aqi <= i_high:
            return round(((epa_aqi - i_low) / (i_high - i_low)) * (c_high - c_low) + c_low, 1)
    return round(500.4 + (epa_aqi - 500) * 1.25, 1)

def get_roast(cigs: float) -> str:
    if cigs >= 15:
        return "CHAINSMOKER TIER: Even your air purifier needs a nebulizer."
    elif cigs >= 8:
        return "HALF-A-PACK DAY: Complimentary Chotti Advance with every jog."
    elif cigs >= 3:
        return "CASUAL PUFFER: Mild throat itch, ideal for Silk Board traffic."
    return "CLEAN-ISH: Suspiciously breathable. Check if sensor is unplugged."

def fetch_city_average(city: str) -> dict | None:
    """Averages all active monitoring stations for a given city search keyword."""
    search_url = f"https://api.waqi.info/search/?token={WAQI_TOKEN}&keyword={city}"
    resp = httpx.get(search_url, timeout=15.0).json()

    valid_stations = [
        s for s in resp.get("data", [])
        if str(s.get("aqi", "")).isdigit() and int(s.get("aqi", 0)) > 0
    ]

    if not valid_stations:
        return None

    total_aqi = sum(int(s["aqi"]) for s in valid_stations)
    avg_aqi = round(total_aqi / len(valid_stations))

    # Approximate city-wide raw PM2.5 density from the averaged US-EPA AQI
    raw_pm25 = us_epa_to_raw_pm25(float(avg_aqi))
    cigs_24h = round(raw_pm25 / 22.0, 1)

    return {
        "city": city.upper(),
        "station": f"City Average ({len(valid_stations)} active stations)",
        "timestamp": datetime.now(IST).strftime("%d %b %Y, %I:%M %p IST"),
        "overall_aqi": avg_aqi,
        "raw_pm25": raw_pm25,
        "cigs_24h": cigs_24h,
        "cigs_6h": round(cigs_24h * 0.25, 1),
        "status_roast": get_roast(cigs_24h)
    }

def build_daily_payload():
    if not WAQI_TOKEN:
        raise RuntimeError("Missing WAQI_TOKEN secret in GitHub Actions!")

    results = []
    for city in CITIES:
        city_data = fetch_city_average(city)
        if city_data:
            results.append(city_data)

    if not results:
        raise RuntimeError("No valid city AQI data returned from WAQI API.")

    results.sort(key=lambda x: x["cigs_24h"], reverse=True)
    top_city = results[0]
    top_city["leaderboard"] = [
        {"city": r["city"], "aqi": r["overall_aqi"], "cigs": r["cigs_24h"]}
        for r in results
    ]

    with open("receipt_props.json", "w") as f:
        json.dump(top_city, f, indent=2)
    print(f"✅ City-wide average computed. Top offender: {top_city['city']} ({top_city['overall_aqi']} AQI | {top_city['cigs_24h']} cigs)")

if __name__ == "__main__":
    build_daily_payload()
