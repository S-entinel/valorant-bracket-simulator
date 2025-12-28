#!/usr/bin/env python3
"""
VCT Match Scraper - Collects 500+ matches from all 2024 leagues

Run this to get 20+ matches per team:
    python scripts/vct_match_scraper_extended.py
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
        
        print(f"  ✓ Found {len(matches)} completed matches")
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
        delay: float = 2.0
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
        
        for i, event in enumerate(events, 1):
            print(f"\n[{i}/{len(events)}] ", end="")
            matches = self.scrape_event_matches(
                event_id=event["id"],
                event_name=event.get("name", "")
            )
            all_matches.extend(matches)
            
            # Be nice to the server
            if i < len(events):
                print(f"  Waiting {delay}s before next request...")
                time.sleep(delay)
        
        return all_matches
    
    def save_matches(
        self,
        filename: str = "data/vct_matches_2024.json"
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
            json.dump(output, f, indent=2, ensure_ascii=False)
        
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
        
        # Count matches per team
        team_matches = {}
        for match in self.matches:
            team_matches[match["team_a"]] = team_matches.get(match["team_a"], 0) + 1
            team_matches[match["team_b"]] = team_matches.get(match["team_b"], 0) + 1
        
        teams_with_20_plus = sum(1 for count in team_matches.values() if count >= 20)
        
        print("\n" + "=" * 70)
        print(" " * 25 + "SCRAPING SUMMARY")
        print("=" * 70)
        print(f"Total Matches: {len(self.matches)}")
        print(f"Unique Teams: {len(teams)}")
        print(f"Events Covered: {len(events)}")
        print(f"Teams with 20+ matches: {teams_with_20_plus}/{len(teams)}")
        print("=" * 70)
        
        # Top 10 teams by match count
        print("\nTop 10 Teams by Match Count:")
        print("-" * 70)
        sorted_teams = sorted(team_matches.items(), key=lambda x: x[1], reverse=True)[:10]
        for i, (team, count) in enumerate(sorted_teams, 1):
            print(f"  {i:2}. {team:<30} {count:3} matches")
        print("=" * 70)


# VCT 2024 Events - EXTENDED LIST with Regional Leagues
VCT_2024_EVENTS_EXTENDED = [
    # International Tournaments (165 matches currently)
    {"id": "2097", "name": "VCT 2024: Champions"},
    {"id": "1998", "name": "VCT 2024: Masters Shanghai"},
    {"id": "1921", "name": "VCT 2024: Masters Madrid"},
    
    # Americas League
    {"id": "2094", "name": "VCT 2024: Americas Stage 2"},
    {"id": "1922", "name": "VCT 2024: Americas Stage 1"},
    {"id": "1923", "name": "VCT 2024: Americas Kickoff"},
    
    # EMEA League
    {"id": "2095", "name": "VCT 2024: EMEA Stage 2"},
    {"id": "1924", "name": "VCT 2024: EMEA Stage 1"},
    {"id": "1925", "name": "VCT 2024: EMEA Kickoff"},
    
    # Pacific League
    {"id": "2096", "name": "VCT 2024: Pacific Stage 2"},
    {"id": "1926", "name": "VCT 2024: Pacific Stage 1"},
    {"id": "1927", "name": "VCT 2024: Pacific Kickoff"},
    
    # China League
    {"id": "2093", "name": "VCT 2024: China Stage 2"},
    {"id": "1928", "name": "VCT 2024: China Stage 1"},
    {"id": "1929", "name": "VCT 2024: China Kickoff"},
]


def main():
    """Scrape VCT 2024 matches including all regional leagues."""
    
    print("\n" + "=" * 70)
    print(" " * 20 + "VCT MATCH SCRAPER - EXTENDED")
    print("=" * 70)
    print("\nThis will scrape ALL VCT 2024 matches including:")
    print("  • International Tournaments (Champions, Masters)")
    print("  • Regional Leagues (Americas, EMEA, Pacific, China)")
    print("  • Estimated total: 500-800 matches")
    print("\nThis may take 5-10 minutes. Please be patient...")
    print("=" * 70)
    
    scraper = VCTMatchScraper()
    
    # Scrape all events
    scraper.scrape_multiple_events(VCT_2024_EVENTS_EXTENDED, delay=2.0)
    
    # Show summary
    scraper.print_summary()
    
    # Save to file
    scraper.save_matches("data/vct_matches_2024.json")
    
    print("\n✅ DONE! Next steps:")
    print("  1. Regenerate ELO: python scripts/calculate_elo_ratings.py data/vct_matches_2024.json")
    print("  2. Delete database: rm valorant_simulator.db")
    print("  3. Restart backend: python run_backend.py")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()