import json
import os
from typing import List, Dict, Any

import matplotlib.pyplot as plt


def load_results(filename: str = "live_simulation_results.json") -> List[Dict[str, Any]]:
    """Load simulation results JSON and return the list of team stats."""
    if not os.path.exists(filename):
        raise FileNotFoundError(
            f"Could not find {filename}. "
            f"Run run_simulator_live.py first to generate it."
        )

    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)

    teams = data.get("teams", [])
    if not teams:
        raise ValueError(f"No 'teams' data in {filename}.")

    return teams


def plot_championship_probabilities(
    teams: List[Dict[str, Any]],
    output_image: str = "live_results.png",
) -> None:
    """
    Plot a bar chart of championship probabilities for each team.

    Teams are sorted descending by championship_prob.
    """
    # Sort by win probability
    teams_sorted = sorted(
        teams, key=lambda t: t.get("championship_prob", 0.0), reverse=True
    )

    names = [t["name"] for t in teams_sorted]
    probs = [t.get("championship_prob", 0.0) for t in teams_sorted]

    plt.figure(figsize=(12, 6))
    bars = plt.bar(range(len(names)), probs)

    plt.xticks(range(len(names)), names, rotation=45, ha="right")
    plt.ylabel("Championship Probability (%)")
    plt.title("Valorant Tournament – Championship Odds (Live VLR.gg Data)")

    # Annotate bars with exact percentages
    for bar, p in zip(bars, probs):
        height = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            height,
            f"{p:.2f}%",
            ha="center",
            va="bottom",
            fontsize=8,
        )

    plt.tight_layout()
    plt.savefig(output_image, dpi=150)
    print(f"✓ Saved plot to {output_image}")
    plt.show()


def main() -> None:
    print("\nLoading simulation results from live_simulation_results.json...")
    teams = load_results("live_simulation_results.json")
    print(f"Found {len(teams)} teams. Plotting championship probabilities...\n")
    plot_championship_probabilities(teams)


if __name__ == "__main__":
    main()
