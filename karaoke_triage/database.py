import csv
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from rapidfuzz import fuzz

from .config import DATABASE_PATH
from .models import Song

class SongDatabase:
    def __init__(self, database_path: Path = DATABASE_PATH):
        self.database_path = database_path
        self._ensure_database_exists()
        
    def _ensure_database_exists(self):
        if not self.database_path.exists():
            with open(self.database_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['title', 'artist', 'file_path', 'date_downloaded', 'source'])
    
    def search(self, query: str, threshold: int = 70) -> Optional[Song]:
        query = query.lower()
        best_match = None
        highest_score = 0
        
        with open(self.database_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                search_key = f"{row['title']} {row['artist']}".lower()
                score = fuzz.ratio(query, search_key)
                
                if score > highest_score and score >= threshold:
                    highest_score = score
                    best_match = Song(
                        title=row['title'],
                        artist=row['artist'],
                        file_path=row['file_path'],
                        date_downloaded=datetime.fromisoformat(row['date_downloaded']) if row['date_downloaded'] else None,
                        source=row['source']
                    )
        
        return best_match
    
    def add_song(self, song: Song):
        with open(self.database_path, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                song.title,
                song.artist,
                song.file_path,
                song.date_downloaded.isoformat() if song.date_downloaded else '',
                song.source
            ]) 