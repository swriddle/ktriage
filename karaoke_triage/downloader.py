import subprocess
from pathlib import Path
from typing import Optional

from .config import DOWNLOADS_DIR

def download_youtube_video(url: str, output_path: Optional[Path] = None) -> bool:
    """Download a YouTube video using yt-dlp."""
    if output_path is None:
        output_path = DOWNLOADS_DIR / "%(title)s.%(ext)s"
    
    try:
        cmd = [
            "yt-dlp",
            url,
            "-o", str(output_path),
            "-x",  # Extract audio
            "--audio-format", "mp3",  # Convert to mp3
            "--audio-quality", "0"  # Best quality
        ]
        
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Error downloading video: {e}")
        print(f"Error output: {e.stderr}")
        return False 