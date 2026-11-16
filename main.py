import os
import requests
import yt_dlp
import glob

TOKEN = os.environ["BALE_TOKEN"]
CHANNEL = "@afsaneh_gardeshgari_sarina"

BASE = f"https://tapi.bale.ai/bot{TOKEN}"

# پیام‌های قدیمی تا شماره ۷ نادیده گرفته می‌شوند
response = requests.get(
    f"{BASE}/getUpdates",
    params={"offset": 8},
    timeout=30
).json()

if not response.get("ok"):
    raise Exception(response)

updates = response.get("result", [])

if not updates:
    print("No new messages.")
    exit()

last_id = max(item["update_id"] for item in updates)

for update in updates:
    message = update.get("message", {})
    chat = message.get("chat", {})
    text = message.get("text", "").strip()

    if chat.get("type") != "private":
        continue

    if "instagram.com/" not in text:
        continue

    print("New Instagram link found!")

    options = {
        "outtmpl": "reel_%(id)s.%(ext)s",
        "format": "best[ext=mp4]/best",
        "noplaylist": True
    }

    with yt_dlp.YoutubeDL(options) as ydl:
        info = ydl.extract_info(text, download=True)
        video_path = ydl.prepare_filename(info)

    caption = (
        info.get("description")
        or info.get("title")
        or ""
    )[:1024]

    api = f"{BASE}/sendVideo"

    with open(video_path, "rb") as video:
        result = requests.post(
            api,
            data={
                "chat_id": CHANNEL,
                "caption": caption
            },
            files={"video": video},
            timeout=300
        ).json()

    if not result.get("ok"):
        raise Exception(result)

    print("Video sent successfully!")

# فقط بعد از پردازش موفق، پیام‌ها تأیید می‌شوند
requests.get(
    f"{BASE}/getUpdates",
    params={"offset": last_id + 1},
    timeout=30
).raise_for_status()

print("Updates processed successfully!")