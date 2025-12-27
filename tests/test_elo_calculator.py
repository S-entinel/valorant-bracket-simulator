import pytest
import json
from src.elo_calculator import ELOCalculator


class TestELOCalculator:
    """Test ELO rating calculations."""
    
    def test_initial_rating(self):
        """All teams should start at initial rating."""
        calc = ELOCalculator(initial_rating=1500.0)
        
        assert calc.get_rating("Team A") == 1500.0
        assert calc.get_rating("Team B") == 1500.0
    
    def test_expected_score_equal_teams(self):
        """Equal teams should have 50% expected score."""
        calc = ELOCalculator()
        
        expected = calc.expected_score(1500, 1500)
        assert abs(expected - 0.5) < 0.001
    
    def test_expected_score_stronger_team(self):
        """Stronger team should have higher expected score."""
        calc = ELOCalculator()
        
        # 100 point advantage -> ~64% win probability
        expected = calc.expected_score(1600, 1500)
        assert 0.60 < expected < 0.70
    
    def test_expected_score_symmetry(self):
        """Expected scores should sum to 1."""
        calc = ELOCalculator()
        
        exp_a = calc.expected_score(1600, 1500)
        exp_b = calc.expected_score(1500, 1600)
        
        assert abs((exp_a + exp_b) - 1.0) < 0.001
    
    def test_calculate_actual_score_decisive_win(self):
        """2-0 win should give 1.0 score."""
        calc = ELOCalculator(use_map_scores=True)
        
        score = calc.calculate_actual_score(2, 0)
        assert score == 1.0
    
    def test_calculate_actual_score_close_win(self):
        """2-1 win should give 0.67 score."""
        calc = ELOCalculator(use_map_scores=True)
        
        score = calc.calculate_actual_score(2, 1)
        assert abs(score - 0.67) < 0.01
    
    def test_calculate_actual_score_loss(self):
        """0-2 loss should give 0.0 score."""
        calc = ELOCalculator(use_map_scores=True)
        
        score = calc.calculate_actual_score(0, 2)
        assert score == 0.0
    
    def test_calculate_actual_score_binary_mode(self):
        """Binary mode should give 1 or 0 only."""
        calc = ELOCalculator(use_map_scores=False)
        
        win_score = calc.calculate_actual_score(2, 1)  # Close win
        loss_score = calc.calculate_actual_score(1, 2)  # Close loss
        
        assert win_score == 1.0
        assert loss_score == 0.0
    
    def test_update_ratings_winner_gains_points(self):
        """Winner should gain rating points."""
        calc = ELOCalculator(k_factor=32, initial_rating=1500.0)
        
        new_a, new_b = calc.update_ratings("Team A", "Team B", 2, 0)
        
        assert new_a > 1500.0  # Winner gains
        assert new_b < 1500.0  # Loser loses
    
    def test_update_ratings_conservation(self):
        """Total rating points should be conserved."""
        calc = ELOCalculator(k_factor=32, initial_rating=1500.0)
        
        total_before = 1500.0 + 1500.0
        new_a, new_b = calc.update_ratings("Team A", "Team B", 2, 1)
        total_after = new_a + new_b
        
        assert abs(total_before - total_after) < 0.1
    
    def test_update_ratings_upset_bonus(self):
        """Underdog winning should gain more points than expected."""
        calc = ELOCalculator(k_factor=32, initial_rating=1500.0)
        
        # Set up ratings with team B favored
        calc.ratings["Team A"] = 1400.0
        calc.ratings["Team B"] = 1600.0
        
        # Team A (underdog) wins
        new_a, new_b = calc.update_ratings("Team A", "Team B", 2, 0)
        
        rating_change_a = new_a - 1400.0
        rating_change_b = new_b - 1600.0
        
        # Underdog should gain more than they'd lose
        assert rating_change_a > 20  # Significant gain
        assert rating_change_b < -20  # Significant loss
    
    def test_process_matches(self):
        """Should process multiple matches correctly."""
        calc = ELOCalculator(k_factor=32, initial_rating=1500.0)
        
        matches = [
            {"team_a": "Team A", "team_b": "Team B", "score_a": 2, "score_b": 0},
            {"team_a": "Team C", "team_b": "Team D", "score_a": 2, "score_b": 1},
        ]
        
        calc.process_matches(matches)
        
        assert len(calc.match_history) == 2
        assert len(calc.ratings) == 4
    
    def test_get_ratings_sorting(self):
        """Ratings should be sorted by ELO (highest first)."""
        calc = ELOCalculator()
        
        calc.ratings["Team A"] = 1600.0
        calc.ratings["Team B"] = 1700.0
        calc.ratings["Team C"] = 1500.0
        
        # Add fake match history for counts
        calc.match_history = [
            {"team_a": "Team A", "team_b": "Team B"},
            {"team_a": "Team B", "team_b": "Team C"},
        ]
        
        ratings = calc.get_ratings(min_matches=0)
        
        assert ratings[0]["name"] == "Team B"  # Highest
        assert ratings[1]["name"] == "Team A"
        assert ratings[2]["name"] == "Team C"  # Lowest
    
    def test_get_ratings_min_matches_filter(self):
        """Should filter teams by minimum matches played."""
        calc = ELOCalculator()
        
        matches = [
            {"team_a": "Team A", "team_b": "Team B", "score_a": 2, "score_b": 0},
            {"team_a": "Team A", "team_b": "Team C", "score_a": 2, "score_b": 0},
            {"team_a": "Team D", "team_b": "Team E", "score_a": 2, "score_b": 0},
        ]
        
        calc.process_matches(matches)
        
        # Team A has 2 matches, others have 1
        ratings = calc.get_ratings(min_matches=2)
        
        assert len(ratings) == 1
        assert ratings[0]["name"] == "Team A"
    
    def test_get_rating_history(self):
        """Should track rating changes over time."""
        calc = ELOCalculator(k_factor=32, initial_rating=1500.0)
        
        matches = [
            {"team_a": "Team A", "team_b": "Team B", "score_a": 2, "score_b": 0},
            {"team_a": "Team A", "team_b": "Team C", "score_a": 2, "score_b": 1},
        ]
        
        calc.process_matches(matches)
        
        history = calc.get_rating_history("Team A")
        
        # Should have initial rating + 2 match results
        assert len(history) == 3
        assert history[0] == (0, 1500.0)  # Initial
        assert history[1][1] > 1500.0  # After first win
        assert history[2][1] > history[1][1]  # After second win
    
    def test_k_factor_impact(self):
        """Higher K-factor should produce larger rating changes."""
        calc_low_k = ELOCalculator(k_factor=16, initial_rating=1500.0)
        calc_high_k = ELOCalculator(k_factor=64, initial_rating=1500.0)
        
        # Same match for both
        new_a_low, _ = calc_low_k.update_ratings("A", "B", 2, 0)
        new_a_high, _ = calc_high_k.update_ratings("A", "B", 2, 0)
        
        change_low = new_a_low - 1500.0
        change_high = new_a_high - 1500.0
        
        assert change_high > change_low * 1.5  # Significant difference
    
    def test_match_history_records_changes(self):
        """Match history should record rating changes."""
        calc = ELOCalculator(k_factor=32, initial_rating=1500.0)
        
        calc.update_ratings("Team A", "Team B", 2, 0)
        
        match = calc.match_history[0]
        
        assert "team_a" in match
        assert "team_b" in match
        assert "score" in match
        assert "rating_a_before" in match
        assert "rating_a_after" in match
        assert "rating_change_a" in match
        
        # Verify change is calculated correctly
        expected_change = match["rating_a_after"] - match["rating_a_before"]
        assert abs(match["rating_change_a"] - expected_change) < 0.001
    
    def test_save_and_load_integration(self, tmp_path):
        """Should save ratings in correct format for bracket simulator."""
        calc = ELOCalculator()
        
        matches = [
            {"team_a": "EDG", "team_b": "Heretics", "score_a": 2, "score_b": 0},
            {"team_a": "LEVIATÁN", "team_b": "Sentinels", "score_a": 2, "score_b": 1},
        ]
        
        calc.process_matches(matches)
        
        output_file = tmp_path / "test_ratings.json"
        calc.save_ratings(filename=str(output_file))
        
        # Load and verify format
        with open(output_file) as f:
            data = json.load(f)
        
        assert "teams" in data
        assert "metadata" in data
        assert len(data["teams"]) == 4
        
        # Verify team structure
        team = data["teams"][0]
        assert "id" in team
        assert "name" in team
        assert "elo_rating" in team
        assert "matches_played" in team
        assert "rank" in team
        
        # Verify metadata
        metadata = data["metadata"]
        assert metadata["source"] == "elo_calculator"
        assert metadata["k_factor"] == 32
        assert metadata["total_matches"] == 2


class TestELOEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_zero_maps_played(self):
        """Should handle 0-0 score gracefully."""
        calc = ELOCalculator()
        
        score = calc.calculate_actual_score(0, 0)
        assert score == 0.5  # Draw
    
    def test_very_large_rating_difference(self):
        """Should handle large rating gaps correctly."""
        calc = ELOCalculator()
        
        # 1000 point gap
        expected = calc.expected_score(2000, 1000)
        
        # Should be very high but not 1.0
        assert 0.99 < expected < 1.0
    
    def test_same_team_twice(self):
        """Should handle team playing against itself (shouldn't happen)."""
        calc = ELOCalculator()
        
        # This is an edge case that shouldn't happen in real data
        new_a, new_b = calc.update_ratings("Team A", "Team A", 2, 1)
        
        # Ratings should be unchanged since expected score = 0.5
        assert abs(new_a - 1500.0) < 20  # Small change due to map score
    
    def test_negative_k_factor(self):
        """Negative K-factor should reverse rating changes."""
        calc = ELOCalculator(k_factor=-32, initial_rating=1500.0)
        
        new_a, new_b = calc.update_ratings("Team A", "Team B", 2, 0)
        
        # Winner should lose points, loser should gain
        assert new_a < 1500.0
        assert new_b > 1500.0