import subprocess
from pathlib import Path
from typing import Optional
from yt_dlp import YoutubeDL

from .config import DOWNLOADS_DIR


def progress_hook(d):
    # TODO Use this to show a progress bar modal
    pass


def download_youtube_video(url: str, output_path: Optional[Path] = None) -> bool:
    """Download a YouTube video using yt-dlp."""
    if output_path is None:
        output_path = DOWNLOADS_DIR / "%(title)s.%(ext)s"

    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',  # Choose the best quality
        'outtmpl': str(output_path),  # Save location
        'progress_hooks': [progress_hook],  # Hook for progress
        'merge_output_format': 'mp4',
    }

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download(url)
