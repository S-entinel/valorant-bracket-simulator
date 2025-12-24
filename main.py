import argparse
from bracket_simulator import BracketSimulator
from vlr_http_scraper import ValorantHTTPScraper
from historical_validation import HistoricalValidator

def main():
    parser = argparse.ArgumentParser(description="Valorant Tournament Simulator")
    subparsers = parser.add_subparsers(dest="command")
    
    # Scrape command
    scrape_parser = subparsers.add_parser("scrape", help="Scrape live VLR data")
    scrape_parser.add_argument("--limit", type=int, default=16)
    
    # Simulate command
    sim_parser = subparsers.add_parser("simulate", help="Run tournament simulation")
    sim_parser.add_argument("--teams", type=int, default=8)
    sim_parser.add_argument("--sims", type=int, default=10000)
    sim_parser.add_argument("--best-of", type=int, default=3)
    
    # Validate command
    val_parser = subparsers.add_parser("validate", help="Historical validation")
    val_parser.add_argument("--sims", type=int, default=10000)
    
    args = parser.parse_args()
    
    if args.command == "scrape":
        scraper = ValorantHTTPScraper()
        scraper.get_top_teams(limit=args.limit)
        scraper.save_data()
        
    elif args.command == "simulate":
        sim = BracketSimulator("teams_data.json", best_of=args.best_of)
        sim.select_teams(count=args.teams)
        stats = sim.run_simulation(n=args.sims)
        sim.print_statistics(stats)
        
    elif args.command == "validate":
        validator = HistoricalValidator()
        result = validator.run_validation(n_simulations=args.sims)
        validator.print_validation_report(result)

if __name__ == "__main__":
    main()