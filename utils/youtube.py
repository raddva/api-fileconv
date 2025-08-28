import os
import yt_dlp

def download_youtube_mp3(url, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": os.path.join(output_dir, "%(title)s.%(ext)s"),
        "quiet": True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        original_path = ydl.prepare_filename(info)

        base, _ = os.path.splitext(original_path)
        mp3_path = base + ".mp3"
        os.rename(original_path, mp3_path)

        return mp3_path, info.get("title", "audio")
