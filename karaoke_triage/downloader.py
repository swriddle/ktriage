# import json
# import os
from pathlib import Path
# import subprocess
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
    # p = Path(os.path.expanduser('~/kldssdkljffdsklj.txt'))
    if output_path is None:
        output_path = DOWNLOADS_DIR / "%(title)s.%(ext)s"

    def progress_hook(d):
        # Only call progress_callback if we have fragment information
        if progress_callback and 'downloaded_bytes' in d and 'total_bytes' in d:
            # with open(p, 'a') as f:
            #     f.write('1a\n')
            progress_callback(d)
        # else:
        #     if progress_callback:
        #         cond1 = True
        #     else:
        #         cond1 = False
        #     cond2 = 'fragment_index' in d
        #     cond3 = 'fragment_count' in d
        #     # with open(p, 'a') as f:
        #     #     # f.write(f'2a x={cond1}, y={cond2}, z={cond3}\n')
        #     #     f.write(f'{json.dumps(d)}')

    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',
        'outtmpl': str(output_path),
        'progress_hooks': [progress_hook],
        'merge_output_format': 'mp4',
        'noplaylist': True,
    }

    try:
        # with open(p, 'a') as f:
        #     f.write('xa\n')
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return True
    except Exception as e:
        print(f"Error downloading video: {e}")
        return False
