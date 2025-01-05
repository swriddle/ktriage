from textual.app import App, ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Header, Footer, Input, TextLog
from textual.binding import Binding

from .database import SongDatabase
from .karaokenerds import KaraokeNerdsScraper
from .downloader import download_youtube_video
from .logger import ActivityLogger
from .models import Song, SongStatus, SearchResult
from datetime import datetime

class KaraokeTriageApp(App):
    CSS = """
    Screen {
        align: center middle;
    }
    
    #main {
        width: 80%;
        height: 80%;
        border: solid green;
        padding: 1;
    }
    
    Input {
        dock: top;
        width: 100%;
    }
    
    TextLog {
        height: 100%;
        border: solid blue;
        background: $surface-darken-1;
    }
    """
    
    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit"),
        Binding("ctrl+c", "quit", "Quit"),
    ]
    
    def __init__(self):
        super().__init__()
        self.database = SongDatabase()
        self.scraper = KaraokeNerdsScraper()
        self.logger = ActivityLogger()
    
    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="main"):
            with Vertical():
                yield Input(placeholder="Enter song title or Artist+Title...", id="search")
                yield TextLog(id="log", wrap=True)
        yield Footer()
    
    def on_input_submitted(self, event: Input.Submitted) -> None:
        query = event.value.strip()
        if not query:
            return
        
        self.process_query(query)
    
    def process_query(self, query: str) -> None:
        log = self.query_one(TextLog)
        log.write(f"Searching for: {query}")
        
        # Check local database
        local_match = self.database.search(query)
        if local_match:
            log.write("[green]✓ Found locally![/]")
            self.logger.log_activity(local_match, SongStatus.LOCAL)
            return
        
        # Search KaraokeNerds
        log.write("Searching KaraokeNerds...")
        youtube_link = self.scraper.search(query)
        
        if youtube_link:
            log.write(f"Found online version: {youtube_link}")
            log.write("Downloading...")
            
            if download_youtube_video(youtube_link):
                song = Song(
                    title=query,  # This is simplified - you might want to parse artist/title
                    artist="",
                    file_path=str(youtube_link),
                    date_downloaded=datetime.now(),
                    source="youtube"
                )
                self.database.add_song(song)
                self.logger.log_activity(song, SongStatus.DOWNLOADED)
                log.write("[green]✓ Download complete![/]")
            else:
                log.write("[red]× Download failed![/]")
        else:
            log.write("[red]× Song unavailable[/]")
            song = Song(title=query, artist="")
            self.logger.log_activity(song, SongStatus.UNAVAILABLE) 