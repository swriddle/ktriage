# Overall Flow

1. **Prompt User for Search**
   - You enter (or paste) a song title or a combination of artist and title
   - *Fuzzy search* is applied to your local CSV database first

2. **Check Local Database**
   - If a match is found above a certain confidence threshold, the tool will mark the song as **locally available**
   - If it's not found (or below threshold), proceed to **karaokenerds.com** search

3. **Search karaokenerds.com**
   - Query: GET https://www.karaokenerds.com/Search?query=<url-encoded-search>
   - Parse the HTML result for the main table
   - For each "song" (in pairs of <tr class="group"> + <tr class="details d-none">), find any version that includes:
     - a link with title="You can watch this version online"
     - that version **is not** labeled "Karaoke Version" if that matters in your usage (based on your description)
   - If found, grab the **YouTube link**

4. **Download from YouTube**
   - If a suitable link is found, automatically run yt-dlp <YouTubeLink>
   - When the download completes, (optionally) add the new track info to your CSV so that next time it counts as *locally available*

5. **Mark as Unavailable**
   - If no suitable link is found (or if you decide not to download), the song is **unavailable**
   - *Log this event* with the user's name and date/time

6. **Display Final Result**
   - For each song requested, the TUI will show one of three statuses: **Local**, **Online + Downloaded**, or **Unavailable**

# Data Structures and Storage

1. **Local CSV**
   - Fields might include: Title, Artist, FilePath, DateDownloaded, Source
   - Use fuzzy search on (Title + Artist) combos
   - E.g. [title.lower(), artist.lower()] concatenated, or stored in a separate "search_field" column for quick matching

2. **Logging**
   - You can maintain a simple CSV log with columns like:

```
requested_by, date_time, title, artist, status
```

   - Append a row each time a song is not found locally
   - You might also log successful downloads or local usage, depending on your needs

# Fuzzy Search Mechanics

- Use a Python library like [RapidFuzz](https://github.com/maxbachmann/RapidFuzz) or [FuzzyWuzzy](https://github.com/seatgeek/fuzzywuzzy) to handle approximate matching
- For each entry in your local CSV:
  - Create a search key: search_key = f"{title.lower()} {artist.lower()}"
  - Compare search_key with the user's query (also in lower case)
  - If your best match (above a threshold, say 70%) is found, return that local track

# Parsing karaokenerds.com

Since there's no official API, you can scrape by:

1. **Requests**
   - Perform a GET to https://www.karaokenerds.com/Search?query=...

2. **HTML Parsing**
   - Use [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) or similar
   - Identify tr.group (the "summary" row) followed by tr.details (the "versions" row)
   - Extract the *song title*, *artist*, and the *list of versions*
   - In each version <li class="track list-group-item ...>, look for:
     - <a href="someYoutubeLink" target="_blank"> (the anchor with title="You can watch this version online")
     - Also read the text (Karaoke Version, Pioneer, Stingray Karaoke, etc.) if you need to skip certain providers

3. **YouTube Link**
   - Once you identify a <span title="You can watch this version online"> link, you'll get the href to YouTube
   - If that version is appropriate (not Karaoke Version, or whichever logic you want), pick that link

# Downloading With yt-dlp

- Call yt-dlp <YouTubeLink> in a subprocess

```python
import subprocess

def download_youtube_video(url, output_path=None):
    cmd = ["yt-dlp", url]
    if output_path:
        cmd.extend(["-o", output_path])
    subprocess.run(cmd, check=True)
```

- After the download finishes:
  - Update your local CSV with the newly downloaded file
  - Keep track of FilePath, DateDownloaded, maybe the version
  - Return a success message to your TUI

# TUI with Textual

- [Textual](https://github.com/Textualize/textual) is a great choice for building a text-based UI in Python:

1. **Start the app** and set up a main screen or "View"
2. **Input box** for the user to type the *artist/title*
3. **Output panel** or log area to show:
   - The matched local file, or
   - The downloaded link, or
   - Unavailable status
4. Possibly implement a mini-menu if you want the user to do something different than the default (e.g., skip auto-download)

# Minimal Example of Structure

```python
# pseudocode / partial example

from textual.app import App
from textual.widgets import Header, Footer, Input, TextLog
from textual.containers import Vertical

class KaraokeTriageApp(App):

    async def on_mount(self):
        self.input_box = Input(placeholder="Enter song title or Artist+Title...")
        self.log = TextLog()
        
        await self.view.dock(Header(), edge="top")
        await self.view.dock(Footer(), edge="bottom")
        await self.view.dock(Vertical(self.input_box, self.log), edge="left")

    async def on_input_submitted(self, message: Input.Submitted):
        query = message.value.strip()
        if not query:
            return

        # 1) fuzzy search in local CSV
        found_local = check_local_database(query)
        if found_local:
            self.log.write(f"Found locally: {found_local}")
        else:
            # 2) Search karaokenerds.com
            yt_link = search_karaokenerds_for_youtube(query)
            if yt_link:
                self.log.write(f"Found online: {yt_link}, downloading...")
                download_success = download_youtube_video(yt_link)
                if download_success:
                    self.log.write("Download complete! Added to local library.")
                else:
                    self.log.write("Download failed.")
            else:
                # 3) Mark unavailable and log
                self.log.write("Song unavailable.")
                log_unavailable(query, user="someone")
        
        # Clear input
        self.input_box.value = ""

def check_local_database(query) -> bool:
    # TODO: fuzzy search logic in CSV
    return False

def search_karaokenerds_for_youtube(query) -> str:
    # TODO: requests + BeautifulSoup to find the YouTube link
    return None

def download_youtube_video(url) -> bool:
    # TODO: run yt-dlp
    return True

def log_unavailable(query, user):
    # TODO: append row to log CSV
    pass

if __name__ == "__main__":
    KaraokeTriageApp.run()
```

This is just a skeleton, but it gives a sense of how to structure your TUI logic with Textual. You'd fill in the pieces for fuzzy search, requests parsing, etc.

# Batch Handling

- You mentioned it's primarily single-entry, but you may want the option for multiple entries
- You could either let the user paste multiple lines, or run the TUI in a loop that re-prompts after each query, as above

# Summary & Next Steps

1. **Set Up Your CSV**
   - Decide on columns and format
   - Decide on the fuzzy search threshold

2. **Implement karaokenerds.com HTML Parser**
   - Use requests + BeautifulSoup
   - Extract the relevant link

3. **Implement the TUI** (Textual)
   - Minimal keystrokes: once the user hits *Enter* after typing, the app goes through the entire pipeline (local check -> online search -> auto-download/log)

4. **Logging & Monitoring**
   - Append to a CSV log with (user, date_time, title, artist, status) each time
   - Potentially add a little reporting function if you want to see the top requested unavailable songs

5. **Packaging**
   - If you want to share it with others, you can distribute it via PyPI or as a simple GitHub repo with instructions
