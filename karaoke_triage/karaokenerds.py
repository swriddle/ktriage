import requests
from bs4 import BeautifulSoup
from typing import Optional
from urllib.parse import quote_plus

from .config import KARAOKENERDS_SEARCH_URL, USER_AGENT

class KaraokeNerdsScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': USER_AGENT})
    
    def search(self, query: str) -> Optional[str]:
        """Search KaraokeNerds and return first valid YouTube link."""
        encoded_query = quote_plus(query)
        url = f"{KARAOKENERDS_SEARCH_URL}?query={encoded_query}"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all group rows
            group_rows = soup.find_all('tr', class_='group')
            
            for group in group_rows:
                # Find the corresponding details row
                details = group.find_next_sibling('tr', class_='details')
                if not details:
                    continue
                
                # Find watchable versions
                watchable_links = details.find_all('a', title="You can watch this version online")
                
                for link in watchable_links:
                    # Skip if it's labeled as "Karaoke Version"
                    if "Karaoke Version" not in link.get_text():
                        href = link.get('href')
                        if 'youtube.com' in href or 'youtu.be' in href:
                            return href
            
            return None
            
        except requests.RequestException as e:
            print(f"Error searching KaraokeNerds: {e}")
            return None 