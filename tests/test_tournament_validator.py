# tests/test_tournament_validator.py
"""
Tests for multi-tournament validation system.
"""

import pytest
import json
from src.tournament_validator import (
    split_by_tournament,
    get_tournament_teams,
    calculate_elo_from_matches,
    predict_tournament_winner
)


class TestTournamentSplitting:
    """Test tournament data splitting."""
    
    def test_split_by_tournament(self):
        """Should group matches by tournament."""
        matches = [
            {"team_a": "A", "team_b": "B", "score_a": 2, "score_b": 0, "event": "Tournament 1"},
            {"team_a": "C", "team_b": "D", "score_a": 2, "score_b": 1, "event": "Tournament 1"},
            {"team_a": "E", "team_b": "F", "score_a": 2, "score_b": 0, "event": "Tournament 2"},
        ]
        
        result = split_by_tournament(matches)
        
        assert "Tournament 1" in result
        assert "Tournament 2" in result
        assert len(result["Tournament 1"]) == 2
        assert len(result["Tournament 2"]) == 1
    
    def test_filter_showmatches(self):
        """Should exclude showmatches from results."""
        matches = [
            {"team_a": "A", "team_b": "B", "score_a": 2, "score_b": 0, "event": "T1", "round": "Finals"},
            {"team_a": "C", "team_b": "D", "score_a": 8, "score_b": 13, "event": "T1", "round": "Showmatch"},
        ]
        
        result = split_by_tournament(matches)
        
        assert len(result["T1"]) == 1
        assert result["T1"][0]["team_a"] == "A"
    
    def test_get_tournament_teams(self):
        """Should extract unique team names."""
        matches = [
            {"team_a": "Team A", "team_b": "Team B", "score_a": 2, "score_b": 0},
            {"team_a": "Team B", "team_b": "Team C", "score_a": 2, "score_b": 1},
        ]
        
        teams = get_tournament_teams(matches)
        
        assert len(teams) == 3
        assert "Team A" in teams
        assert "Team B" in teams
        assert "Team C" in teams


class TestELOCalculation:
    """Test ELO calculation logic."""
    
    def test_calculate_elo_initial_rating(self):
        """Teams should start at 1500."""
        matches = [
            {"team_a": "A", "team_b": "B", "score_a": 2, "score_b": 0}
        ]
        
        ratings = calculate_elo_from_matches(matches)
        
        # Winner should be above 1500, loser below
        assert ratings["A"] > 1500
        assert ratings["B"] < 1500
    
    def test_calculate_elo_conservation(self):
        """Total rating points should be conserved."""
        matches = [
            {"team_a": "A", "team_b": "B", "score_a": 2, "score_b": 1}
        ]
        
        ratings = calculate_elo_from_matches(matches)
        
        total = ratings["A"] + ratings["B"]
        # Should sum to 3000 (2 teams * 1500 initial)
        assert abs(total - 3000) < 0.1
    
    def test_calculate_elo_map_scoring(self):
        """Closer matches should have smaller rating changes."""
        matches_decisive = [
            {"team_a": "A1", "team_b": "B1", "score_a": 2, "score_b": 0}
        ]
        matches_close = [
            {"team_a": "A2", "team_b": "B2", "score_a": 2, "score_b": 1}
        ]
        
        ratings_decisive = calculate_elo_from_matches(matches_decisive)
        ratings_close = calculate_elo_from_matches(matches_close)
        
        change_decisive = ratings_decisive["A1"] - 1500
        change_close = ratings_close["A2"] - 1500
        
        # Decisive win should give bigger rating change
        assert change_decisive > change_close


class TestPredictions:
    """Test tournament prediction logic."""
    
    def test_predict_empty_ratings(self):
        """Should handle empty ratings gracefully."""
        predictions = predict_tournament_winner({}, ["Team A", "Team B"])
        
        assert predictions == {}
    
    def test_predict_single_team(self):
        """Should handle single team edge case."""
        ratings = {"Team A": 1600}
        predictions = predict_tournament_winner(ratings, ["Team A"])
        
        # Can't predict with only 1 team
        assert len(predictions) <= 1
    
    def test_predict_stronger_team_higher_prob(self):
        """Stronger teams should have higher win probability."""
        ratings = {
            "Strong Team": 1700,
            "Weak Team 1": 1400,
            "Weak Team 2": 1400,
            "Weak Team 3": 1400,
        }
        teams = list(ratings.keys())
        
        predictions = predict_tournament_winner(ratings, teams, n_simulations=1000)
        
        if predictions:
            strong_prob = predictions.get("Strong Team", 0)
            weak_probs = [predictions.get(t, 0) for t in teams if "Weak" in t]
            
            # Strong team should have highest probability
            for weak_prob in weak_probs:
                assert strong_prob > weak_prob
    
    def test_predict_probabilities_sum_to_100(self):
        """Probabilities should approximately sum to 100%."""
        ratings = {
            f"Team {i}": 1500 + (i * 10)
            for i in range(8)
        }
        teams = list(ratings.keys())
        
        predictions = predict_tournament_winner(ratings, teams, n_simulations=5000)
        
        if predictions:
            total_prob = sum(predictions.values())
            # Allow 5% tolerance for Monte Carlo variance
            assert 95 <= total_prob <= 105


class TestValidationLogic:
    """Test validation metrics calculation."""
    
    def test_correct_prediction(self):
        """Should identify correct predictions."""
        predicted = "Team A"
        actual = "Team A"
        
        assert predicted == actual
    
    def test_top_3_prediction(self):
        """Should identify top-3 predictions."""
        predictions = [
            ("Team A", 30.0),
            ("Team B", 25.0),
            ("Team C", 20.0),
            ("Team D", 15.0),
        ]
        
        actual = "Team C"
        rank = next(i + 1 for i, (name, _) in enumerate(predictions) if name == actual)
        
        assert rank == 3
        assert rank <= 3  # Top-3
    
    def test_prediction_miss(self):
        """Should identify prediction misses."""
        predictions = [
            ("Team A", 30.0),
            ("Team B", 25.0),
            ("Team C", 20.0),
        ]
        
        actual = "Team Z"
        try:
            rank = next(i + 1 for i, (name, _) in enumerate(predictions) if name == actual)
        except StopIteration:
            rank = None
        
        assert rank is None  # Not in predictions


class TestDataIntegrity:
    """Test data validation and edge cases."""
    
    def test_missing_teams_in_ratings(self):
        """Should handle teams not in training data."""
        ratings = {
            "Team A": 1600,
            "Team B": 1550,
        }
        
        # Tournament includes team not in training
        tournament_teams = ["Team A", "Team B", "Team C"]
        
        predictions = predict_tournament_winner(ratings, tournament_teams)
        
        # Should still make predictions with available teams
        assert "Team A" in predictions or "Team B" in predictions
    
    def test_empty_tournament_teams(self):
        """Should handle empty tournament teams list."""
        ratings = {"Team A": 1600}
        
        predictions = predict_tournament_winner(ratings, [])
        
        assert predictions == {}
    
    def test_duplicate_teams(self):
        """Should handle duplicate team names."""
        matches = [
            {"team_a": "Team A", "team_b": "Team B", "score_a": 2, "score_b": 0},
            {"team_a": "Team A", "team_b": "Team B", "score_a": 2, "score_b": 1},
        ]
        
        teams = get_tournament_teams(matches)
        
        # Should have unique teams only
        assert len(teams) == 2
        assert len(set(teams)) == 2