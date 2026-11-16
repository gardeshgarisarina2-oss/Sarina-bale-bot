import os
import glob
import requests
import yt_dlp

TOKEN = os.environ["BALE_TOKEN"]
CHANNEL = "@afsaneh_gardeshgari_sarina"

REEL_URL = "https://www.instagram.com/reel/DadQ2nyssJL/"

options = {
    "outtmpl": "reel.%(ext)s",
    "format": "best[ext=mp4]/best",
    "noplaylist": True
}

with yt_dlp.YoutubeDL(options) as ydl:
    info = ydl.extract_info(REEL_URL, download=True)
    video_path = ydl.prepare_filename(info)

if not os.path.exists(video_path):
    raise FileNotFoundError("Video file not found!")

caption = info.get("description") or info.get("title") or ""
caption = caption[:1024]

api_url = f"https://tapi.bale.ai/bot{TOKEN}/sendVideo"

with open(video_path, "rb") as video:
    response = requests.post(
        api_url,
        data={
            "chat_id": CHANNEL,
            "caption": caption
        },
        files={
            "video": (os.path.basename(video_path), video)
        },
        timeout=(30, 300)
    )

result = response.json()

if not result.get("ok"):
    raise Exception(f"Bale error: {result}")

print("Video sent to Bale successfully! ❤️")