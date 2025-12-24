"""
CLI tool to calculate ELO ratings from VCT match history.

Usage:
    # Step 1: Scrape matches (optional - we can provide pre-scraped data)
    python vct_match_scraper.py
    
    # Step 2: Calculate ELO ratings
    python calculate_elo_ratings.py vct_matches_2024.json
    
    # This will:
    # - Load match history
    # - Calculate ELO ratings
    # - Save to team_ratings.json (compatible with bracket_simulator.py)
    # - Print ratings table
"""

import argparse
import sys
from elo_calculator import ELOCalculator


def main():
    parser = argparse.ArgumentParser(
        description="Calculate ELO ratings from VCT match history"
    )
    
    parser.add_argument(
        "matches_file",
        nargs="?",
        default="vct_matches_2024.json",
        help="JSON file with match data (default: vct_matches_2024.json)"
    )
    
    parser.add_argument(
        "-k", "--k-factor",
        type=int,
        default=32,
        help="ELO K-factor (default: 32)"
    )
    
    parser.add_argument(
        "-i", "--initial-rating",
        type=float,
        default=1500.0,
        help="Initial rating for all teams (default: 1500.0)"
    )
    
    parser.add_argument(
        "-o", "--output",
        default="team_ratings.json",
        help="Output file for calculated ratings (default: team_ratings.json)"
    )
    
    parser.add_argument(
        "--binary-scores",
        action="store_true",
        help="Use binary win/loss instead of map scores"
    )
    
    parser.add_argument(
        "-n", "--top",
        type=int,
        default=None,
        help="Show only top N teams (default: show all)"
    )
    
    args = parser.parse_args()
    
    # Create calculator
    print(f"\nInitializing ELO Calculator...")
    print(f"  K-factor: {args.k_factor}")
    print(f"  Initial rating: {args.initial_rating}")
    print(f"  Scoring: {'Binary (win/loss)' if args.binary_scores else 'Map-based'}")
    
    calc = ELOCalculator(
        k_factor=args.k_factor,
        initial_rating=args.initial_rating,
        use_map_scores=not args.binary_scores
    )
    
    # Load and process matches
    try:
        print(f"\nLoading matches from {args.matches_file}...")
        calc.load_from_file(args.matches_file)
    except FileNotFoundError:
        print(f"\nError: File '{args.matches_file}' not found.")
        print("\nTo scrape match data, run:")
        print("  python vct_match_scraper.py")
        sys.exit(1)
    except Exception as e:
        print(f"\nError loading match data: {e}")
        sys.exit(1)
    
    # Print ratings
    calc.print_ratings(top_n=args.top)
    
    # Save to file
    print(f"Saving ratings to {args.output}...")
    calc.save_ratings(filename=args.output)
    
    print("\n✅ Done! You can now use these ratings with bracket_simulator.py:")
    print(f"   python bracket_simulator.py --teams-file {args.output}")
    print()


if __name__ == "__main__":
    main()