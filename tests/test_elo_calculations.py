import pytest
import math
from bracket_simulator import BracketSimulator


class TestELOCalculations:
    """Test suite for ELO probability calculations."""

    def test_equal_teams_50_percent_probability(self, sample_teams_file):
        """Equal ELO teams should have 50% win probability."""
        sim = BracketSimulator(sample_teams_file, best_of=1)
        prob = sim.calculate_win_probability(1500, 1500)
        assert abs(prob - 0.5) < 0.001, "Equal teams should have ~50% win rate"

    def test_stronger_team_higher_probability(self, sample_teams_file):
        """Higher ELO team should have >50% win probability."""
        sim = BracketSimulator(sample_teams_file, best_of=1)
        prob = sim.calculate_win_probability(1600, 1500)
        assert prob > 0.5, "Stronger team should have >50% win rate"
        assert prob < 1.0, "Win probability should be <100%"

    def test_large_elo_difference(self, sample_teams_file):
        """Large ELO difference should produce high probability."""
        sim = BracketSimulator(sample_teams_file, best_of=1)
        prob = sim.calculate_win_probability(1800, 1400)  # 400 point gap
        assert prob > 0.9, "400 ELO gap should give >90% win rate"

    def test_probability_symmetry(self, sample_teams_file):
        """P(A beats B) + P(B beats A) should equal 1."""
        sim = BracketSimulator(sample_teams_file, best_of=1)
        prob_a = sim.calculate_win_probability(1600, 1500)
        prob_b = sim.calculate_win_probability(1500, 1600)
        assert abs((prob_a + prob_b) - 1.0) < 0.001, "Probabilities must sum to 1"

    def test_series_probability_bo1(self, sample_teams_file):
        """BO1 series probability should equal map probability."""
        sim = BracketSimulator(sample_teams_file, best_of=1)
        map_prob = 0.6
        series_prob = sim.series_win_probability(map_prob, best_of=1)
        assert abs(series_prob - map_prob) < 0.001, "BO1 should equal map prob"

    def test_series_probability_bo3(self, sample_teams_file):
        """BO3 should favor stronger team more than single map."""
        sim = BracketSimulator(sample_teams_file, best_of=3)
        map_prob = 0.6
        series_prob = sim.series_win_probability(map_prob, best_of=3)
        
        # BO3 should increase probability for favorite
        assert series_prob > map_prob, "BO3 should favor stronger team"
        
        # Verify binomial calculation
        # P(win 2) + P(win 3) where n=3, p=0.6
        expected = (
            math.comb(3, 2) * (0.6**2) * (0.4**1) +
            math.comb(3, 3) * (0.6**3) * (0.4**0)
        )
        assert abs(series_prob - expected) < 0.001

    def test_series_probability_bo5(self, sample_teams_file):
        """BO5 should further favor stronger team."""
        sim = BracketSimulator(sample_teams_file, best_of=5)
        map_prob = 0.6
        bo3_prob = sim.series_win_probability(map_prob, best_of=3)
        bo5_prob = sim.series_win_probability(map_prob, best_of=5)
        
        assert bo5_prob > bo3_prob, "BO5 should favor stronger team more than BO3"

    def test_extreme_probabilities(self, sample_teams_file):
        """Test edge cases with extreme probabilities."""
        sim = BracketSimulator(sample_teams_file, best_of=3)
        
        # Very high probability
        high_prob = sim.series_win_probability(0.99, best_of=3)
        assert high_prob > 0.99, "High map win rate should stay high"
        
        # Very low probability
        low_prob = sim.series_win_probability(0.01, best_of=3)
        assert low_prob < 0.01, "Low map win rate should stay low"


class TestELOVariance:
    """Test ELO variance feature (performance noise)."""

    def test_variance_affects_probabilities(self, sample_teams_file):
        """ELO variance should create different match outcomes."""
        sim = BracketSimulator(sample_teams_file, best_of=1, elo_sigma=50)
        
        team_a = {"name": "Team A", "elo_rating": 1600, "seed": 1}
        team_b = {"name": "Team B", "elo_rating": 1600, "seed": 2}
        
        # Run same matchup 100 times - should get some variation
        results = [sim.simulate_match(team_a, team_b)["name"] for _ in range(100)]
        
        team_a_wins = results.count("Team A")
        team_b_wins = results.count("Team B")
        
        # With variance, shouldn't be exactly 50/50
        # But should be roughly balanced
        assert 30 < team_a_wins < 70, "Variance should create realistic spread"
        assert 30 < team_b_wins < 70

    def test_no_variance_deterministic(self, sample_teams_file):
        """Without variance, equal teams should split exactly."""
        sim = BracketSimulator(sample_teams_file, best_of=1, elo_sigma=None)
        
        team_a = {"name": "Team A", "elo_rating": 1600, "seed": 1}
        team_b = {"name": "Team B", "elo_rating": 1600, "seed": 2}
        
        # Equal teams with no variance should be ~50/50 over many sims
        results = [sim.simulate_match(team_a, team_b)["name"] for _ in range(1000)]
        team_a_wins = results.count("Team A")
        
        # Should be close to 50%
        assert 450 < team_a_wins < 550, "No variance should give ~50/50 for equal teams"