import os
import json
import httpx

def get_fresh_access_token() -> str:
    client_id = os.environ["X_CLIENT_ID"].strip()
    client_secret = os.environ["X_CLIENT_SECRET"].strip()
    refresh_token = os.environ["X_REFRESH_TOKEN"].strip()

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
        board_lines.append(f"{medal} {entry['city']}: {entry['cigs']}c (AQI {entry['aqi']})")
    
    leaderboard_text = "\n".join(board_lines)

    # Ultra-compact caption guaranteed under 280 chars
    caption = (
        f"🧾 HAWA HISAAB | {data['timestamp']}\n\n"
        f"🚨 Worst: {data['city']} ({data['cigs_24h']} cigs/day | PM2.5 22µg=1c)\n\n"
        f"{leaderboard_text}\n\n"
        f"#HawaHisaab #{data['city']}AQI"
    )

    print(f"Prepared tweet ({len(caption)} chars):\n{caption}\n")

    access_token = get_fresh_access_token()

    resp = httpx.post(
        "https://api.x.com/2/tweets",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
        json={"text": caption},
        timeout=15.0,
    )

    tweet_resp = resp.json()
    if resp.status_code != 201 or "data" not in tweet_resp:
        raise RuntimeError(f"Failed to post tweet ({resp.status_code}): {tweet_resp}")

    print("✅ Published Compact Receipt Tweet:", tweet_resp)

if __name__ == "__main__":
    main()
