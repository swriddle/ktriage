from pathlib import Path

# File paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
DOWNLOADS_DIR = DATA_DIR / "downloads"
DATABASE_PATH = DATA_DIR / "songs.csv"
LOG_PATH = DATA_DIR / "activity.log"

# Search settings
FUZZY_MATCH_THRESHOLD = 70  # Minimum confidence score for fuzzy matching

# KaraokeNerds settings
KARAOKENERDS_SEARCH_URL = "https://www.karaokenerds.com/Search"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

# Ensure directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)
