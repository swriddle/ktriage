from textual.app import App, ComposeResult
from textual.containers import Container, Vertical, ScrollableContainer
from textual.widgets import Header, Footer, Input, RichLog, Button, Static, ProgressBar, Label
from textual.binding import Binding
from textual.message import Message
from textual.scroll_view import ScrollView
from textual.screen import ModalScreen
from textual import work
from functools import partial

from .database import SongDatabase
from .karaokenerds import KaraokeNerdsScraper
from .downloader import download_youtube_video
from .logger import ActivityLogger
from .models import Song, SongStatus, SearchResult, KaraokeVersion
from datetime import datetime
import os
import pathlib

class VersionSelector(ScrollableContainer):
    """A scrollable widget to display and select from multiple karaoke versions."""
    
    class VersionSelected(Message):
        """Message sent when a version is selected."""
        def __init__(self, version: KaraokeVersion) -> None:
            self.version = version
            super().__init__()

    BINDINGS = [
        Binding("j", "scroll_down", "Scroll Down", show=False),
        Binding("k", "scroll_up", "Scroll Up", show=False),
        Binding("g", "scroll_home", "Scroll to Top", show=False),
        Binding("G", "scroll_end", "Scroll to Bottom", show=False),
    ]

    def __init__(self, versions: list[KaraokeVersion]) -> None:
        super().__init__()
        self.versions = versions
        self.current_focus = 0

    def compose(self) -> ComposeResult:
        """Create buttons for each version."""
        for i, version in enumerate(self.versions, 1):
            yield Button(
                f"{i}. {version.title} - {version.artist} ({version.provider})", 
                id=f"version_{i-1}",
                classes="version-button"
            )

    def on_mount(self) -> None:
        """Focus the first button when mounted."""
        if self.versions:
            first_button = self.query_one(f"#version_0")
            first_button.focus()

    def action_scroll_down(self) -> None:
        """Handle j key: move focus down one item."""
        if self.current_focus < len(self.versions) - 1:
            self.current_focus += 1
            self.query_one(f"#version_{self.current_focus}").focus()

    def action_scroll_up(self) -> None:
        """Handle k key: move focus up one item."""
        if self.current_focus > 0:
            self.current_focus -= 1
            self.query_one(f"#version_{self.current_focus}").focus()

    def action_scroll_home(self) -> None:
        """Handle g key: scroll to top."""
        self.current_focus = 0
        self.query_one("#version_0").focus()
        self.scroll_home(animate=False)

    def action_scroll_end(self) -> None:
        """Handle G key: scroll to bottom."""
        self.current_focus = len(self.versions) - 1
        self.query_one(f"#version_{self.current_focus}").focus()
        self.scroll_end(animate=False)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        version_idx = int(event.button.id.split('_')[1])
        self.post_message(self.VersionSelected(self.versions[version_idx]))

class DownloadProgress(ModalScreen):
    """A modal screen showing download progress."""

    def __init__(self, version: KaraokeVersion):
        super().__init__()
        self.version = version
        self.progress = 0

    def compose(self) -> ComposeResult:
        yield Container(
            Label(f"Downloading: {self.version.title} - {self.version.artist}"),
            Label("", id="progress_text"),
            ProgressBar(total=100, show_percentage=True, id="progress_bar"),
            classes="download_modal"
        )

    def update_progress(self, fragment_index: int, fragment_count: int) -> None:
        """Update the progress bar and text."""
        if fragment_count > 0:
            percentage = min(100, int((fragment_index / fragment_count) * 100))
            self.query_one("#progress_bar").update(progress=percentage)
            self.query_one("#progress_text").update(f"Fragment {fragment_index} of {fragment_count}")

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
        height: 60%;
        border: solid blue;
        background: $surface-darken-1;
    }

    VersionSelector {
        width: 100%;
        height: 40%;
        background: $panel;
        border: solid $primary;
        overflow-y: scroll;
        padding: 0;
    }

    Button {
        width: 100%;
        margin: 0;
        padding: 0;
        border: none;
        height: 1;
    }

    Button:focus {
        background: $accent;
        color: $text;
    }

    .version-button {
        text-align: left;
    }

    .download_modal {
        background: $surface;
        border: solid $primary;
        padding: 1;
        margin: 1;
        width: 80%;
        min-height: 10;
        height: auto;
        align: center middle;
    }

    DownloadProgress {
        align: center middle;
        width: 100%;
    }

    DownloadProgress Label {
        content-align: center middle;
        width: 100%;
        margin-bottom: 1;
    }

    DownloadProgress ProgressBar {
        width: 100%;
        margin: 1 2;
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
        self.download_progress = None

    @work(thread=True)
    def download_version(self, version: KaraokeVersion) -> bool:
        """Download the version in a separate thread."""
        p = pathlib.Path(os.path.expanduser('~/x3.txt'))
        def progress_callback(progress_data: dict) -> None:
            """Callback for download progress updates."""
            if self.download_progress and 'downloaded_bytes' in progress_data and 'total_bytes' in progress_data:
                with open(p, 'a') as f:
                    f.write('1\n')
                self.call_from_thread(
                    self.download_progress.update_progress,
                    progress_data['downloaded_bytes'],
                    progress_data['total_bytes']
                )
            else:
                with open(p, 'a') as f:
                    f.write('2\n')

        with open(p, 'a') as f:
            f.write('pre-download_youtube_video\n')
        success = download_youtube_video(version.youtube_link, progress_callback=progress_callback)
        with open(p, 'a') as f:
            f.write('post-download_youtube_video\n')

        with open(p, 'a') as f:
            f.write('about to close modal\n')
        # Close the modal after download completes
        if self.download_progress:
            with open(p, 'a') as f:
                f.write('closing the shit window\n')
            self.call_from_thread(self.pop_screen)
            self.download_progress = None
        else:
            with open(p, 'a') as f:
                f.write('who gives a flying fuck\n')

        return success

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
            log.write("Select a version to download (j/k to navigate, Enter to select):")
            
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
        path = pathlib.Path(os.path.expanduser('~/x317.txt'))
        log = self.query_one(RichLog)
        version = message.version
        
        log.write(f"Downloading: {version.title} - {version.artist} ({version.provider})")
        with open(path, 'a') as f:
            f.write(f'on_version_selector_version_selected downloading! link={version.youtube_link}\n')

        # Show download progress modal
        self.download_progress = DownloadProgress(version)
        self.push_screen(self.download_progress)
        
        # Start download in background
        def download_complete(worker) -> None:
            success = worker.result
            
            if success:
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
            
            # Just remove the version selector since modal is already closed
            self.query_one(VersionSelector).remove()
            self.download_progress = None
        
        worker = self.download_version(version)
        worker.callback = download_complete
