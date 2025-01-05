import requests
from bs4 import BeautifulSoup
from typing import List, Optional
from urllib.parse import quote_plus

from .config import KARAOKENERDS_SEARCH_URL, USER_AGENT
from .models import KaraokeVersion

class KaraokeNerdsScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': USER_AGENT})

    def search(self, query: str) -> List[KaraokeVersion]:
        """Search KaraokeNerds and return all available versions."""
        encoded_query = quote_plus(query)
        url = f"{KARAOKENERDS_SEARCH_URL}?query={encoded_query}"
        versions = []

        try:
            response = self.session.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find all group rows
            group_rows = soup.find_all('tr', class_='group')

            for group in group_rows:
                # Extract song metadata from the group row
                title_elem = group.find('td', class_='song-title')
                artist_elem = group.find('td', class_='song-artist')
                
                if not title_elem or not artist_elem:
                    continue
                
                title = title_elem.get_text(strip=True)
                artist = artist_elem.get_text(strip=True)

                # Find the corresponding details row
                details = group.find_next_sibling('tr', class_='details')
                if not details:
                    continue

                # Find all versions in the details section
                version_items = details.find_all('li', class_='track')
                
                for item in version_items:
                    # Find watchable link
                    link = item.find('a', title="You can watch this version online")
                    if not link:
                        continue
                        
                    href = link.get('href')
                    if not (href and ('youtube.com' in href or 'youtu.be' in href)):
                        continue

                    # Extract provider name
                    provider = "Unknown"
                    provider_elem = item.find('span', class_='version-name')
                    if provider_elem:
                        provider = provider_elem.get_text(strip=True)

                    versions.append(KaraokeVersion(
                        title=title,
                        artist=artist,
                        provider=provider,
                        youtube_link=href
                    ))

            return versions

        except requests.RequestException as e:
            print(f"Error searching KaraokeNerds: {e}")
            return []

def main():
    """Interactive testing function for KaraokeNerds scraper."""
    scraper = KaraokeNerdsScraper()

    while True:
        query = input("\nEnter search query (or 'q' to quit): ").strip()
        if query.lower() == 'q':
            break

        print(f"\nSearching for: {query}")
        results = scraper.search(query)

        if results:
            print(f"\n✓ Found {len(results)} matches!")
            for i, version in enumerate(results, 1):
                print(f"\n{i}. {version.title} - {version.artist}")
                print(f"   Provider: {version.provider}")
                print(f"   YouTube: {version.youtube_link}")
        else:
            print("\n× No matches found")

if __name__ == '__main__':
    main()
