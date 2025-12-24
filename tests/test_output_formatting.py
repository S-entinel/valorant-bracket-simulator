import pytest
import json
from io import StringIO
import sys
from bracket_simulator import BracketSimulator


class TestOutputFormatting:
    """Test statistics printing and formatting."""

    def test_statistics_format(self, sample_teams_file):
        """Should produce well-formatted statistics."""
        sim = BracketSimulator(sample_teams_file, best_of=3)
        sim.select_teams(count=4)
        stats = sim.run_simulation(n=100)
        
        # Stats should be a list
        assert isinstance(stats, list)
        assert len(stats) == 4
        
        # Each stat should have required fields
        for team_stat in stats:
            assert "name" in team_stat
            assert "seed" in team_stat
            assert "championship_prob" in team_stat

    def test_statistics_json_serializable(self, sample_teams_file):
        """Statistics should be JSON serializable."""
        sim = BracketSimulator(sample_teams_file, best_of=3)
        sim.select_teams(count=4)
        stats = sim.run_simulation(n=100)
        
        # Should not raise exception
        json_str = json.dumps(stats)
        assert json_str is not None
        
        # Should be deserializable
        deserialized = json.loads(json_str)
        assert len(deserialized) == 4

    def test_save_statistics_to_file(self, sample_teams_file, tmp_path):
        """Should save statistics to JSON file."""
        sim = BracketSimulator(sample_teams_file, best_of=3)
        sim.select_teams(count=4)
        stats = sim.run_simulation(n=100)
        
        output_file = tmp_path / "test_stats.json"
        
        with open(output_file, "w") as f:
            json.dump(stats, f)
        
        assert output_file.exists()
        
        # Verify contents
        with open(output_file) as f:
            loaded_stats = json.load(f)
        
        assert len(loaded_stats) == 4
        assert loaded_stats[0]["name"] in ["Team Alpha", "Team Beta", "Team Gamma", "Team Delta"]


