"""
Scraper for extracting deep metadata (credits) from Apple Music web pages.
Implements the "Deep Mining" strategy described in the research.
"""
import httpx
from bs4 import BeautifulSoup
import logging
import time
import random
import re
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class CreditsScraper:
    """
    Scrapes Apple Music web pages to extract credits not available in the public API.
    """
    
    BASE_URL = "https://music.apple.com"
    
    # Rate limiting configuration
    MIN_DELAY = 5.0  # seconds
    MAX_DELAY = 10.0 # seconds
    
    def __init__(self):
        self.last_request_time = 0
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }
        
    def _wait_for_rate_limit(self):
        """Enforce rate limiting to avoid IP bans."""
        current_time = time.time()
        elapsed = current_time - self.last_request_time
        
        if elapsed < self.MIN_DELAY:
            delay = self.MIN_DELAY - elapsed + random.uniform(0, self.MAX_DELAY - self.MIN_DELAY)
            logger.debug(f"Rate limiting: sleeping for {delay:.2f}s")
            time.sleep(delay)
            
        self.last_request_time = time.time()
        
    def fetch_credits(self, track_url: str) -> List[Dict]:
        """
        Fetch credits for a track from its Apple Music web URL.
        
        Args:
            track_url: Full URL to the track page (e.g., https://music.apple.com/us/song/name/id)
            
        Returns:
            List of credit dictionaries with 'name', 'role', and 'slug' (if available)
        """
        self._wait_for_rate_limit()
        
        try:
            logger.info(f"Scraping credits from: {track_url}")
            response = httpx.get(track_url, headers=self.headers, follow_redirects=True, timeout=10.0)
            response.raise_for_status()
            
            return self._parse_credits(response.text)
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP error scraping {track_url}: {e}")
            return []
        except Exception as e:
            logger.error(f"Error scraping {track_url}: {e}")
            return []
            
    def _parse_credits(self, html_content: str) -> List[Dict]:
        """
        Parse HTML content to extract credit information.
        """
        credits = []
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Apple Music web structure for credits is often in a specific section
        # Look for the credits container
        # Note: parsing logic depends on current Apple Music DOM structure which may change
        
        # Strategy 1: Look for JSON data embedded in the page (most reliable)
        # Often found in a script tag with ID dealing with "shoebox" or "server-data"
        scripts = soup.find_all('script', type='application/json')
        for script in scripts:
            if not script.string:
                continue
                
            # Naive text search for credits patterns within JSON if structured parsing is complex
            # "role":"Immersive Mix Engineer","name":"Steven Wilson"
            # This is a fallback heuristic if full JSON parsing structure is unknown
            pass
            
        # Strategy 2: DOM Parsing
        # Look for elements with class names related to credits
        # This is fragile but necessary as fallback
        
        # Targeted Roles for Spatial Audio
        target_roles = [
            "Immersive Mix Engineer", "Dolby Atmos Mixer", "Surround Mix Engineer", 
            "Mix Engineer", "Mastering Engineer"
        ]
        
        # Find all text that matches roles
        # This is a simplified scraper. A real production one would need robust selectors or Playwright.
        text_content = soup.get_text()
        
        # Simple Regex extraction (prototype)
        # Pattern: Role Name (e.g. "Immersive Mix Engineer: Steven Wilson")
        for role in target_roles:
            # Flexible pattern
            pattern = re.compile(f"{role}\\s*[:|-]?\\s*([A-Z][a-zA-Z0-9\\s\\.]+)", re.IGNORECASE)
            matches = pattern.findall(text_content)
            
            for name in matches:
                name = name.strip()
                if len(name) > 2 and len(name) < 50: # Sanity check
                    credits.append({
                        "role": role,
                        "name": name,
                        "slug": name.lower().replace(" ", "-") # simplistic slug
                    })
                    
        # Remove duplicates
        unique_credits = []
        seen = set()
        for c in credits:
            key = f"{c['name']}:{c['role']}"
            if key not in seen:
                seen.add(key)
                unique_credits.append(c)
                
        return unique_credits

