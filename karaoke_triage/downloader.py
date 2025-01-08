import json
from pathlib import Path
import subprocess
from typing import Optional, Callable
from yt_dlp import YoutubeDL

from .config import DOWNLOADS_DIR


# def progress_hook(d):
#     # TODO Use this to show a progress bar modal
#     with open('/Users/sean/hook-format.txt', 'a') as f:
#         f.write(json.dumps(d))
#         f.write('\n-----------------\n')


def download_youtube_video(url: str, output_path: Optional[Path] = None, progress_callback: Optional[Callable] = None) -> bool:
    """Download a YouTube video using yt-dlp."""
    if output_path is None:
        output_path = DOWNLOADS_DIR / "%(title)s.%(ext)s"

    def progress_hook(d):
        if progress_callback:
            progress_callback(d)

    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',
        'outtmpl': str(output_path),
        'progress_hooks': [progress_hook],
        'merge_output_format': 'mp4',
        'noplaylist': True,
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return True
    except Exception as e:
        print(f"Error downloading video: {e}")
        return False
