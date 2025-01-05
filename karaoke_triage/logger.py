import csv
from datetime import datetime
from pathlib import Path
from typing import Optional

from .config import LOG_PATH
from .models import Song, SongStatus

class ActivityLogger:
    def __init__(self, log_path: Path = LOG_PATH):
        self.log_path = log_path
        self._ensure_log_exists()
    
    def _ensure_log_exists(self):
        if not self.log_path.exists():
            with open(self.log_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['timestamp', 'requested_by', 'title', 'artist', 'status'])
    
    def log_activity(self, song: Song, status: SongStatus, requested_by: Optional[str] = None):
        with open(self.log_path, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.now().isoformat(),
                requested_by or 'anonymous',
                song.title,
                song.artist,
                status.value
            ]) 