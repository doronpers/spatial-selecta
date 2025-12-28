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
import json
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
        Uses multiple strategies with fallbacks for robustness.
        """
        credits = []
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
        except Exception as e:
            logger.error(f"Error parsing HTML content: {e}")
            return []
        
        # Strategy 1: Look for JSON data embedded in the page (most reliable)
        # Often found in a script tag with ID dealing with "shoebox" or "server-data"
        try:
            scripts = soup.find_all('script', type='application/json')
            for script in scripts:
                try:
                    data = json.loads(script.string)
                    # Look for credits in nested JSON structure
                    # This is a placeholder - actual structure depends on Apple Music's current implementation
                    if isinstance(data, dict):
                        # Try common paths for credits data
                        if 'credits' in data:
                            credits.extend(self._extract_credits_from_json(data['credits']))
                except (json.JSONDecodeError, AttributeError):
                    continue
        except Exception as e:
            logger.debug(f"Strategy 1 (JSON parsing) failed: {e}")
        
        # Strategy 2: DOM Parsing (fallback)
        # Look for elements with class names related to credits
        try:
            # Common selectors for credits sections
            credit_selectors = [
                '[class*="credit"]',
                '[class*="contributor"]',
                '[data-testid*="credit"]',
                '.credits',
                '.contributors'
            ]
            
            for selector in credit_selectors:
                elements = soup.select(selector)
                for elem in elements:
                    text = elem.get_text(strip=True)
                    if text:
                        parsed = self._parse_credit_text(text)
                        if parsed:
                            credits.extend(parsed)
        except Exception as e:
            logger.debug(f"Strategy 2 (DOM parsing) failed: {e}")
        
        # Strategy 3: Regex-based text extraction (last resort)
        if not credits:
            try:
                text_content = soup.get_text()
                credits = self._extract_credits_from_text(text_content)
            except Exception as e:
                logger.debug(f"Strategy 3 (regex extraction) failed: {e}")
        
        # Remove duplicates and validate
        unique_credits = []
        seen = set()
        for c in credits:
            if not isinstance(c, dict) or 'name' not in c or 'role' not in c:
                continue
            key = f"{c['name'].lower()}:{c['role'].lower()}"
            if key not in seen:
                seen.add(key)
                # Validate credit data
                if 2 < len(c['name']) < 100 and len(c['role']) < 100:
                    unique_credits.append(c)
        
        return unique_credits
    
    def _extract_credits_from_json(self, json_data) -> List[Dict]:
        """Extract credits from JSON structure."""
        credits = []
        # Placeholder for JSON-based extraction
        # Implementation depends on actual Apple Music JSON structure
        return credits
    
    def _parse_credit_text(self, text: str) -> List[Dict]:
        """Parse credit information from text content."""
        credits = []
        target_roles = [
            "Immersive Mix Engineer", "Dolby Atmos Mixer", "Surround Mix Engineer", 
            "Mix Engineer", "Mastering Engineer", "Engineer", "Producer"
        ]
        
        for role in target_roles:
            pattern = re.compile(f"{re.escape(role)}\\s*[:|-]?\\s*([A-Z][a-zA-Z0-9\\s\\.]+)", re.IGNORECASE)
            matches = pattern.findall(text)
            for name in matches:
                name = name.strip()
                if 2 < len(name) < 50:
                    credits.append({
                        "role": role,
                        "name": name,
                        "slug": name.lower().replace(" ", "-").replace(".", "")
                    })
        return credits
    
    def _extract_credits_from_text(self, text_content: str) -> List[Dict]:
        """Extract credits using regex patterns on full text."""
        return self._parse_credit_text(text_content)

