"""
API Integration Tests for Valorant Tournament Simulator Backend

Run with: pytest tests/test_api.py -v
"""

import pytest
import sys
import os
from fastapi.testclient import TestClient

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.main import app
from backend.database import Base, engine, SessionLocal
from backend.services.team_service import TeamService

# Test client
client = TestClient(app)


@pytest.fixture(scope="module")
def setup_database():
    """Create test database"""
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Load sample team data
    team_service = TeamService()
    team_service.create_team({
        'id': 'test1',
        'name': 'Test Team Alpha',
        'region': 'Americas',
        'elo_rating': 1700.0,
        'matches_played': 10
    })
    team_service.create_team({
        'id': 'test2',
        'name': 'Test Team Beta',
        'region': 'EMEA',
        'elo_rating': 1650.0,
        'matches_played': 8
    })
    team_service.create_team({
        'id': 'test3',
        'name': 'Test Team Gamma',
        'region': 'Pacific',
        'elo_rating': 1600.0,
        'matches_played': 12
    })
    team_service.create_team({
        'id': 'test4',
        'name': 'Test Team Delta',
        'region': 'Americas',
        'elo_rating': 1550.0,
        'matches_played': 9
    })
    
    yield
    
    # Cleanup
    Base.metadata.drop_all(bind=engine)


