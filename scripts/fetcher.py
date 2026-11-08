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
    # Extrapolation for extreme spikes above 500 AQI
    return round(500.4 + (epa_aqi - 500) * 1.25, 1)

def get_roast(cigs: float) -> str:
    if cigs >= 20:
        return "APOCALYPSE TIER: You aren't breathing air, you're inhaling a chimney."
    elif cigs >= 10:
        return "CHAINSMOKER TIER: Even your air purifier needs a nebulizer."
    elif cigs >= 5:
        return "HALF-A-PACK DAY: Complimentary Chotti Advance with every jog."
    elif cigs >= 2:
        return "CASUAL PUFFER: Mild throat itch, ideal for traffic congestion."
    return "CLEAN-ISH: Suspiciously breathable. Check if sensor is unplugged."

def fetch_max_station_data(city: str) -> dict | None:
    """Scans all active stations in a city and returns the MAXIMUM peak reading."""
    search_url = f"https://api.waqi.info/search/?token={WAQI_TOKEN}&keyword={city}"
    try:
        resp = httpx.get(search_url, timeout=12.0).json()
        valid_stations = [
            s for s in resp.get("data", [])
            if str(s.get("aqi", "")).isdigit() and int(s.get("aqi", 0)) > 0
        ]
        
        if valid_stations:
            # Sort descending by AQI to get the absolute worst hotspot first
            valid_stations.sort(key=lambda s: int(s["aqi"]), reverse=True)
            worst_station = valid_stations[0]
            worst_uid = worst_station["uid"]

            # Fetch detailed feed for that specific peak station
            feed_url = f"https://api.waqi.info/feed/@{worst_uid}/?token={WAQI_TOKEN}"
            feed_resp = httpx.get(feed_url, timeout=12.0).json()
            
            if feed_resp.get("status") == "ok":
                data = feed_resp["data"]
                max_aqi = int(data["aqi"])
                
                # Extract PM2.5 sub-index if available, otherwise use max_aqi
                pm25_sub = data.get("iaqi", {}).get("pm25", {}).get("v", max_aqi)
                raw_pm25 = us_epa_to_raw_pm25(float(pm25_sub))
                cigs_24h = round(raw_pm25 / 22.0, 1)

                return {
                    "city": city.upper(),
                    "station": data["city"]["name"],
                    "timestamp": datetime.now(IST).strftime("%d %b %Y, %I:%M %p IST"),
                    "overall_aqi": max_aqi,
                    "raw_pm25": raw_pm25,
                    "cigs_24h": cigs_24h,
                    "cigs_6h": round(cigs_24h * 0.25, 1),
                    "status_roast": get_roast(cigs_24h)
                }
    except Exception:
        pass

    # Fallback to direct city feed if search fails
    feed_url = f"https://api.waqi.info/feed/{city}/?token={WAQI_TOKEN}"
    try:
        resp = httpx.get(feed_url, timeout=12.0).json()
        if resp.get("status") == "ok":
            data = resp["data"]
            aqi = int(data["aqi"])
            raw_pm25 = us_epa_to_raw_pm25(float(aqi))
            cigs_24h = round(raw_pm25 / 22.0, 1)
            return {
                "city": city.upper(),
                "station": data["city"]["name"],
                "timestamp": datetime.now(IST).strftime("%d %b %Y, %I:%M %p IST"),
                "overall_aqi": aqi,
                "raw_pm25": raw_pm25,
                "cigs_24h": cigs_24h,
                "cigs_6h": round(cigs_24h * 0.25, 1),
                "status_roast": get_roast(cigs_24h)
            }
    except Exception:
        pass

    return None

def build_daily_payload():
    if not WAQI_TOKEN:
        raise RuntimeError("Missing WAQI_TOKEN secret in GitHub Actions!")

    results = []
    for city in CITIES:
        city_data = fetch_max_station_data(city)
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
    print(f"✅ Max peak captured. Top offender: {top_city['city']} ({top_city['station']} | {top_city['overall_aqi']} AQI)")

if __name__ == "__main__":
    build_daily_payload()
