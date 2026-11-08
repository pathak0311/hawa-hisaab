import os
import json
import httpx
from datetime import datetime, timezone, timedelta

WAQI_TOKEN = os.getenv("WAQI_TOKEN")
CITIES = ["delhi", "noida", "gurgaon", "mumbai", "bangalore"]
IST = timezone(timedelta(hours=5, minutes=30))

def aqi_to_raw_pm25(aqi: float) -> float:
    breakpoints = [
        (0, 50, 0.0, 12.0), (51, 100, 12.1, 35.4),
        (101, 150, 35.5, 55.4), (151, 200, 55.5, 150.4),
        (201, 300, 150.5, 250.4), (301, 500, 250.5, 500.4),
    ]
    for i_low, i_high, c_low, c_high in breakpoints:
        if i_low <= aqi <= i_high:
            return round(((aqi - i_low) / (i_high - i_low)) * (c_high - c_low) + c_low, 1)
    return round(250.5 + (aqi - 300) * 1.25, 1)

def get_roast(cigs: float) -> str:
    if cigs >= 15:
        return "CHAINSMOKER TIER: Even your air purifier needs a nebulizer."
    elif cigs >= 8:
        return "HALF-A-PACK DAY: Complimentary Chotti Advance with every jog."
    elif cigs >= 3:
        return "CASUAL PUFFER: Mild throat itch, ideal for Silk Board traffic."
    return "CLEAN-ISH: Suspiciously breathable. Check if sensor is unplugged."

def build_daily_payload():
    results = []
    for city in CITIES:
        url = f"https://api.waqi.info/feed/{city}/?token={WAQI_TOKEN}"
        resp = httpx.get(url, timeout=10.0).json()
        if resp.get("status") == "ok":
            data = resp["data"]
            overall_aqi = int(data["aqi"])
            pm25_sub = data.get("iaqi", {}).get("pm25", {}).get("v", overall_aqi)
            raw_pm25 = aqi_to_raw_pm25(float(pm25_sub))
            cigs_24h = round(raw_pm25 / 22.0, 1)
            results.append({
                "city": city.upper(),
                "station": data["city"]["name"],
                "timestamp": datetime.now(IST).strftime("%d %b %Y, %I:%M %p IST"),
                "overall_aqi": overall_aqi,
                "raw_pm25": raw_pm25,
                "cigs_24h": cigs_24h,
                "cigs_6h": round(cigs_24h * 0.25, 1),
                "status_roast": get_roast(cigs_24h)
            })

    # Sort by highest cigarette intake so the worst city gets featured on the receipt
    results.sort(key=lambda x: x["cigs_24h"], reverse=True)
    top_city = results[0]
    top_city["leaderboard"] = [
        {"city": r["city"], "aqi": r["overall_aqi"], "cigs": r["cigs_24h"]}
        for r in results
    ]

    with open("receipt_props.json", "w") as f:
        json.dump(top_city, f, indent=2)

if __name__ == "__main__":
    build_daily_payload()
