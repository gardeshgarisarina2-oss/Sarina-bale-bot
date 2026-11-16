import os
import glob
import requests
import yt_dlp

TOKEN = os.environ["BALE_TOKEN"]
CHANNEL = "@afsaneh_gardeshgari_sarina"

# دریافت پیام‌های ربات
url = f"https://tapi.bale.ai/bot{TOKEN}/getUpdates"
data = requests.get(url, timeout=30).json()

if not data.get("ok"):
    raise Exception(data)

updates = data.get("result", [])

# پیدا کردن آخرین لینک اینستاگرام در پیام خصوصی
reel_url = None

for update in updates:
    message = update.get("message", {})
    chat = message.get("chat", {})
    text = message.get("text", "")

    if chat.get("type") == "private" and "instagram.com/" in text:
        reel_url = text.strip()

if not reel_url:
    print("No Instagram link found.")
    exit()

print("Instagram link found!")

# دانلود ویدئو
options = {
    "outtmpl": "reel.%(ext)s",
    "format": "best[ext=mp4]/best",
    "noplaylist": True
}

with yt_dlp.YoutubeDL(options) as ydl:
    info = ydl.extract_info(reel_url, download=True)

files = glob.glob("reel.*")

if not files:
    raise Exception("Video not found!")

video_path = files[0]
caption = (info.get("description") or info.get("title") or "")[:1024]

# ارسال به کانال بله
api = f"https://tapi.bale.ai/bot{TOKEN}/sendVideo"

with open(video_path, "rb") as video:
    response = requests.post(
        api,
        data={"chat_id": CHANNEL, "caption": caption},
        files={"video": video},
        timeout=300
    )

result = response.json()

if not result.get("ok"):
    raise Exception(result)

print("Video sent to Bale successfully!")