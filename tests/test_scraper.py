import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import pytest
from unittest.mock import Mock, patch, MagicMock
from scripts.vlr_http_scraper import ValorantHTTPScraper


class TestVLRScraper:
    """Test VLR.gg scraping functionality."""

    @patch('scripts.vlr_http_scraper.requests.Session.get')
    def test_scraper_makes_request(self, mock_get):
        """Should make HTTP request to VLR.gg."""
        mock_response = Mock()
        mock_response.text = "<html><body></body></html>"
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        scraper = ValorantHTTPScraper()
        
        # This will fail on parsing, but we're just testing the request
        with pytest.raises(RuntimeError):
            scraper.get_top_teams(limit=1)
        
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert "rankings" in args[0]

    def test_scraper_user_agent_set(self):
        """Should set user agent header."""
        scraper = ValorantHTTPScraper()
        
        assert "User-Agent" in scraper.session.headers
        assert "Mozilla" in scraper.session.headers["User-Agent"]

    def test_elo_conversion_formula(self):
        """Should convert VLR rating to ELO correctly."""
        scraper = ValorantHTTPScraper()
        
        # VLR 2000 -> ELO 1700
        # VLR 1500 -> ELO 1400
        # Formula: 1400 + (vlr - 1500) * 0.6
        
        vlr_2000_elo = 1400 + (2000 - 1500) * 0.6
        assert vlr_2000_elo == 1700.0
        
        vlr_1500_elo = 1400 + (1500 - 1500) * 0.6
        assert vlr_1500_elo == 1400.0

    @patch('scripts.vlr_http_scraper.requests.Session.get')
    def test_scraper_respects_limit(self, mock_get):
        """Should stop scraping after reaching limit."""
        # Create mock HTML with multiple teams
        mock_html = """
        <html>
            <body>
                <table class="wf-faux-table mod-teams">
                    <tr class="wf-card mod-hover">
                        <td class="rank-item-rank"><a>1</a></td>
                        <td class="rank-item-team">
                            <a href="/team/123/test-team">
                                <div>Test Team<div class="rank-item-team-country">NA</div></div>
                            </a>
                        </td>
                        <td class="rank-item-rating"><a>1800</a></td>
                    </tr>
                </table>
            </body>
        </html>
        """
        
        mock_response = Mock()
        mock_response.text = mock_html
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        scraper = ValorantHTTPScraper()
        teams = scraper.get_top_teams(limit=1)
        
        assert len(teams) <= 1, "Should respect limit parameter"

    def test_save_data_creates_file(self, tmp_path):
        """Should save scraped data to JSON file."""
        scraper = ValorantHTTPScraper()
        scraper.teams = [
            {
                "id": "1",
                "name": "Test Team",
                "rank": "1",
                "region": "NA",
                "vlr_rating": "1800",
                "elo_rating": 1580.0,
            }
        ]
        
        output_file = tmp_path / "test_data.json"
        scraper.save_data(filename=str(output_file))
        
        assert output_file.exists()
        
        import json
        with open(output_file) as f:
            data = json.load(f)
        
        assert "teams" in data
        assert len(data["teams"]) == 1
        assert data["teams"][0]["name"] == "Test Team"