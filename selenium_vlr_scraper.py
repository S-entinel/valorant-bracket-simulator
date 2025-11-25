from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import json
import time
from datetime import datetime

class ValorantSeleniumScraper:
    def __init__(self):
        """Initialize Selenium WebDriver"""
        print("Setting up Chrome WebDriver...")
        
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.base_url = "https://www.vlr.gg"
        self.teams = []
        
        print("✓ WebDriver initialized\n")
    
    def get_top_teams(self, limit=16):
        """
        Scrape top teams from VLR.gg rankings using Selenium
        """
        print(f"Fetching top {limit} teams from VLR.gg World Rankings...")
        url = f"{self.base_url}/rankings"
        
        try:
            self.driver.get(url)
            print("  → Page loaded, waiting for content...")
            
            # Wait for rankings to load
            wait = WebDriverWait(self.driver, 15)
            time.sleep(3)  # Extra wait for JavaScript
            
            # Find all ranking tables
            tables = self.driver.find_elements(By.CSS_SELECTOR, "table.wf-faux-table.mod-teams")
            print(f"  → Found {len(tables)} ranking tables")
            
            if not tables:
                print("  ✗ No ranking tables found!")
                return []
            
            # Get the World rankings table (first one)
            world_table = tables[0]
            
            # Find all team rows in the table
            team_rows = world_table.find_elements(By.CSS_SELECTOR, "tr.wf-card.mod-hover")
            print(f"  → Found {len(team_rows)} teams in World rankings\n")
            
            for idx, row in enumerate(team_rows[:limit]):
                try:
                    # Extract rank
                    rank_elem = row.find_element(By.CSS_SELECTOR, "td.rank-item-rank a")
                    rank = rank_elem.text.strip()
                    
                    # Extract team name and country
                    team_cell = row.find_element(By.CSS_SELECTOR, "td.rank-item-team")
                    team_link = team_cell.find_element(By.TAG_NAME, "a")
                    
                    # Get team name from div
                    team_name_div = team_link.find_element(By.CSS_SELECTOR, "div")
                    team_name = team_name_div.text.split('\n')[0].strip()
                    
                    # Get region/country
                    try:
                        country_elem = team_link.find_element(By.CSS_SELECTOR, "div.rank-item-team-country")
                        region = country_elem.text.strip()
                    except:
                        region = "Unknown"
                    
                    # Extract team ID from URL
                    team_href = team_link.get_attribute("href")
                    team_id = team_href.split('/team/')[1].split('/')[0] if '/team/' in team_href else str(idx + 1)
                    
                    # Extract VLR rating
                    try:
                        rating_elem = row.find_element(By.CSS_SELECTOR, "td.rank-item-rating a")
                        vlr_rating = rating_elem.text.strip()
                    except:
                        vlr_rating = "1500"
                    
                    # Convert VLR rating to our ELO system
                    # VLR ratings are typically 1500-2000, we'll map to our 1400-1700 range
                    try:
                        vlr_num = int(vlr_rating)
                        # Scale down: VLR 2000 -> 1700, VLR 1500 -> 1400
                        elo_rating = 1400 + ((vlr_num - 1500) * 0.6)
                        elo_rating = round(elo_rating, 1)
                    except:
                        elo_rating = 1500
                    
                    team_data = {
                        'id': team_id,
                        'name': team_name,
                        'rank': rank,
                        'region': region,
                        'vlr_rating': vlr_rating,
                        'elo_rating': elo_rating,
                        'last_updated': datetime.now().isoformat()
                    }
                    
                    self.teams.append(team_data)
                    print(f"  ✓ #{rank}: {team_name:<25} (ELO: {elo_rating}, VLR: {vlr_rating}, {region})")
                    
                except Exception as e:
                    print(f"  ✗ Error parsing row {idx + 1}: {e}")
                    continue
            
            print(f"\n✓ Successfully collected {len(self.teams)} teams")
            return self.teams
            
        except Exception as e:
            print(f"✗ Error during scraping: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def save_data(self, filename='valorant_data_live.json'):
        """Save scraped data to JSON"""
        data = {
            'teams': self.teams,
            'last_updated': datetime.now().isoformat(),
            'metadata': {
                'source': 'VLR.gg (Selenium - World Rankings)',
                'team_count': len(self.teams),
                'note': 'ELO ratings converted from VLR ratings'
            }
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Data saved to {filename}")
    
    def close(self):
        """Close the browser"""
        self.driver.quit()
        print("✓ Browser closed")


def main():
    """Main function"""
    print("="*70)
    print("VALORANT DATA SCRAPER - VLR.gg World Rankings")
    print("="*70)
    print()
    
    scraper = ValorantSeleniumScraper()
    
    try:
        # Get top teams
        teams = scraper.get_top_teams(limit=16)
        
        if not teams:
            print("\n⚠ No teams were scraped.")
            print("Something went wrong with the scraping process.")
            return
        
        # Save data
        scraper.save_data()
        
        print("\n" + "="*70)
        print("SCRAPING COMPLETE!")
        print("="*70)
        print(f"Teams collected: {len(teams)}")
        print("\nTop 5 teams by ELO:")
        for i, team in enumerate(sorted(teams, key=lambda x: x['elo_rating'], reverse=True)[:5], 1):
            print(f"  {i}. {team['name']:<20} - ELO: {team['elo_rating']}")
        
        print("\n✓ You can now use 'valorant_data_live.json' with your simulator!")
        print("  Run: python bracket_simulator.py")
        print("  Then update the filename to 'valorant_data_live.json'")
        
    except Exception as e:
        print(f"\n✗ Fatal error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        scraper.close()


if __name__ == "__main__":
    main()