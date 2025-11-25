from bracket_simulator import BracketSimulator

def main():
    """Run simulator with live VLR.gg data"""
    print("\n" + "="*80)
    print(" " * 15 + "VALORANT TOURNAMENT SIMULATOR - LIVE VLR.gg DATA")
    print("="*80)
    
    # Initialize with live data
    simulator = BracketSimulator('valorant_data_live.json')
    
    print("\nYou have 10 teams from live VLR.gg World Rankings!")
    print("We'll run an 8-team single elimination tournament.\n")
    
    # Select top 8 teams
    simulator.select_teams(count=8)
    
    # Run 10,000 simulations
    print("\nRunning 10,000 simulations...")
    stats = simulator.run_simulation(n=10000)
    
    # Display results
    simulator.display_results(stats)
    
    # Save results
    simulator.save_results(stats, filename='live_simulation_results.json')
    
    print("="*80)
    print("✓ Simulation complete with LIVE VLR.gg data!")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()