import os
import re
import time
import requests
import yt_dlp

TOKEN = os.environ["BALE_TOKEN"]
CHANNEL = "@afsaneh_gardeshgari_sarina"
BASE = f"https://tapi.bale.ai/bot{TOKEN}"

session = requests.Session()

response = session.get(
    f"{BASE}/getUpdates",
    timeout=40
).json()

if not response.get("ok"):
    raise Exception(response)

updates = sorted(
    response.get("result", []),
    key=lambda x: x["update_id"]
)

if not updates:
    print("No new messages.")
    exit()

last_id = max(u["update_id"] for u in updates)
seen_reels = set()

for update in updates:
    message = update.get("message", {})
    chat = message.get("chat", {})
    link = message.get("text", "").strip()

    if chat.get("type") != "private":
        continue

    if "instagram.com/" not in link:
        continue

    match = re.search(r"/(?:reel|reels|p)/([^/?]+)", link)

    if not match:
        continue

    reel_id = match.group(1)

    if reel_id in seen_reels:
        print("Duplicate link skipped:", reel_id)
        continue

    seen_reels.add(reel_id)
    print("New Reel:", reel_id)

    options = {
        "outtmpl": "reel_%(id)s.%(ext)s",
        "format": "best[ext=mp4]/best",
        "noplaylist": True,
        "retries": 3
    }

    with yt_dlp.YoutubeDL(options) as ydl:
        info = ydl.extract_info(link, download=True)
        video_path = ydl.prepare_filename(info)

    caption = (
        info.get("description")
        or info.get("title")
        or ""
    )[:1024]

    print("Uploading video...")

    try:
        with open(video_path, "rb") as video:
            result = session.post(
                f"{BASE}/sendVideo",
                data={
                    "chat_id": CHANNEL,
                    "caption": caption
                },
                files={
                    "video": (
                        os.path.basename(video_path),
                        video,
                        "video/mp4"
                    )
                },
                timeout=(30, 300)
            )

        data = result.json()
        print(data)

        if data.get("ok"):
            print("Video sent successfully!")
        else:
            print("Bale returned an error. Check channel before retrying.")

    except requests.exceptions.RequestException as error:
        print("Upload result uncertain:", error)
        print("No automatic retry to prevent duplicate posts.")

# Acknowledge received messages
session.get(
    f"{BASE}/getUpdates",
    params={"offset": last_id + 1},
    timeout=40
).raise_for_status()

print("All messages processed!")