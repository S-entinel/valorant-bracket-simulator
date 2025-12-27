import pytest
from src.bracket_simulator import BracketSimulator


class TestBracketSetup:
    """Test tournament bracket setup and team selection."""

    def test_load_teams_from_file(self, sample_teams_file):
        """Should successfully load teams from JSON file."""
        sim = BracketSimulator(sample_teams_file, best_of=3)
        assert len(sim.all_teams) == 4
        assert sim.all_teams[0]["name"] == "Team Alpha"

    def test_select_teams_by_elo(self, sample_teams_file):
        """Should select and seed teams by ELO rating."""
        sim = BracketSimulator(sample_teams_file, best_of=3)
        selected = sim.select_teams(count=4)
        
        # Should be ordered by ELO (highest first)
        assert selected[0]["name"] == "Team Alpha"  # 1700
        assert selected[1]["name"] == "Team Gamma"  # 1680
        assert selected[2]["name"] == "Team Beta"   # 1650
        assert selected[3]["name"] == "Team Delta"  # 1620

    def test_assign_seeds(self, sample_teams_file):
        """Should assign seeds 1-N based on ELO."""
        sim = BracketSimulator(sample_teams_file, best_of=3)
        selected = sim.select_teams(count=4)
        
        for i, team in enumerate(selected, 1):
            assert team["seed"] == i, f"Team {i} should have seed {i}"

    def test_auto_bracket_size(self, sample_teams_file):
        """Should auto-select largest power of 2."""
        sim = BracketSimulator(sample_teams_file, best_of=3)
        selected = sim.select_teams(count=None)  # Auto
        
        # With 4 teams, should select 4 (2^2)
        assert len(selected) == 4

    def test_insufficient_teams_error(self, sample_teams_file):
        """Should raise error if requesting more teams than available."""
        sim = BracketSimulator(sample_teams_file, best_of=3)
        
        with pytest.raises(ValueError, match="only 4 available"):
            sim.select_teams(count=8)


class TestRoundNaming:
    """Test tournament round name generation."""

    def test_finals_name(self, sample_teams_file):
        """2 teams = Finals."""
        sim = BracketSimulator(sample_teams_file, best_of=3)
        assert sim.get_round_name(2) == "Finals"

    def test_semifinals_name(self, sample_teams_file):
        """4 teams = Semifinals."""
        sim = BracketSimulator(sample_teams_file, best_of=3)
        assert sim.get_round_name(4) == "Semifinals"

    def test_quarterfinals_name(self, sample_teams_file):
        """8 teams = Quarterfinals."""
        sim = BracketSimulator(sample_teams_file, best_of=3)
        assert sim.get_round_name(8) == "Quarterfinals"

    def test_round_of_16_name(self, sample_teams_file):
        """16 teams = Round_of_16."""
        sim = BracketSimulator(sample_teams_file, best_of=3)
        assert sim.get_round_name(16) == "Round_of_16"


class TestTournamentSimulation:
    """Test complete tournament simulation."""

    def test_single_tournament_produces_champion(self, sample_teams_file):
        """Single tournament should produce exactly one champion."""
        sim = BracketSimulator(sample_teams_file, best_of=1)
        sim.select_teams(count=4)
        
        result = sim.simulate_tournament_with_tracking()
        
        assert "champion" in result
        assert result["champion"]["name"] in [
            "Team Alpha", "Team Beta", "Team Gamma", "Team Delta"
        ]

    def test_tournament_tracks_advancement(self, sample_teams_file):
        """Should track which rounds each team reached."""
        sim = BracketSimulator(sample_teams_file, best_of=1)
        sim.select_teams(count=4)
        
        sim.simulate_tournament_with_tracking()
        
        # All 4 teams should have reached semifinals
        assert len(sim.simulation_results) > 0
        
        # Champion should have reached finals
        for team_name, stats in sim.simulation_results.items():
            if stats.get("championships", 0) > 0:
                assert stats.get("reached_Finals", 0) > 0

    def test_monte_carlo_simulation(self, sample_teams_file):
        """Monte Carlo should produce probability distributions."""
        sim = BracketSimulator(sample_teams_file, best_of=1)
        sim.select_teams(count=4)
        
        stats = sim.run_simulation(n=100)  # 100 sims for speed
        
        assert len(stats) == 4, "Should have stats for all 4 teams"
        
        # All probabilities should sum to ~100%
        total_champ_prob = sum(t["championship_prob"] for t in stats)
        assert abs(total_champ_prob - 100.0) < 1.0, "Probabilities should sum to 100%"

    def test_stronger_team_higher_probability(self, sample_teams_file):
        """Higher ELO team should win more often."""
        sim = BracketSimulator(sample_teams_file, best_of=3)
        sim.select_teams(count=4)
        
        stats = sim.run_simulation(n=1000)
        
        # Team Alpha (highest ELO) should have highest win probability
        top_team = stats[0]
        assert top_team["name"] == "Team Alpha"
        assert top_team["championship_prob"] > 20.0, "Strongest team should have >20% win rate"

    def test_all_teams_reach_first_round(self, sample_teams_file):
        """All selected teams should reach round 1."""
        sim = BracketSimulator(sample_teams_file, best_of=1)
        sim.select_teams(count=4)
        
        stats = sim.run_simulation(n=100)
        
        for team in stats:
            assert team["semifinals_prob"] == 100.0, "All teams start in semifinals (4-team bracket)"


class TestStatisticsCalculation:
    """Test statistics calculation and formatting."""

    def test_statistics_sorted_by_win_probability(self, sample_teams_file):
        """Stats should be sorted by championship probability."""
        sim = BracketSimulator(sample_teams_file, best_of=3)
        sim.select_teams(count=4)
        
        stats = sim.run_simulation(n=100)
        
        # Should be in descending order
        for i in range(len(stats) - 1):
            assert stats[i]["championship_prob"] >= stats[i + 1]["championship_prob"]

    def test_probability_fields_present(self, sample_teams_file):
        """All probability fields should be in output."""
        sim = BracketSimulator(sample_teams_file, best_of=3)
        sim.select_teams(count=4)
        
        stats = sim.run_simulation(n=100)
        team_stat = stats[0]
        
        required_fields = [
            "name", "seed", "elo_rating",
            "championship_prob", "finals_prob", "semifinals_prob"
        ]
        
        for field in required_fields:
            assert field in team_stat, f"Missing field: {field}"

    def test_probabilities_are_percentages(self, sample_teams_file):
        """Probabilities should be 0-100, not 0-1."""
        sim = BracketSimulator(sample_teams_file, best_of=3)
        sim.select_teams(count=4)
        
        stats = sim.run_simulation(n=100)
        
        for team in stats:
            assert 0 <= team["championship_prob"] <= 100
            assert 0 <= team["finals_prob"] <= 100