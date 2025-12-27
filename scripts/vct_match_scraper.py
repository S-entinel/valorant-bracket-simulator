# vct_match_scraper.py
"""
Scraper for VCT (Valorant Champions Tour) match history from VLR.gg

This scrapes actual match results to feed into the ELO calculator,
replacing manual rating estimates with data-driven calculations.
"""

import requests
from bs4 import BeautifulSoup
import json
import time
from typing import List, Dict, Optional
from datetime import datetime


class VCTMatchScraper:
    """Scrape VCT match results from VLR.gg"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                         'AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/120.0.0.0 Safari/537.36'
        })
        self.matches: List[Dict] = []
    
    def scrape_event_matches(
        self,
        event_id: str,
        event_name: str = ""
    ) -> List[Dict]:
        """
        Scrape all matches from a specific VCT event.
        
        Args:
            event_id: VLR.gg event ID (e.g., "2097" for Champions 2024)
            event_name: Human-readable event name
            
        Returns:
            List of match dictionaries
        """
        url = f"https://www.vlr.gg/event/matches/{event_id}/"
        
        print(f"Scraping {event_name or f'Event {event_id}'}...")
        print(f"URL: {url}")
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Error fetching data: {e}")
            return []
        
        soup = BeautifulSoup(response.text, 'html.parser')
        matches = []
        
        # Find all match cards
        match_cards = soup.find_all('a', class_='wf-module-item')
        
        for card in match_cards:
            try:
                match_data = self._parse_match_card(card, event_name)
                if match_data:
                    matches.append(match_data)
            except Exception as e:
                print(f"Error parsing match: {e}")
                continue
        
        print(f"Found {len(matches)} completed matches")
        self.matches.extend(matches)
        
        return matches
    
    def _parse_match_card(
        self,
        card,
        event_name: str
    ) -> Optional[Dict]:
        """Parse individual match card from HTML."""
        
        # Get teams
        teams = card.find_all('div', class_='match-item-vs-team-name')
        if len(teams) != 2:
            return None
        
        team_a = teams[0].text.strip()
        team_b = teams[1].text.strip()
        
        # Get scores
        scores = card.find_all('div', class_='match-item-vs-team-score')
        if len(scores) != 2:
            return None  # Match not completed yet
        
        try:
            score_a = int(scores[0].text.strip())
            score_b = int(scores[1].text.strip())
        except (ValueError, AttributeError):
            return None  # Match not completed
        
        # Get match date/round (optional)
        round_info = card.find('div', class_='match-item-event-series')
        round_name = round_info.text.strip() if round_info else "Unknown"
        
        return {
            "team_a": team_a,
            "team_b": team_b,
            "score_a": score_a,
            "score_b": score_b,
            "event": event_name,
            "round": round_name,
        }
    
    def scrape_multiple_events(
        self,
        events: List[Dict[str, str]],
        delay: float = 1.0
    ) -> List[Dict]:
        """
        Scrape matches from multiple VCT events.
        
        Args:
            events: List of {"id": "2097", "name": "Champions 2024"}
            delay: Seconds to wait between requests (be nice to servers)
            
        Returns:
            Combined list of all matches
        """
        all_matches = []
        
        for event in events:
            matches = self.scrape_event_matches(
                event_id=event["id"],
                event_name=event.get("name", "")
            )
            all_matches.extend(matches)
            
            # Be nice to the server
            time.sleep(delay)
        
        return all_matches
    
    def save_matches(
        self,
        filename: str = "vct_matches_2024.json"
    ) -> None:
        """Save scraped matches to JSON file."""
        
        output = {
            "matches": self.matches,
            "metadata": {
                "total_matches": len(self.matches),
                "scraped_at": datetime.now().isoformat(),
                "source": "vlr.gg"
            }
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2)
        
        print(f"\n✓ Saved {len(self.matches)} matches to {filename}")
    
    def print_summary(self) -> None:
        """Print summary of scraped matches."""
        if not self.matches:
            print("No matches scraped yet")
            return
        
        # Count teams
        teams = set()
        for match in self.matches:
            teams.add(match["team_a"])
            teams.add(match["team_b"])
        
        # Count events
        events = set(match["event"] for match in self.matches)
        
        print("\n" + "=" * 60)
        print("MATCH SCRAPING SUMMARY")
        print("=" * 60)
        print(f"Total Matches: {len(self.matches)}")
        print(f"Unique Teams: {len(teams)}")
        print(f"Events Covered: {len(events)}")
        print("=" * 60)


# VCT 2024 Event IDs (major international tournaments)
VCT_2024_EVENTS = [
    {"id": "2097", "name": "VCT 2024: Champions"},
    {"id": "1998", "name": "VCT 2024: Masters Shanghai"},
    {"id": "1921", "name": "VCT 2024: Masters Madrid"},
    # Add more regional leagues if needed:
    # {"id": "XXXX", "name": "VCT Americas 2024"},
    # {"id": "XXXX", "name": "VCT EMEA 2024"},
    # {"id": "XXXX", "name": "VCT Pacific 2024"},
]


def main():
    """Scrape VCT 2024 matches and save to file."""
    
    print("\n" + "=" * 70)
    print(" " * 20 + "VCT MATCH SCRAPER")
    print("=" * 70)
    
    scraper = VCTMatchScraper()
    
    # Scrape major 2024 tournaments
    print("\nScraping VCT 2024 international tournaments...")
    scraper.scrape_multiple_events(VCT_2024_EVENTS, delay=1.5)
    
    # Print summary
    scraper.print_summary()
    
    # Save to file
    scraper.save_matches("vct_matches_2024.json")
    
    print("\n" + "=" * 70)
    print("Next step: Run ELO calculator with this match data")
    print("  python -c 'from elo_calculator import ELOCalculator; "
          "calc = ELOCalculator(); calc.load_from_file(\"vct_matches_2024.json\"); "
          "calc.print_ratings(); calc.save_ratings()'")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()