import requests
from bs4 import BeautifulSoup
import sys
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
                tds = group.find_all('td')
                # Extract song metadata from the group row
                title_td, artist_td, details_td = tds
                title = title_td.get_text(strip=True)
                artist = artist_td.get_text(strip=True)
                details = details_td.get_text(strip=True)

                # Find the corresponding details row
                details = group.find_next_sibling('tr', class_='details')
                if not details:
                    continue

                # Find all versions in the details section
                version_items = details.find_all('li', class_='track')
                
                for item in version_items:

                    span = item.find('span', title='You can watch this version online')
                    if not span:
                        # No watchable link, skipping
                        continue

                    link = span.parent

                    if not link:
                        continue
                        
                    href = link.get('href')
                    if not (href and ('youtube.com' in href or 'youtu.be' in href)):
                        continue

                    # Extract provider name
                    provider = "Unknown"
                    provider_elems = item.find_all('span', class_='badge')
                    assert len(provider_elems) == 1
                    provider_elem = provider_elems[0]
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


def search(scraper, query):
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


def main(args):
    """Interactive testing function for KaraokeNerds scraper."""
    scraper = KaraokeNerdsScraper()

    if len(args) > 1:
        query = args[1]
        search(scraper, query)
    else:
        while True:
            query = input("\nEnter search query (or 'q' to quit): ").strip()
            if query.lower() == 'q':
                break

            search(scraper, query)


if __name__ == '__main__':
    main(sys.argv)
