# run_simulator_live.py
from bracket_simulator import BracketSimulator


def main() -> None:
    """Run simulator with live VLR.gg data (from valorant_data_live.json)."""
    print("\n" + "=" * 80)
    print(" " * 15 + "VALORANT TOURNAMENT SIMULATOR - LIVE VLR.gg DATA")
    print("=" * 80)

    # Live data scraped via vlr_http_scraper.py
    teams_file = "valorant_data_live.json"

    # Live settings: BO3 with moderate Elo variance
    simulator = BracketSimulator(
        teams_file=teams_file,
        best_of=3,       # BO3 (typical)
        elo_sigma=50.0,  # ~1 map swing on a good/bad day
    )

    print("\nUsing live world rankings from:", teams_file)
    print("We’ll run a 16-team single elimination bracket.\n")

    simulator.select_teams(count=16)

    n_sims = 10000
    stats = simulator.run_simulation(n=n_sims)

    simulator.display_results(stats)
    simulator.save_results(stats, filename="live_simulation_results.json")

    print("=" * 80)
    print("✓ Simulation complete with LIVE VLR.gg data!")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
