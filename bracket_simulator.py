import json
import random
import math
from collections import defaultdict
from typing import List, Dict, Any, Optional


class BracketSimulator:
    def __init__(
        self,
        teams_file: str = "valorant_data.json",
        *,
        best_of: int = 3,
        elo_sigma: Optional[float] = None,
    ) -> None:
        """
        Initialize simulator with team data.

        Params
        ------
        teams_file : str
            Path to JSON file with team data (like valorant_data_live.json).
        best_of : int
            Match format: 1 (BO1), 3 (BO3), 5 (BO5), etc.
        elo_sigma : float or None
            Standard deviation of Elo noise per match. If provided,
            each team gets Elo ~ N(base_elo, sigma^2) in each match,
            modelling hot/cold performance.
        """
        with open(teams_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.all_teams: List[Dict[str, Any]] = data["teams"]
        self.teams: List[Dict[str, Any]] = []
        self.simulation_results: Dict[str, Dict[str, int]] = defaultdict(
            lambda: defaultdict(int)
        )

        self.best_of = best_of
        self.elo_sigma = elo_sigma

    # ------------------------------------------------------------------
    # Tournament setup
    # ------------------------------------------------------------------

    def select_teams(self, count: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Select top N teams by Elo rating for the tournament and assign seeds.

        If count is None, automatically choose the largest power of 2
        <= number of available teams (e.g. 8, 16, 32...).
        """
        available = len(self.all_teams)

        if count is None:
            # largest power of 2 <= available
            power = 1
            while power * 2 <= available:
                power *= 2
            count = power

        if count > available:
            raise ValueError(
                f"Requested {count} teams, but only {available} available."
            )

        self.teams = sorted(
            self.all_teams, key=lambda x: x["elo_rating"], reverse=True
        )[:count]

        print(f"\n{'=' * 60}")
        print(f"TOURNAMENT BRACKET: Top {count} Teams")
        print(f"{'=' * 60}")
        for i, team in enumerate(self.teams, 1):
            team["seed"] = i
            print(f"  Seed #{i}: {team['name']:<20} (ELO: {team['elo_rating']})")
        print(f"{'=' * 60}\n")

        return self.teams

    # ------------------------------------------------------------------
    # ELO & series win probabilities
    # ------------------------------------------------------------------

    def calculate_win_probability(self, team_a_rating: float, team_b_rating: float) -> float:
        """
        Calculate MAP win probability using ELO formula:

        P(A map win) = 1 / (1 + 10^((Rb - Ra)/400))
        """
        return 1.0 / (1.0 + 10 ** ((team_b_rating - team_a_rating) / 400.0))

    def series_win_probability(self, map_win_prob: float, best_of: int) -> float:
        """
        Given map-level win probability p, return probability that a team wins
        a best-of-N series (N odd) via the binomial distribution.
        """
        if best_of <= 1:
            return map_win_prob

        wins_needed = best_of // 2 + 1
        p = map_win_prob
        q = 1.0 - p

        series_prob = 0.0
        for k in range(wins_needed, best_of + 1):
            # C(N, k) * p^k * q^(N-k)
            series_prob += math.comb(best_of, k) * (p ** k) * (q ** (best_of - k))

        return series_prob

    # ------------------------------------------------------------------
    # Match & tournament simulation
    # ------------------------------------------------------------------

    def simulate_match(self, team_a: Dict[str, Any], team_b: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simulate a single match between two teams.

        - Base Elo from team['elo_rating']
        - Optional performance noise: N(0, self.elo_sigma)
        - Compute map-level win prob via Elo
        - Elevate to series probability via series_win_probability
        """
        ra = team_a["elo_rating"]
        rb = team_b["elo_rating"]

        # Add performance variance if enabled
        if self.elo_sigma is not None and self.elo_sigma > 0:
            ra += random.gauss(0, self.elo_sigma)
            rb += random.gauss(0, self.elo_sigma)

        map_prob_a = self.calculate_win_probability(ra, rb)
        p_a_series = self.series_win_probability(map_prob_a, self.best_of)

        return team_a if random.random() < p_a_series else team_b

    def get_round_name(self, teams_remaining: int) -> str:
        """Get human-readable round name."""
        if teams_remaining == 2:
            return "Finals"
        elif teams_remaining == 4:
            return "Semifinals"
        elif teams_remaining == 8:
            return "Quarterfinals"
        elif teams_remaining == 16:
            return "Round_of_16"
        else:
            return f"Round_of_{teams_remaining}"

    def track_advancement(
        self,
        teams_remaining: int,
        remaining_teams: List[Dict[str, Any]],
    ) -> None:
        """
        Record that these teams reached this round in simulation_results.
        """
        round_name = self.get_round_name(teams_remaining)
        key = f"reached_{round_name}"

        for team in remaining_teams:
            self.simulation_results[team["name"]][key] += 1

    def simulate_tournament_with_tracking(self) -> Dict[str, Any]:
        remaining_teams = self.teams.copy()

        while len(remaining_teams) > 1:

            self.track_advancement(len(remaining_teams), remaining_teams)
            
            next_round_teams = []
            for i in range(0, len(remaining_teams), 2):
                team_a = remaining_teams[i]
                team_b = remaining_teams[i + 1]
                winner = self.simulate_match(team_a, team_b)
                next_round_teams.append(winner)
            
            remaining_teams = next_round_teams
        
        champion = remaining_teams[0]
        self.simulation_results[champion["name"]]["championships"] += 1

        return {"champion": champion}

    def run_simulation(self, n: int = 10000) -> List[Dict[str, Any]]:
        """
        Run Monte Carlo tournament simulation n times.

        Returns:
            Per-team statistics (list of dicts).
        """
        self.simulation_results = defaultdict(lambda: defaultdict(int))

        print(
            f"Running {n:,} simulations (best-of-{self.best_of}, "
            f"Elo sigma={self.elo_sigma})..."
        )
        for _ in range(n):
            self.simulate_tournament_with_tracking()

        stats = self.calculate_statistics(n)
        return stats

    def calculate_statistics(self, total_simulations: int) -> List[Dict[str, Any]]:
        """
        Convert raw counts in simulation_results to percentages.
        """
        stats: List[Dict[str, Any]] = []

        for team in self.teams:
            name = team["name"]
            results = self.simulation_results[name]

            def pct(key: str) -> float:
                return round(
                    100.0 * results.get(key, 0) / total_simulations, 2
                )

            team_stats = {
                "name": name,
                "seed": team.get("seed"),
                "elo_rating": team["elo_rating"],
                "championship_prob": pct("championships"),
                "finals_prob": pct("reached_Finals"),
                "semifinals_prob": pct("reached_Semifinals"),
                "quarterfinals_prob": pct("reached_Quarterfinals"),
                "round_of_16_prob": pct("reached_Round_of_16"),
            }
            stats.append(team_stats)

        # Sort by championship probability descending
        stats.sort(key=lambda t: t["championship_prob"], reverse=True)
        return stats

    # ------------------------------------------------------------------
    # Output / display
    # ------------------------------------------------------------------

    def display_results(self, stats: List[Dict[str, Any]]) -> None:
        """Pretty-print simulation results to the console."""
        print("\nSIMULATION RESULTS (sorted by championship probability):")
        print(
            f"{'Team':<20} {'Seed':<4} {'ELO':<6} "
            f"{'Win%':>7} {'Finals%':>9} {'Semis%':>9} {'Quarters%':>10}"
        )
        print("-" * 70)

        for row in stats:
            print(
                f"{row['name']:<20} "
                f"{str(row['seed']):<4} "
                f"{row['elo_rating']:<6.1f} "
                f"{row['championship_prob']:>6.2f}% "
                f"{row['finals_prob']:>8.2f}% "
                f"{row['semifinals_prob']:>8.2f}% "
                f"{row['quarterfinals_prob']:>9.2f}%"
            )

        print("")

    def save_results(
        self,
        stats: List[Dict[str, Any]],
        filename: str = "simulation_results.json",
        *,
        tournament_format: str = "Single Elimination",
    ) -> None:
        """
        Save simulation stats to a JSON file in a structure compatible with
        live_simulation_results.json.
        """
        output = {
            "tournament_format": tournament_format,
            "team_count": len(self.teams),
            "teams": stats,
            "timestamp": None,  # JSON null
        }

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2)

        print(f"✓ Results saved to {filename}")


def main() -> None:
    """Interactive CLI using static valorant_data.json."""
    print("\n" + "=" * 80)
    print(" " * 20 + "VALORANT TOURNAMENT SIMULATOR")
    print("=" * 80)

    teams_file = "valorant_data.json"
    print(f"\nUsing team file: {teams_file}")

    # Team count (optional; None = auto largest power of 2)
    count_str = input(
        "How many teams should be in the bracket? "
        "[press Enter for auto (largest power of 2)]: "
    ).strip()
    team_count: Optional[int] = int(count_str) if count_str else None

    # Match format
    print("\nMatch format:")
    print("  [1] BO1")
    print("  [2] BO3 (default)")
    print("  [3] BO5")
    fmt_choice = input("Enter choice (1/2/3) [default: 2]: ").strip()
    best_of_map = {"1": 1, "2": 3, "3": 5}
    best_of = best_of_map.get(fmt_choice, 3)

    # Elo noise
    print("\nPerformance variance (Elo sigma).")
    print("  0 = no variance (deterministic Elo)")
    print("  25–75 = realistic match-to-match fluctuation")
    sigma_str = input("Enter Elo sigma [default: 0]: ").strip()
    elo_sigma = float(sigma_str) if sigma_str else 0.0
    if elo_sigma <= 0:
        elo_sigma = None

    # Number of simulations
    sims_str = input(
        "\nNumber of simulations to run [default: 10000]: "
    ).strip()
    n_sims = int(sims_str) if sims_str else 10000

    simulator = BracketSimulator(
        teams_file=teams_file,
        best_of=best_of,
        elo_sigma=elo_sigma,
    )

    simulator.select_teams(count=team_count)
    stats = simulator.run_simulation(n=n_sims)
    simulator.display_results(stats)

    out_name = "simulation_results.json"
    simulator.save_results(stats, filename=out_name)

    print("=" * 80)
    print("Want to run another simulation? Just run the script again!")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()