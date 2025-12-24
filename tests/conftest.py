import pytest
import json
import tempfile
from typing import List, Dict, Any


@pytest.fixture
def sample_teams() -> List[Dict[str, Any]]:
    """Sample team data for testing."""
    return [
        {
            "id": "1",
            "name": "Team Alpha",
            "region": "NA",
            "elo_rating": 1700.0,
            "vlr_rating": "2000",
        },
        {
            "id": "2",
            "name": "Team Beta",
            "region": "EU",
            "elo_rating": 1650.0,
            "vlr_rating": "1900",
        },
        {
            "id": "3",
            "name": "Team Gamma",
            "region": "APAC",
            "elo_rating": 1680.0,
            "vlr_rating": "1950",
        },
        {
            "id": "4",
            "name": "Team Delta",
            "region": "NA",
            "elo_rating": 1620.0,
            "vlr_rating": "1850",
        },
    ]


@pytest.fixture
def sample_teams_file(sample_teams, tmp_path) -> str:
    """Create temporary JSON file with sample teams."""
    teams_data = {
        "teams": sample_teams,
        "last_updated": "2024-01-01T00:00:00",
        "metadata": {
            "source": "test_data",
            "team_count": len(sample_teams),
        },
    }
    
    teams_file = tmp_path / "test_teams.json"
    with open(teams_file, "w") as f:
        json.dump(teams_data, f)
    
    return str(teams_file)


@pytest.fixture
def eight_team_bracket() -> List[Dict[str, Any]]:
    """8-team bracket for tournament testing."""
    return [
        {"id": str(i), "name": f"Team {i}", "elo_rating": 1700 - (i * 10)}
        for i in range(1, 9)
    ]


@pytest.fixture
def historical_teams() -> List[Dict[str, Any]]:
    """VCT Champions 2024 teams for validation testing."""
    return [
        {"id": "edg", "name": "EDward Gaming", "seed": 1, "elo_rating": 1720.0},
        {"id": "heretics", "name": "Team Heretics", "seed": 2, "elo_rating": 1710.0},
        {"id": "leviatan", "name": "LEVIATÁN", "seed": 3, "elo_rating": 1695.0},
        {"id": "sentinels", "name": "Sentinels", "seed": 4, "elo_rating": 1680.0},
        {"id": "drx", "name": "DRX", "seed": 5, "elo_rating": 1660.0},
        {"id": "fnatic", "name": "FNATIC", "seed": 6, "elo_rating": 1650.0},
        {"id": "trace", "name": "Trace Esports", "seed": 7, "elo_rating": 1620.0},
        {"id": "g2", "name": "G2 Esports", "seed": 8, "elo_rating": 1615.0},
    ]