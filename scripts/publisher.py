import os
import json
import tweepy
import httpx

def main():
    with open("receipt_props.json") as f:
        data = json.load(f)

    board_lines = []
    for idx, entry in enumerate(data["leaderboard"], 1):
        medal = "🥇" if idx == 1 else "🥈" if idx == 2 else "🥉" if idx == 3 else "•"
        board_lines.append(f"{medal} {entry['city']}: {entry['cigs']} cigs ({entry['aqi']} AQI)")
    leaderboard_text = "\n".join(board_lines)

    caption = (
        f"🧾 AAJ KA HAWA HISAAB ({data['timestamp']})\n\n"
        f"{data['city']} tops the Lung Khata today at {data['cigs_24h']} passive cigarettes/day.\n\n"
        f"🚬 24-Hr National Standings:\n"
        f"{leaderboard_text}\n\n"
        f"💬 {data['status_roast']}\n\n"
        f"#HawaHisaab #{data['city']}AQI #IndiaAQI #AirPollution"
    )

    # 1. Publish to X
    auth = tweepy.OAuth1UserHandler(
        os.getenv("X_API_KEY"), os.getenv("X_API_SECRET"),
        os.getenv("X_ACCESS_TOKEN"), os.getenv("X_ACCESS_SECRET")
    )
    api_v1 = tweepy.API(auth)
    client_v2 = tweepy.Client(
        consumer_key=os.getenv("X_API_KEY"),
        consumer_secret=os.getenv("X_API_SECRET"),
        access_token=os.getenv("X_ACCESS_TOKEN"),
        access_token_secret=os.getenv("X_ACCESS_SECRET")
    )

    media = api_v1.media_upload(filename="out/receipt.png")
    client_v2.create_tweet(text=caption, media_ids=[media.media_id])

    # 2. Publish to Instagram (Optional)
    ig_user_id = os.getenv("IG_USER_ID")
    ig_token = os.getenv("IG_ACCESS_TOKEN")
    public_png_url = os.getenv("PUBLIC_PNG_URL", "").strip()

    if ig_user_id and ig_token and public_png_url:
        base_url = f"https://graph.facebook.com/v21.0/{ig_user_id}"
        container = httpx.post(
            f"{base_url}/media",
            params={"image_url": public_png_url, "caption": caption, "access_token": ig_token}
        ).json()
        if "id" in container:
            httpx.post(
                f"{base_url}/media_publish",
                params={"creation_id": container["id"], "access_token": ig_token}
            )

if __name__ == "__main__":
    main()
