import json
import random
from collections import defaultdict
import math

class BracketSimulator:
    def __init__(self, teams_file='valorant_data.json'):
        """Initialize simulator with team data"""
        with open(teams_file, 'r') as f:
            data = json.load(f)
        
        self.all_teams = data['teams']
        self.teams = []
        self.simulation_results = defaultdict(lambda: defaultdict(int))
    
    def select_teams(self, count=8):
        """Select top N teams for the tournament"""
        self.teams = sorted(self.all_teams, key=lambda x: x['elo_rating'], reverse=True)[:count]
        print(f"\n{'='*60}")
        print(f"TOURNAMENT BRACKET: Top {count} Teams")
        print(f"{'='*60}")
        for i, team in enumerate(self.teams, 1):
            print(f"  Seed #{i}: {team['name']:<20} (ELO: {team['elo_rating']})")
        print(f"{'='*60}\n")
        return self.teams
    
    def calculate_win_probability(self, team_a_rating, team_b_rating):
        """
        Calculate win probability using ELO formula
        P(A wins) = 1 / (1 + 10^((Rb - Ra)/400))
        """
        return 1 / (1 + 10 ** ((team_b_rating - team_a_rating) / 400))
    
    def simulate_match(self, team_a, team_b):
        """Simulate a single match between two teams"""
        prob_a_wins = self.calculate_win_probability(
            team_a['elo_rating'], 
            team_b['elo_rating']
        )
        
        # Generate random number and determine winner
        if random.random() < prob_a_wins:
            return team_a
        else:
            return team_b
    
    def simulate_single_elimination(self):
        """
        Simulate a single-elimination bracket
        Returns the champion
        """
        # Copy teams list to avoid modifying original
        remaining_teams = self.teams.copy()
        round_num = 1
        
        # Calculate total rounds
        total_rounds = int(math.log2(len(remaining_teams)))
        
        # Simulate each round until we have a champion
        while len(remaining_teams) > 1:
            next_round_teams = []
            round_name = self.get_round_name(len(remaining_teams))
            
            # Pair up teams and simulate matches
            for i in range(0, len(remaining_teams), 2):
                team_a = remaining_teams[i]
                team_b = remaining_teams[i + 1]
                
                winner = self.simulate_match(team_a, team_b)
                next_round_teams.append(winner)
            
            remaining_teams = next_round_teams
            round_num += 1
        
        # Return the champion
        return remaining_teams[0]
    
    def get_round_name(self, teams_remaining):
        """Get the name of the current round"""
        if teams_remaining == 2:
            return "Finals"
        elif teams_remaining == 4:
            return "Semifinals"
        elif teams_remaining == 8:
            return "Quarterfinals"
        else:
            return f"Round of {teams_remaining}"
    
    def track_advancement(self, teams_remaining, remaining_teams):
        """Track how far each team advanced"""
        round_name = self.get_round_name(teams_remaining)
        for team in remaining_teams:
            self.simulation_results[team['name']]['reached_' + round_name] += 1
    
    def simulate_tournament_with_tracking(self):
        """
        Simulate tournament and track each team's progression
        """
        remaining_teams = self.teams.copy()
        
        while len(remaining_teams) > 1:
            # Track advancement before eliminations
            self.track_advancement(len(remaining_teams), remaining_teams)
            
            next_round_teams = []
            
            for i in range(0, len(remaining_teams), 2):
                team_a = remaining_teams[i]
                team_b = remaining_teams[i + 1]
                winner = self.simulate_match(team_a, team_b)
                next_round_teams.append(winner)
            
            remaining_teams = next_round_teams
        
        # Track finals and champion
        champion = remaining_teams[0]
        self.track_advancement(1, [champion])
        
        return champion
    
    def run_simulation(self, n=10000):
        """
        Run Monte Carlo simulation N times
        """
        print(f"Running {n:,} simulations...")
        print("Progress: ", end="", flush=True)
        
        # Reset results
        self.simulation_results = defaultdict(lambda: defaultdict(int))
        
        progress_interval = n // 20  # Update 20 times
        
        for i in range(n):
            champion = self.simulate_tournament_with_tracking()
            self.simulation_results[champion['name']]['championships'] += 1
            
            # Progress indicator
            if (i + 1) % progress_interval == 0:
                print("▓", end="", flush=True)
        
        print(" ✓ Complete!\n")
        
        return self.calculate_statistics(n)
    
    def calculate_statistics(self, total_simulations):
        """Calculate final statistics from simulation results"""
        stats = []
        
        for team in self.teams:
            team_name = team['name']
            results = self.simulation_results[team_name]
            
            team_stats = {
                'name': team_name,
                'seed': self.teams.index(team) + 1,
                'elo_rating': team['elo_rating'],
                'championship_prob': (results['championships'] / total_simulations) * 100,
                'finals_prob': 0,
                'semifinals_prob': 0,
                'quarterfinals_prob': 0
            }
            
            # Calculate probabilities for each round
            if len(self.teams) >= 2:
                team_stats['finals_prob'] = (results.get('reached_Finals', 0) / total_simulations) * 100
            if len(self.teams) >= 4:
                team_stats['semifinals_prob'] = (results.get('reached_Semifinals', 0) / total_simulations) * 100
            if len(self.teams) >= 8:
                team_stats['quarterfinals_prob'] = (results.get('reached_Quarterfinals', 0) / total_simulations) * 100
            
            stats.append(team_stats)
        
        # Sort by championship probability
        stats.sort(key=lambda x: x['championship_prob'], reverse=True)
        
        return stats
    
    def display_results(self, stats):
        """Display simulation results in a formatted table"""
        print(f"\n{'='*80}")
        print(f"SIMULATION RESULTS ({len(self.teams)}-Team Single Elimination)")
        print(f"{'='*80}\n")
        
        # Header
        print(f"{'Rank':<6}{'Team':<20}{'Seed':<6}{'ELO':<8}{'Win %':<10}", end="")
        
        if len(self.teams) >= 8:
            print(f"{'QF %':<10}", end="")
        if len(self.teams) >= 4:
            print(f"{'SF %':<10}", end="")
        if len(self.teams) >= 2:
            print(f"{'Finals %':<10}")
        else:
            print()
        
        print("-" * 80)
        
        # Results
        for i, team_stat in enumerate(stats, 1):
            print(f"{i:<6}{team_stat['name']:<20}#{team_stat['seed']:<5}{team_stat['elo_rating']:<8.0f}{team_stat['championship_prob']:<9.2f}%", end="")
            
            if len(self.teams) >= 8:
                print(f"{team_stat['quarterfinals_prob']:<9.2f}%", end="")
            if len(self.teams) >= 4:
                print(f"{team_stat['semifinals_prob']:<9.2f}%", end="")
            if len(self.teams) >= 2:
                print(f"{team_stat['finals_prob']:<9.2f}%")
            else:
                print()
        
        print(f"\n{'='*80}\n")
        
        # Key insights
        print("KEY INSIGHTS:")
        print(f"  • Most likely champion: {stats[0]['name']} ({stats[0]['championship_prob']:.1f}%)")
        print(f"  • Biggest underdog with chance: {stats[-1]['name']} ({stats[-1]['championship_prob']:.2f}%)")
        
        # Calculate upset potential
        top_seed_stats = next(s for s in stats if s['seed'] == 1)
        print(f"  • Top seed ({top_seed_stats['name']}) win probability: {top_seed_stats['championship_prob']:.1f}%")
        print()
    
    def save_results(self, stats, filename='simulation_results.json'):
        """Save results to JSON file"""
        output = {
            'tournament_format': 'Single Elimination',
            'team_count': len(self.teams),
            'teams': stats,
            'timestamp': json.dumps(None)
        }
        
        with open(filename, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"✓ Results saved to {filename}\n")