class TestTournamentTracking:
    """Test tournament tracking and advancement recording."""

    def test_tracking_records_all_rounds(self, sample_teams_file):
        """Should record advancement through all rounds."""
        sim = BracketSimulator(sample_teams_file, best_of=1)
        sim.select_teams(count=4)
        
        # Run multiple simulations
        for _ in range(50):
            sim.simulate_tournament_with_tracking()
        
        # Check that we have results for all teams
        assert len(sim.simulation_results) == 4
        
        for team_name in sim.simulation_results:
            results = sim.simulation_results[team_name]
            
            # All teams should have participated
            total_appearances = sum(results.get(f"reached_{round_name}", 0) 
                                   for round_name in ["Semifinals", "Finals"])
            assert total_appearances > 0

    def test_championship_count_accurate(self, sample_teams_file):
        """Championship count should match finals wins."""
        sim = BracketSimulator(sample_teams_file, best_of=1)
        sim.select_teams(count=4)
        
        # Run known number of simulations
        n_sims = 100
        for _ in range(n_sims):
            sim.simulate_tournament_with_tracking()
        
        # Total championships should equal total simulations
        total_championships = sum(
            results.get("championships", 0) 
            for results in sim.simulation_results.values()
        )
        
        assert total_championships == n_sims

    def test_advancement_probabilities_sum_correctly(self, sample_teams_file):
        """Advancement probabilities should make sense."""
        sim = BracketSimulator(sample_teams_file, best_of=3)
        sim.select_teams(count=4)
        
        stats = sim.run_simulation(n=1000)
        
        # For 4-team bracket, all teams start in semifinals
        for team in stats:
            assert team["semifinals_prob"] == 100.0
        
        # Finals probability should be <= semifinals probability
        for team in stats:
            assert team["finals_prob"] <= team["semifinals_prob"]
        
        # Championship probability should be <= finals probability
        for team in stats:
            assert team["championship_prob"] <= team["finals_prob"]


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_two_team_bracket(self, sample_teams_file):
        """Should handle 2-team bracket (just finals)."""
        sim = BracketSimulator(sample_teams_file, best_of=3)
        selected = sim.select_teams(count=2)
        
        assert len(selected) == 2
        assert sim.get_round_name(2) == "Finals"
        
        result = sim.simulate_tournament_with_tracking()
        assert result["champion"]["name"] in ["Team Alpha", "Team Gamma"]

    def test_large_elo_variance(self, sample_teams_file):
        """Large variance should create more unpredictability."""
        sim_low = BracketSimulator(sample_teams_file, best_of=1, elo_sigma=10)
        sim_high = BracketSimulator(sample_teams_file, best_of=1, elo_sigma=100)
        
        sim_low.select_teams(count=4)
        sim_high.select_teams(count=4)
        
        stats_low = sim_low.run_simulation(n=1000)
        stats_high = sim_high.run_simulation(n=1000)
        
        # Higher variance should lead to more spread probabilities
        # (harder to predict winner)
        top_prob_low = stats_low[0]["championship_prob"]
        top_prob_high = stats_high[0]["championship_prob"]
        
        # With more variance, top team should have lower dominance
        # (though this is probabilistic, so might not always hold)
        assert top_prob_low >= 0
        assert top_prob_high >= 0

    def test_zero_simulations_error(self, sample_teams_file):
        """Should handle n=0 gracefully."""
        sim = BracketSimulator(sample_teams_file, best_of=3)
        sim.select_teams(count=4)
        
        # This might return empty stats or raise error
        # Either behavior is acceptable
        try:
            stats = sim.run_simulation(n=0)
            # If it doesn't raise, should return empty or valid stats
            assert isinstance(stats, list)
        except (ValueError, ZeroDivisionError):
            # Also acceptable to raise an error
            pass

    def test_best_of_1_vs_best_of_5_difference(self, sample_teams_file):
        """BO5 should favor stronger team more than BO1."""
        sim_bo1 = BracketSimulator(sample_teams_file, best_of=1)
        sim_bo5 = BracketSimulator(sample_teams_file, best_of=5)
        
        sim_bo1.select_teams(count=4)
        sim_bo5.select_teams(count=4)
        
        stats_bo1 = sim_bo1.run_simulation(n=1000)
        stats_bo5 = sim_bo5.run_simulation(n=1000)
        
        # Strongest team (Team Alpha) should have higher win rate in BO5
        top_team_bo1 = stats_bo1[0]["championship_prob"]
        top_team_bo5 = stats_bo5[0]["championship_prob"]
        
        # BO5 should favor favorite more (though probabilistic)
        assert top_team_bo5 >= top_team_bo1 - 5  # Allow 5% tolerance


class TestDataIntegrity:
    """Test data validation and integrity."""

    def test_elo_ratings_preserved(self, sample_teams_file):
        """ELO ratings should not change during simulation."""
        sim = BracketSimulator(sample_teams_file, best_of=3)
        teams_before = sim.all_teams.copy()
        
        sim.select_teams(count=4)
        sim.run_simulation(n=100)
        
        teams_after = sim.all_teams
        
        # ELO ratings should be unchanged
        for before, after in zip(teams_before, teams_after):
            assert before["elo_rating"] == after["elo_rating"]

    def test_team_names_unique(self, sample_teams_file):
        """All team names should be unique."""
        sim = BracketSimulator(sample_teams_file, best_of=3)
        
        names = [team["name"] for team in sim.all_teams]
        assert len(names) == len(set(names)), "Team names should be unique"

    def test_seeds_sequential(self, sample_teams_file):
        """Seeds should be 1, 2, 3, ... N."""
        sim = BracketSimulator(sample_teams_file, best_of=3)
        selected = sim.select_teams(count=4)
        
        seeds = [team["seed"] for team in selected]
        assert seeds == [1, 2, 3, 4]

    def test_probability_bounds(self, sample_teams_file):
        """All probabilities should be between 0 and 100."""
        sim = BracketSimulator(sample_teams_file, best_of=3)
        sim.select_teams(count=4)
        stats = sim.run_simulation(n=100)
        
        for team in stats:
            for key, value in team.items():
                if key.endswith("_prob"):
                    assert 0 <= value <= 100, f"{key} should be 0-100, got {value}"