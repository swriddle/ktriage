from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, List

class SongStatus(Enum):
    LOCAL = "local"
    DOWNLOADED = "downloaded"
    UNAVAILABLE = "unavailable"

@dataclass
class Song:
    title: str
    artist: str
    file_path: Optional[str] = None
    date_downloaded: Optional[datetime] = None
    source: Optional[str] = None
    
@dataclass
class SearchResult:
    song: Song
    status: SongStatus
    youtube_link: Optional[str] = None
    confidence: Optional[float] = None

@dataclass
class KaraokeVersion:
    title: str
    artist: str
    provider: str
    youtube_link: str 