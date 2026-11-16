import yt_dlp

url = "https://www.instagram.com/reel/DadQ2nyssJL/"

options = {
    "outtmpl": "reel.%(ext)s",
    "format": "best",
    "noplaylist": True
}

with yt_dlp.YoutubeDL(options) as ydl:
    ydl.download([url])

print("Video downloaded successfully!")