def main():
    """Main function to run the simulator"""
    print("\n" + "="*80)
    print(" " * 20 + "VALORANT TOURNAMENT BRACKET SIMULATOR")
    print("="*80)
    
    # Initialize simulator
    simulator = BracketSimulator('valorant_data.json')
    
    # Select teams for tournament
    print("\nHow many teams for the tournament?")
    print("  [8] 8 teams (Quarterfinals start)")
    print("  [16] 16 teams (Round of 16 start)")
    
    choice = input("\nEnter choice (8 or 16) [default: 8]: ").strip()
    team_count = 16 if choice == '16' else 8
    
    simulator.select_teams(count=team_count)
    
    # Get simulation count
    print("How many simulations to run?")
    print("  [1] 1,000 simulations (fast, less accurate)")
    print("  [2] 10,000 simulations (recommended)")
    print("  [3] 50,000 simulations (slow, most accurate)")
    
    sim_choice = input("\nEnter choice (1/2/3) [default: 2]: ").strip()
    
    sim_counts = {'1': 1000, '2': 10000, '3': 50000}
    n_simulations = sim_counts.get(sim_choice, 10000)
    
    # Run simulation
    print()
    stats = simulator.run_simulation(n=n_simulations)
    
    # Display results
    simulator.display_results(stats)
    
    # Save results
    simulator.save_results(stats)
    
    print("="*80)
    print("Want to run another simulation? Just run the script again!")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()