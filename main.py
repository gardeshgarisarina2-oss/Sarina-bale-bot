import os
import requests
import yt_dlp
import time

TOKEN = os.environ["BALE_TOKEN"]
CHANNEL = "@afsaneh_gardeshgari_sarina"
BASE = f"https://tapi.bale.ai/bot{TOKEN}"

# دریافت پیام‌های جدید
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
    sent = False

    for attempt in range(1, 4):
        print(f"Sending video, attempt {attempt}/3")

        try:
            with open(video_path, "rb") as video:
                result = requests.post(
                    api,
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
                    timeout=(30, 180)
                )

            print("Bale response:", result.text)

            data = result.json()

            if data.get("ok"):
                print("Video sent successfully!")
                sent = True
                break

            print("Bale upload failed:", data)

        except Exception as error:
            print("Upload error:", error)

        if attempt < 3:
            time.sleep(5)

    if not sent:
        raise Exception("Video could not be sent after 3 attempts.")

# تأیید پیام‌ها بعد از پردازش موفق
requests.get(
    f"{BASE}/getUpdates",
    params={"offset": last_id + 1},
    timeout=30
).raise_for_status()

print("Updates processed successfully!")