from textual.app import App, ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Header, Footer, Input, RichLog, Button, Static
from textual.binding import Binding
from textual.message import Message

from .database import SongDatabase
from .karaokenerds import KaraokeNerdsScraper
from .downloader import download_youtube_video
from .logger import ActivityLogger
from .models import Song, SongStatus, SearchResult, KaraokeVersion
from datetime import datetime

class VersionSelector(Static):
    """A widget to display and select from multiple karaoke versions."""
    
    class VersionSelected(Message):
        """Message sent when a version is selected."""
        def __init__(self, version: KaraokeVersion) -> None:
            self.version = version
            super().__init__()

    def __init__(self, versions: list[KaraokeVersion]) -> None:
        super().__init__()
        self.versions = versions

    def compose(self) -> ComposeResult:
        for i, version in enumerate(self.versions, 1):
            yield Button(
                f"{i}. {version.title} - {version.artist} ({version.provider})", 
                id=f"version_{i-1}"
            )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        version_idx = int(event.button.id.split('_')[1])
        self.post_message(self.VersionSelected(self.versions[version_idx]))

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
    
    RichLog {
        height: 100%;
        border: solid blue;
        background: $surface-darken-1;
    }

    VersionSelector {
        layout: vertical;
        background: $panel;
        height: auto;
        margin: 1;
        padding: 1;
    }

    Button {
        width: 100%;
        margin-bottom: 1;
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
                yield RichLog(id="log", wrap=True)
        yield Footer()
    
    def on_input_submitted(self, event: Input.Submitted) -> None:
        query = event.value.strip()
        if not query:
            return
        
        self.process_query(query)
    
    def process_query(self, query: str) -> None:
        log = self.query_one(RichLog)
        log.write(f"Searching for: {query}")
        
        # Check local database
        local_match = self.database.search(query)
        if local_match:
            log.write("[green]✓ Found locally![/]")
            self.logger.log_activity(local_match, SongStatus.LOCAL)
            return
        
        # Search KaraokeNerds
        log.write("Searching KaraokeNerds...")
        versions = self.scraper.search(query)
        
        if versions:
            log.write(f"[green]✓ Found {len(versions)} versions online![/]")
            log.write("Select a version to download:")
            
            # Remove any existing version selector
            if self.query("VersionSelector"):
                self.query_one(VersionSelector).remove()
            
            # Add the version selector below the log
            selector = VersionSelector(versions)
            self.query_one("#main").mount(selector)
        else:
            log.write("[red]× No versions found online[/]")
            song = Song(title=query, artist="")
            self.logger.log_activity(song, SongStatus.UNAVAILABLE)
    
    def on_version_selector_version_selected(self, message: VersionSelector.VersionSelected) -> None:
        """Handle version selection."""
        log = self.query_one(RichLog)
        version = message.version
        
        log.write(f"Downloading: {version.title} - {version.artist} ({version.provider})")
        
        if download_youtube_video(version.youtube_link):
            song = Song(
                title=version.title,
                artist=version.artist,
                file_path=str(version.youtube_link),
                date_downloaded=datetime.now(),
                source=version.provider
            )
            self.database.add_song(song)
            self.logger.log_activity(song, SongStatus.DOWNLOADED)
            log.write("[green]✓ Download complete![/]")
        else:
            log.write("[red]× Download failed![/]")
        
        # Remove the version selector after download
        self.query_one(VersionSelector).remove() 