class TestHealthCheck:
    """Test basic health check endpoint"""
    
    def test_root_endpoint(self):
        """Should return status information"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "online"
        assert "version" in data


class TestTeamEndpoints:
    """Test team-related endpoints"""
    
    def test_get_all_teams(self, setup_database):
        """Should return list of all teams"""
        response = client.get("/api/teams")
        assert response.status_code == 200
        teams = response.json()
        assert isinstance(teams, list)
        assert len(teams) >= 4
    
    def test_get_teams_with_region_filter(self, setup_database):
        """Should filter teams by region"""
        response = client.get("/api/teams?region=Americas")
        assert response.status_code == 200
        teams = response.json()
        assert all(team["region"] == "Americas" for team in teams)
    
    def test_get_teams_with_rating_filter(self, setup_database):
        """Should filter teams by rating range"""
        response = client.get("/api/teams?min_rating=1600&max_rating=1700")
        assert response.status_code == 200
        teams = response.json()
        assert all(1600 <= team["elo_rating"] <= 1700 for team in teams)
    
    def test_get_teams_with_limit(self, setup_database):
        """Should limit number of results"""
        response = client.get("/api/teams?limit=2")
        assert response.status_code == 200
        teams = response.json()
        assert len(teams) == 2
    
    def test_get_team_by_id(self, setup_database):
        """Should return single team by ID"""
        response = client.get("/api/teams/test1")
        assert response.status_code == 200
        team = response.json()
        assert team["id"] == "test1"
        assert team["name"] == "Test Team Alpha"
    
    def test_get_team_not_found(self, setup_database):
        """Should return 404 for non-existent team"""
        response = client.get("/api/teams/nonexistent")
        assert response.status_code == 404


class TestSimulationEndpoints:
    """Test simulation-related endpoints"""
    
    def test_run_simulation_minimal(self, setup_database):
        """Should run simulation with minimal parameters"""
        response = client.post("/api/simulate", json={
            "team_ids": ["test1", "test2", "test3", "test4"],
            "num_simulations": 100  # Small number for speed
        })
        assert response.status_code == 200
        data = response.json()
        
        assert "simulation_id" in data
        assert data["status"] == "completed"
        assert data["teams_count"] == 4
        assert data["num_simulations"] == 100
        assert "results" in data
        assert len(data["results"]) == 4
    
    def test_run_simulation_full_parameters(self, setup_database):
        """Should run simulation with all parameters"""
        response = client.post("/api/simulate", json={
            "team_ids": ["test1", "test2"],
            "num_simulations": 500,
            "best_of": 5,
            "elo_sigma": 50.0,
            "tournament_format": "single_elimination"
        })
        assert response.status_code == 200
        data = response.json()
        
        assert data["best_of"] == 5
        assert data["elo_sigma"] == 50.0
    
    def test_run_simulation_invalid_team(self, setup_database):
        """Should return 404 for invalid team ID"""
        response = client.post("/api/simulate", json={
            "team_ids": ["test1", "nonexistent"],
            "num_simulations": 100
        })
        assert response.status_code == 404
    
    def test_run_simulation_too_few_teams(self, setup_database):
        """Should reject simulation with too few teams"""
        response = client.post("/api/simulate", json={
            "team_ids": ["test1"],
            "num_simulations": 100
        })
        assert response.status_code == 422  # Validation error
    
    def test_run_simulation_invalid_num_simulations(self, setup_database):
        """Should reject invalid simulation count"""
        response = client.post("/api/simulate", json={
            "team_ids": ["test1", "test2"],
            "num_simulations": 50  # Below minimum
        })
        assert response.status_code == 422
    
    def test_get_simulation_results(self, setup_database):
        """Should retrieve simulation results by ID"""
        # First run a simulation
        create_response = client.post("/api/simulate", json={
            "team_ids": ["test1", "test2"],
            "num_simulations": 100
        })
        simulation_id = create_response.json()["simulation_id"]
        
        # Then retrieve it
        response = client.get(f"/api/simulations/{simulation_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["simulation_id"] == simulation_id
        assert "results" in data
    
    def test_get_simulation_not_found(self, setup_database):
        """Should return 404 for non-existent simulation"""
        response = client.get("/api/simulations/nonexistent-id")
        assert response.status_code == 404
    
    def test_list_simulations(self, setup_database):
        """Should list recent simulations"""
        # Run a couple simulations first
        for _ in range(2):
            client.post("/api/simulate", json={
                "team_ids": ["test1", "test2"],
                "num_simulations": 100
            })
        
        response = client.get("/api/simulations")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2
    
    def test_list_simulations_pagination(self, setup_database):
        """Should support pagination"""
        response = client.get("/api/simulations?limit=1&offset=0")
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 1
    
    def test_delete_simulation(self, setup_database):
        """Should delete a simulation"""
        # Create simulation
        create_response = client.post("/api/simulate", json={
            "team_ids": ["test1", "test2"],
            "num_simulations": 100
        })
        simulation_id = create_response.json()["simulation_id"]
        
        # Delete it
        response = client.delete(f"/api/simulations/{simulation_id}")
        assert response.status_code == 200
        
        # Verify it's deleted
        get_response = client.get(f"/api/simulations/{simulation_id}")
        assert get_response.status_code == 404


class TestStatisticsEndpoints:
    """Test statistics endpoints"""
    
    def test_get_stats_summary(self, setup_database):
        """Should return overall statistics"""
        response = client.get("/api/stats/summary")
        assert response.status_code == 200
        data = response.json()
        
        assert "total_teams" in data
        assert "total_simulations" in data
        assert "avg_elo" in data
        assert "regions" in data
        
        assert data["total_teams"] >= 4
        assert isinstance(data["regions"], dict)


class TestValidation:
    """Test request validation"""
    
    def test_simulation_best_of_validation(self, setup_database):
        """Should validate best_of parameter"""
        response = client.post("/api/simulate", json={
            "team_ids": ["test1", "test2"],
            "num_simulations": 100,
            "best_of": 7  # Invalid, must be 1, 3, or 5
        })
        assert response.status_code == 422
    
    def test_simulation_elo_sigma_validation(self, setup_database):
        """Should validate elo_sigma parameter"""
        response = client.post("/api/simulate", json={
            "team_ids": ["test1", "test2"],
            "num_simulations": 100,
            "elo_sigma": -10  # Invalid, must be >= 0
        })
        assert response.status_code == 422
    
    def test_teams_limit_validation(self, setup_database):
        """Should validate limit parameter"""
        response = client.get("/api/teams?limit=-1")
        assert response.status_code == 422


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])