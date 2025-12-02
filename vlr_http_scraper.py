# vlr_http_scraper.py
import json
from datetime import datetime
from typing import List, Dict

import requests
from bs4 import BeautifulSoup


class ValorantHTTPScraper:
    """
    Scraper for VLR.gg world rankings using HTTP + BeautifulSoup.

    """

    BASE_URL = "https://www.vlr.gg"

    def __init__(self) -> None:
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/129.0 Safari/537.36"
                )
            }
        )
        self.teams: List[Dict] = []

    def get_top_teams(self, limit: int = 16) -> List[Dict]:
        """
        Scrape the top `limit` teams from the VLR.gg world rankings page.

        """
        print(f"Fetching top {limit} teams from VLR.gg World Rankings (HTTP)...")
        url = f"{self.BASE_URL}/rankings"

        resp = self.session.get(url, timeout=15)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")

        # There is one table per region with this class
        tables = soup.select("table.wf-faux-table.mod-teams")
        if not tables:
            raise RuntimeError("Could not find any rankings tables on VLR.gg page.")

        print(f"  → Found {len(tables)} regional ranking tables\n")

        self.teams = []
        for table_idx, table in enumerate(tables, start=1):
            rows = table.select("tr.wf-card.mod-hover")
            print(f"  Region table #{table_idx}: {len(rows)} rows")

            for idx, row in enumerate(rows, start=1):
                if len(self.teams) >= limit:
                    print(f"\n✓ Reached requested limit of {limit} teams.")
                    return self.teams

                try:
                    # Rank within region
                    rank_elem = row.select_one("td.rank-item-rank a")
                    rank = rank_elem.get_text(strip=True) if rank_elem else str(idx)

                    # Team cell & link
                    team_cell = row.select_one("td.rank-item-team")
                    team_link = team_cell.select_one("a") if team_cell else None
                    if not team_link:
                        print(
                            f"  ✗ Missing team link at table {table_idx}, row {idx}, skipping"
                        )
                        continue

                    # Team name (first line)
                    name_div = team_link.select_one("div")
                    if name_div:
                        full_text = name_div.get_text("\n", strip=True)
                        team_name = full_text.split("\n")[0].strip()
                    else:
                        team_name = team_link.get_text(strip=True)

                    # Region text
                    region_elem = team_link.select_one("div.rank-item-team-country")
                    region = region_elem.get_text(strip=True) if region_elem else "Unknown"

                    # Team ID from href
                    href = team_link.get("href", "")
                    if "/team/" in href:
                        # e.g. /team/2593/fnatic
                        team_id = href.split("/team/")[1].split("/")[0]
                    else:
                        team_id = f"{table_idx}-{idx}"

                    # VLR rating
                    rating_elem = row.select_one("td.rank-item-rating a")
                    vlr_rating_text = rating_elem.get_text(strip=True) if rating_elem else "1500"

                    try:
                        vlr_num = int(vlr_rating_text)
                        # Simple linear mapping to Elo:
                        # VLR 2000 -> 1700, VLR 1500 -> 1400
                        elo_rating = 1400 + (vlr_num - 1500) * 0.6
                        elo_rating = round(elo_rating, 1)
                    except ValueError:
                        vlr_num = 1500
                        elo_rating = 1500.0

                    team_data = {
                        "id": team_id,
                        "name": team_name,
                        "rank": rank,
                        "region": region,
                        "vlr_rating": str(vlr_num),
                        "elo_rating": elo_rating,
                        "last_updated": datetime.now().isoformat(),
                    }

                    self.teams.append(team_data)
                    print(
                        f"  ✓ [{len(self.teams):>2}/{limit}] "
                        f"#{rank:<3} {team_name:<25} "
                        f"(ELO: {elo_rating:>5}, VLR: {vlr_num}, {region})"
                    )

                except Exception as e:
                    print(
                        f"  ✗ Error parsing table {table_idx}, row {idx}: {e}"
                    )
                    continue

        print(
            f"\n✓ Collected all available teams on page "
            f"({len(self.teams)} total, limit was {limit})"
        )
        return self.teams

    def save_data(self, filename: str = "valorant_data_live.json") -> None:
        """Save scraped data to JSON."""
        data = {
            "teams": self.teams,
            "last_updated": datetime.now().isoformat(),
            "metadata": {
                "source": "VLR.gg (HTTP - World Rankings)",
                "team_count": len(self.teams),
                "note": "ELO ratings converted from VLR ratings",
            },
        }

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"\n✓ Data saved to {filename}")

    def close(self) -> None:
        self.session.close()


def main() -> None:
    print("=" * 70)
    print("VALORANT WORLD RANKINGS SCRAPER (HTTP + BeautifulSoup)")
    print("=" * 70)

    scraper = ValorantHTTPScraper()
    try:
        teams = scraper.get_top_teams(limit=16)

        if not teams:
            print("\n⚠ No teams were scraped. Check if VLR.gg changed layout.")
            return

        scraper.save_data()

        print("\n" + "=" * 70)
        print("SCRAPING COMPLETE (HTTP)!")
        print("=" * 70)
        print(f"Teams collected: {len(teams)}")
        print("\nYou can now run:")
        print("  python run_simulator_live.py")
        print("to simulate with fresh live data.")
    finally:
        scraper.close()


if __name__ == "__main__":
    main()
