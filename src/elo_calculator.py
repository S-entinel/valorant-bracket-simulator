"""
ELO Rating Calculator for Valorant Teams

Calculates team ELO ratings from historical match results rather than using
manual estimates. This provides data-driven, objective team strength ratings.

Standard ELO formula:
    New Rating = Old Rating + K * (Actual Score - Expected Score)

Where:
    K = K-factor (32 for esports, determines rating volatility)
    Actual Score = 1 for win, 0 for loss (or fractional for map count)
    Expected Score = 1 / (1 + 10^((opponent_rating - own_rating) / 400))
"""

import json
from typing import Dict, List, Tuple, Optional
from collections import defaultdict
import math


class ELOCalculator:
    """Calculate ELO ratings from match history."""
    
    def __init__(
        self,
        k_factor: int = 32,
        initial_rating: float = 1500.0,
        use_map_scores: bool = True
    ):
        """
        Initialize ELO calculator.
        
        Args:
            k_factor: Rating change multiplier (32 = standard for esports)
            initial_rating: Starting rating for all teams
            use_map_scores: If True, use map counts (13-7 -> 0.65 score)
                          If False, use binary outcomes (1 or 0)
        """
        self.k_factor = k_factor
        self.initial_rating = initial_rating
        self.use_map_scores = use_map_scores
        
        # Team ratings: {team_name: current_rating}
        self.ratings: Dict[str, float] = defaultdict(lambda: initial_rating)
        
        # Match history for debugging/analysis
        self.match_history: List[Dict] = []
        
    def expected_score(self, rating_a: float, rating_b: float) -> float:
        """
        Calculate expected score for team A against team B.
        
        Returns probability that team A wins (0.0 to 1.0).
        """
        return 1.0 / (1.0 + 10 ** ((rating_b - rating_a) / 400.0))
    
    def calculate_actual_score(
        self,
        maps_won: int,
        maps_lost: int
    ) -> float:
        """
        Calculate actual score from map results.
        
        Args:
            maps_won: Maps won by the team
            maps_lost: Maps lost by the team
            
        Returns:
            Actual score (0.0 to 1.0)
            
        Examples:
            2-0 win -> 1.0
            2-1 win -> 0.67
            1-2 loss -> 0.33
            0-2 loss -> 0.0
        """
        if not self.use_map_scores:
            # Binary: 1 if won more maps, 0 otherwise
            return 1.0 if maps_won > maps_lost else 0.0
        
        # Fractional: maps_won / total_maps
        total_maps = maps_won + maps_lost
        if total_maps == 0:
            return 0.5  # Draw (shouldn't happen in Valorant)
        
        return maps_won / total_maps
    
    def update_ratings(
        self,
        team_a: str,
        team_b: str,
        team_a_maps: int,
        team_b_maps: int
    ) -> Tuple[float, float]:
        """
        Update ELO ratings based on match result.
        
        Args:
            team_a: Name of first team
            team_b: Name of second team
            team_a_maps: Maps won by team A
            team_b_maps: Maps won by team B
            
        Returns:
            Tuple of (new_rating_a, new_rating_b)
        """
        # Get current ratings
        rating_a = self.ratings[team_a]
        rating_b = self.ratings[team_b]
        
        # Calculate expected scores
        expected_a = self.expected_score(rating_a, rating_b)
        expected_b = self.expected_score(rating_b, rating_a)
        
        # Calculate actual scores
        actual_a = self.calculate_actual_score(team_a_maps, team_b_maps)
        actual_b = self.calculate_actual_score(team_b_maps, team_a_maps)
        
        # Update ratings
        new_rating_a = rating_a + self.k_factor * (actual_a - expected_a)
        new_rating_b = rating_b + self.k_factor * (actual_b - expected_b)
        
        self.ratings[team_a] = new_rating_a
        self.ratings[team_b] = new_rating_b
        
        # Record match for history
        self.match_history.append({
            "team_a": team_a,
            "team_b": team_b,
            "score": f"{team_a_maps}-{team_b_maps}",
            "rating_a_before": rating_a,
            "rating_b_before": rating_b,
            "rating_a_after": new_rating_a,
            "rating_b_after": new_rating_b,
            "rating_change_a": new_rating_a - rating_a,
            "rating_change_b": new_rating_b - rating_b,
        })
        
        return new_rating_a, new_rating_b
    
    def process_matches(self, matches: List[Dict]) -> None:
        """
        Process a list of matches and update ratings.
        
        Args:
            matches: List of match dictionaries with format:
                {
                    "team_a": "Team Name 1",
                    "team_b": "Team Name 2",
                    "score_a": 2,  # Maps won by team A
                    "score_b": 1   # Maps won by team B
                }
        """
        for match in matches:
            self.update_ratings(
                team_a=match["team_a"],
                team_b=match["team_b"],
                team_a_maps=match["score_a"],
                team_b_maps=match["score_b"]
            )
    
    def load_from_file(self, filename: str) -> None:
        """
        Load match history from JSON file and calculate ratings.
        
        Args:
            filename: Path to JSON file with match data
        """
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        matches = data.get("matches", [])
        self.process_matches(matches)
        
        print(f"Processed {len(matches)} matches")
        print(f"Calculated ratings for {len(self.ratings)} teams")
    
    def get_ratings(
        self,
        min_matches: int = 0,
        sort_by_rating: bool = True
    ) -> List[Dict[str, any]]:
        """
        Get current team ratings.
        
        Args:
            min_matches: Minimum number of matches a team must have played
            sort_by_rating: If True, sort by rating (highest first)
            
        Returns:
            List of team rating dictionaries
        """
        # Count matches per team
        match_counts = defaultdict(int)
        for match in self.match_history:
            match_counts[match["team_a"]] += 1
            match_counts[match["team_b"]] += 1
        
        # Build ratings list
        ratings_list = []
        for team, rating in self.ratings.items():
            if match_counts[team] >= min_matches:
                ratings_list.append({
                    "name": team,
                    "elo_rating": round(rating, 1),
                    "matches_played": match_counts[team]
                })
        
        # Sort if requested
        if sort_by_rating:
            ratings_list.sort(key=lambda x: x["elo_rating"], reverse=True)
        
        return ratings_list
    
    def get_rating(self, team_name: str) -> float:
        """Get current rating for a specific team."""
        return self.ratings.get(team_name, self.initial_rating)
    
    def get_rating_history(self, team_name: str) -> List[Tuple[int, float]]:
        """
        Get rating history for a specific team.
        
        Returns:
            List of (match_number, rating) tuples
        """
        history = [(0, self.initial_rating)]
        
        for i, match in enumerate(self.match_history, 1):
            if match["team_a"] == team_name:
                history.append((i, match["rating_a_after"]))
            elif match["team_b"] == team_name:
                history.append((i, match["rating_b_after"]))
        
        return history
    
    def save_ratings(self, filename: str = "team_ratings.json") -> None:
        """
        Save calculated ratings to JSON file.
        
        Format matches the valorant_data.json structure used by bracket_simulator.py
        """
        ratings_list = self.get_ratings(min_matches=1)
        
        # Convert to team data format
        teams = []
        for i, team_data in enumerate(ratings_list, 1):
            teams.append({
                "id": str(i),
                "name": team_data["name"],
                "elo_rating": team_data["elo_rating"],
                "matches_played": team_data["matches_played"],
                "rank": i,
            })
        
        output = {
            "teams": teams,
            "metadata": {
                "source": "elo_calculator",
                "k_factor": self.k_factor,
                "initial_rating": self.initial_rating,
                "use_map_scores": self.use_map_scores,
                "total_matches": len(self.match_history),
                "total_teams": len(teams),
            }
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2)
        
        print(f"✓ Ratings saved to {filename}")
    
    def print_ratings(self, top_n: Optional[int] = None) -> None:
        """Print current ratings in a formatted table."""
        ratings = self.get_ratings(min_matches=1)
        
        if top_n:
            ratings = ratings[:top_n]
        
        print("\n" + "=" * 70)
        print(f"ELO RATINGS (K={self.k_factor}, Initial={self.initial_rating})")
        print("=" * 70)
        print(f"{'Rank':<6} {'Team':<30} {'Rating':<10} {'Matches':<10}")
        print("-" * 70)
        
        for i, team in enumerate(ratings, 1):
            print(
                f"{i:<6} "
                f"{team['name']:<30} "
                f"{team['elo_rating']:<10.1f} "
                f"{team['matches_played']:<10}"
            )
        
        print("=" * 70 + "\n")


def main():
    """Example usage of ELO calculator."""
    
    # Example match data
    example_matches = {
        "matches": [
            {"team_a": "Team A", "team_b": "Team B", "score_a": 2, "score_b": 0},
            {"team_a": "Team C", "team_b": "Team D", "score_a": 2, "score_b": 1},
            {"team_a": "Team A", "team_b": "Team C", "score_a": 1, "score_b": 2},
            {"team_a": "Team B", "team_b": "Team D", "score_a": 2, "score_b": 1},
        ]
    }
    
    # Create calculator
    calc = ELOCalculator(k_factor=32, initial_rating=1500.0)
    
    # Process matches
    calc.process_matches(example_matches["matches"])
    
    # Print results
    calc.print_ratings()
    
    # Show specific team history
    print("Team A rating history:")
    for match_num, rating in calc.get_rating_history("Team A"):
        print(f"  After match {match_num}: {rating:.1f}")


if __name__ == "__main__":
    main()