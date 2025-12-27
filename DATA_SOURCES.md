# Data Sources

## VCT Matches Dataset

**Total Matches:** 165  
**Source:** VLR.gg (https://www.vlr.gg/)  
**Last Updated:** December 2024

### Tournament Breakdown:
- **VCT 2024 China Stage 1:** 38 matches (April-May 2024)
- **VCT 2024 Americas Stage 1:** 38 matches (April-May 2024)  
- **VCT 2024 Masters Madrid:** 17 matches (March 2024)
- **VCT 2024 Masters Shanghai:** 38 matches (May-June 2024)
- **VCT 2024 Champions:** 34 matches (August 2024)

### Collection Method:
Data scraped using `vct_match_scraper.py` from VLR.gg match pages.

### To Refresh Data:
```bash
python vct_match_scraper.py
```

### Data Format:
Stored in `vct_matches_2024.json` with structure:
```json
{
  "matches": [
    {
      "team_a": "Team Name",
      "team_b": "Team Name", 
      "score_a": 2,
      "score_b": 1,
      "event": "Tournament Name",
      "round": "Round Name"
    }
  ],
  "metadata": {
    "total_matches": 165,
    "scraped_at": "timestamp",
    "source": "vlr.gg"
  }
}
```
