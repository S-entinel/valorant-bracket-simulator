#!/usr/bin/env python3
"""
Calculate ELO ratings from match history and save to JSON.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import argparse
import json
from src.elo_calculator import ELOCalculator


def main():
    parser = argparse.ArgumentParser(description='Calculate ELO ratings from match history')
    parser.add_argument('matches_file', help='Path to matches JSON file')
    parser.add_argument('-o', '--output', default='../data/team_ratings.json', 
                        help='Output file for ratings (default: ../data/team_ratings.json)')
    parser.add_argument('-k', '--k-factor', type=int, default=32,
                        help='ELO K-factor (default: 32)')
    parser.add_argument('-i', '--initial-rating', type=float, default=1500.0,
                        help='Initial rating (default: 1500.0)')
    parser.add_argument('--binary', action='store_true',
                        help='Use binary scoring instead of map-based')
    parser.add_argument('-n', '--top-n', type=int,
                        help='Only show top N teams')
    
    args = parser.parse_args()
    
    print("Initializing ELO Calculator...")
    print(f"  K-factor: {args.k_factor}")
    print(f"  Initial rating: {args.initial_rating}")
    print(f"  Scoring: {'Binary' if args.binary else 'Map-based'}")
    
    # Load matches
    print(f"Loading matches from {args.matches_file}...")
    with open(args.matches_file, 'r') as f:
        data = json.load(f)
    
    matches = data.get('matches', [])
    
    # Calculate ELO
    calc = ELOCalculator(
        k_factor=args.k_factor,
        initial_rating=args.initial_rating,
        use_map_score=not args.binary
    )
    
    calc.process_matches(matches)
    
    print(f"Processed {len(matches)} matches")
    print(f"Calculated ratings for {len(calc.teams)} teams")
    
    # Display results
    calc.print_ratings(top_n=args.top_n)
    
    # Save
    print(f"Saving ratings to {args.output}...")
    calc.save_ratings(args.output)
    print(f"✓ Ratings saved to {args.output}")
    
    print(f"\n✅ Done! You can now use these ratings with bracket_simulator.py:")
    print(f"   python scripts/main.py")


if __name__ == "__main__":
    main()
