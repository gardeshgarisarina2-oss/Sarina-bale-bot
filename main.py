import os
import requests
import yt_dlp
import time

TOKEN = os.environ["BALE_TOKEN"]
CHANNEL = "@afsaneh_gardeshgari_sarina"
BASE = f"https://tapi.bale.ai/bot{TOKEN}"

session = requests.Session()

# دریافت پیام‌های تأییدنشده، بدون شماره ثابت
response = session.get(
    f"{BASE}/getUpdates",
    timeout=40
).json()

if not response.get("ok"):
    raise Exception(response)

updates = response.get("result", [])

if not updates:
    print("No new messages.")
    exit()

last_id = max(u["update_id"] for u in updates)

for update in updates:
    message = update.get("message", {})
    
    if not message:
        continue

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
        "noplaylist": True,
        "retries": 3
    }

    with yt_dlp.YoutubeDL(options) as ydl:
        info = ydl.extract_info(text, download=True)
        video_path = ydl.prepare_filename(info)

    caption = (
        info.get("description")
        or info.get("title")
        or ""
    )[:1024]

    sent = False

    for attempt in range(1, 4):
        print(f"Sending attempt {attempt}/3")

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
                    timeout=(30, 180)
                )

            data = result.json()
            print(data)

            if data.get("ok"):
                sent = True
                print("Video sent successfully!")
                break

        except Exception as error:
            print("Upload error:", error)

        if attempt < 3:
            time.sleep(5)

    if not sent:
        raise Exception("Video sending failed")

# تأیید پیام‌ها فقط پس از ارسال موفق
session.get(
    f"{BASE}/getUpdates",
    params={"offset": last_id + 1},
    timeout=30
).raise_for_status()

print("All messages processed!")