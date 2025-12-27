#!/usr/bin/env python3
"""
Main entry point for running tournament simulations.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.bracket_simulator import BracketSimulator


def main():
    """Run a tournament simulation with the current team ratings."""
    
    # Use ratings from data directory
    teams_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'team_ratings.json')
    
    print("\n" + "=" * 70)
    print("VALORANT TOURNAMENT BRACKET SIMULATOR")
    print("=" * 70)
    
    # Create simulator
    sim = BracketSimulator(teams_file, best_of=3)
    
    # Select teams (8-team bracket)
    print("\nSelecting top 8 teams for bracket...")
    teams = sim.select_teams(count=8)
    
    print("\nSelected Teams:")
    for team in teams:
        print(f"  {team['seed']}. {team['name']:25} (ELO: {team['elo_rating']:.1f})")
    
    # Run simulation
    print(f"\nRunning 10,000 simulations...")
    stats = sim.run_simulation(n=10000)
    
    # Display results
    print("\n" + "=" * 70)
    print("TOURNAMENT PREDICTION RESULTS")
    print("=" * 70)
    
    sim.display_results(stats)
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
