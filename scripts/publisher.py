import os
import json
import httpx

def get_fresh_access_token() -> str:
    client_id = os.environ["X_CLIENT_ID"]
    client_secret = os.environ["X_CLIENT_SECRET"]
    refresh_token = os.environ["X_REFRESH_TOKEN"]

    resp = httpx.post(
        "https://api.x.com/2/oauth2/token",
        data={
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": client_id,
        },
        auth=(client_id, client_secret),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=15.0,
    ).json()

    if "access_token" not in resp:
        raise RuntimeError(f"OAuth2 Token Refresh Failed: {resp}")

    # Pass the new refresh token to the next GitHub Actions step so it updates the secret
    gh_env = os.getenv("GITHUB_ENV")
    if gh_env and "refresh_token" in resp:
        with open(gh_env, "a") as f:
            f.write(f"NEW_X_REFRESH_TOKEN={resp['refresh_token']}\n")

    return resp["access_token"]

def main():
    with open("receipt_props.json") as f:
        data = json.load(f)

    board_lines = []
    for idx, entry in enumerate(data["leaderboard"], 1):
        medal = "🥇" if idx == 1 else "🥈" if idx == 2 else "🥉" if idx == 3 else "•"
        board_lines.append(f"{medal} {entry['city']}: {entry['cigs']} cigs ({entry['aqi']} AQI)")
    leaderboard_text = "\n".join(board_lines)

    caption = (
        f"🧾 HAWA HISAAB | {data['timestamp']}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🚨 Top Offender: {data['city']} ({data['cigs_24h']} cigs/day)\n"
        f"🌫️ Raw PM2.5: {data['raw_pm25']} µg/m³\n\n"
        f"🚬 24-Hr National Lung Khata:\n"
        f"{leaderboard_text}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"💬 {data['status_roast']}\n\n"
        f"#HawaHisaab #{data['city']}AQI #IndiaAQI"
    )

    access_token = get_fresh_access_token()

    tweet_resp = httpx.post(
        "https://api.x.com/2/tweets",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
        json={"text": caption},
        timeout=15.0,
    ).json()

    if "data" not in tweet_resp:
        raise RuntimeError(f"Failed to post tweet: {tweet_resp}")

    print("✅ Published Text Receipt Tweet:", tweet_resp)

if __name__ == "__main__":
    main()
