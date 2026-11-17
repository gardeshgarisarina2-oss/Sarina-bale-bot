import os
import re
import requests
import yt_dlp

TOKEN = os.environ["BALE_TOKEN"]
CHANNEL = "@afsaneh_gardeshgari_sarina"
BASE = f"https://tapi.bale.ai/bot{TOKEN}"

session = requests.Session()


def acknowledge(update_id):
    response = session.get(
        f"{BASE}/getUpdates",
        params={"offset": update_id + 1},
        timeout=20
    )
    response.raise_for_status()

    data = response.json()
    if not data.get("ok"):
        raise Exception(f"Acknowledgment failed: {data}")

    print(f"Update {update_id} acknowledged.")


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
    raise SystemExit(0)

seen_reels = set()

for update in updates:
    update_id = update["update_id"]
    message = update.get("message")

    if not isinstance(message, dict):
        print("Ignored update:", update_id)
        acknowledge(update_id)
        continue

    chat = message.get("chat", {})
    chat_type = chat.get("type", "")
    link = (
        message.get("text")
        or message.get("caption")
        or ""
    ).strip()

    print(
        f"Update: {update_id} | "
        f"Chat: {chat_type} | "
        f"Text: {link[:120]}"
    )

    if chat_type != "private":
        print("Ignored: not a private chat.")
        acknowledge(update_id)
        continue

    if "instagram.com/" not in link:
        print("Ignored: no Instagram link.")
        acknowledge(update_id)
        continue

    match = re.search(
        r"/(?:reel|reels|p|tv)/([^/?]+)",
        link
    )

    if not match:
        print("Ignored: Instagram link format not recognized.")
        acknowledge(update_id)
        continue

    reel_id = match.group(1)

    if reel_id in seen_reels:
        print("Duplicate Reel skipped:", reel_id)
        acknowledge(update_id)
        continue

    seen_reels.add(reel_id)
    print("New Reel found:", reel_id)

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

    print("Uploading to Bale...")

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
        print("Bale response:", data)

        if data.get("ok"):
            print("Video sent successfully!")
        else:
            print("Bale rejected the upload.")

    except (requests.exceptions.RequestException, ValueError) as error:
        print("Upload result uncertain:", error)
        print("No retry to prevent duplicate posts.")

    # تأیید همین پیام، بعد از پردازش
    acknowledge(update_id)

print("All messages processed!")