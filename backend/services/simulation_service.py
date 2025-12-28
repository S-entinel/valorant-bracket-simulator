"""
Simulation Service - Handles tournament simulation operations
"""

import json
import sys
import os
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
import tempfile

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from ..database import SessionLocal, Simulation, ValidationRun, SimulationStatus
from src.bracket_simulator import BracketSimulator
from src.tournament_validator import (
    calculate_elo_from_matches,
    predict_tournament_winner,
    get_tournament_teams
)


class SimulationService:
    """Service for managing tournament simulations"""
    
    def __init__(self):
        self.db = SessionLocal()
    
    def run_simulation(
        self,
        teams: List[Dict[str, Any]],
        num_simulations: int = 10000,
        best_of: int = 3,
        elo_sigma: Optional[float] = None,
        tournament_format: str = "single_elimination"
    ) -> Dict[str, Any]:
        """
        Run a tournament simulation
        
        Args:
            teams: List of team dictionaries
            num_simulations: Number of Monte Carlo iterations
            best_of: Match format (1, 3, or 5)
            elo_sigma: Performance variance
            tournament_format: Tournament type
            
        Returns:
            Simulation results dictionary
        """
        # Generate simulation ID
        simulation_id = str(uuid.uuid4())
        
        # Create simulation record
        sim = Simulation(
            id=simulation_id,
            status=SimulationStatus.PENDING,
            tournament_format=tournament_format,
            teams_count=len(teams),
            num_simulations=num_simulations,
            best_of=best_of,
            elo_sigma=elo_sigma
        )
        
        self.db.add(sim)
        self.db.commit()
        
        try:
            # Update status to running
            sim.status = SimulationStatus.RUNNING
            sim.started_at = datetime.utcnow()
            self.db.commit()
            
            # Create temporary teams file for BracketSimulator
            teams_data = {
                "teams": teams,
                "metadata": {
                    "source": "api",
                    "team_count": len(teams)
                }
            }
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(teams_data, f)
                temp_file = f.name
            
            try:
                # Run simulation using existing BracketSimulator
                simulator = BracketSimulator(
                    teams_file=temp_file,
                    best_of=best_of,
                    elo_sigma=elo_sigma
                )
                
                # Select all teams (they're already filtered)
                simulator.teams = teams
                for i, team in enumerate(simulator.teams, 1):
                    team['seed'] = i
                
                # Run simulation
                results = simulator.run_simulation(n=num_simulations)
                
                # Store results
                sim.results = json.dumps(results)
                sim.sim_metadata = json.dumps({
                    "simulator_version": "1.0",
                    "created_via": "api"
                })
                sim.status = SimulationStatus.COMPLETED
                sim.completed_at = datetime.utcnow()
                self.db.commit()
                
                return self._simulation_to_dict(sim, include_results=True)
                
            finally:
                # Clean up temp file
                if os.path.exists(temp_file):
                    os.remove(temp_file)
        
        except Exception as e:
            # Mark as failed
            sim.status = SimulationStatus.FAILED
            sim.error_message = str(e)
            sim.completed_at = datetime.utcnow()
            self.db.commit()
            raise
    
    def get_simulation(self, simulation_id: str) -> Optional[Dict[str, Any]]:
        """Get simulation by ID"""
        sim = self.db.query(Simulation).filter(Simulation.id == simulation_id).first()
        if sim:
            return self._simulation_to_dict(sim, include_results=True)
        return None
    
    def list_simulations(self, limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
        """List recent simulations"""
        sims = self.db.query(Simulation)\
            .order_by(Simulation.created_at.desc())\
            .limit(limit)\
            .offset(offset)\
            .all()
        
        return [self._simulation_to_dict(sim) for sim in sims]
    
    def delete_simulation(self, simulation_id: str) -> bool:
        """Delete a simulation"""
        sim = self.db.query(Simulation).filter(Simulation.id == simulation_id).first()
        if not sim:
            return False
        
        self.db.delete(sim)
        self.db.commit()
        return True
    
    def get_simulation_count(self) -> int:
        """Get total number of simulations"""
        return self.db.query(Simulation).count()
    
    def run_validation(
        self,
        tournament_name: str,
        actual_winner: str,
        training_matches: List[Dict[str, Any]],
        tournament_teams: List[str]
    ) -> Dict[str, Any]:
        """
        Run historical tournament validation
        
        Args:
            tournament_name: Name of the tournament
            actual_winner: Team that actually won
            training_matches: Historical match data
            tournament_teams: Teams in the tournament
            
        Returns:
            Validation results dictionary
        """
        validation_id = str(uuid.uuid4())
        
        try:
            # Calculate ELO from training matches
            team_ratings = calculate_elo_from_matches(training_matches)
            
            # Run predictions
            predictions = predict_tournament_winner(
                team_ratings,
                tournament_teams,
                n_simulations=5000
            )
            
            if not predictions:
                raise ValueError("No predictions generated")
            
            # Sort predictions
            sorted_predictions = sorted(
                predictions.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            predicted_winner = sorted_predictions[0][0]
            predicted_prob = sorted_predictions[0][1]
            
            actual_winner_prob = predictions.get(actual_winner, 0.0)
            actual_winner_rank = next(
                (i + 1 for i, (name, _) in enumerate(sorted_predictions) if name == actual_winner),
                None
            )
            
            correct = predicted_winner == actual_winner
            
            # Store validation
            validation = ValidationRun(
                id=validation_id,
                tournament_name=tournament_name,
                actual_winner=actual_winner,
                predicted_winner=predicted_winner,
                correct_prediction=1 if correct else 0,
                actual_winner_rank=actual_winner_rank,
                actual_winner_probability=actual_winner_prob,
                results=json.dumps({
                    "predictions": sorted_predictions[:10],
                    "training_matches_count": len(training_matches),
                    "tournament_teams_count": len(tournament_teams)
                })
            )
            
            self.db.add(validation)
            self.db.commit()
            
            return {
                "validation_id": validation_id,
                "tournament_name": tournament_name,
                "predicted_winner": predicted_winner,
                "predicted_probability": predicted_prob,
                "actual_winner": actual_winner,
                "actual_winner_probability": actual_winner_prob,
                "actual_winner_rank": actual_winner_rank,
                "correct_prediction": correct,
                "top_5_predictions": sorted_predictions[:5]
            }
        
        except Exception as e:
            raise ValueError(f"Validation failed: {str(e)}")
    
    def _simulation_to_dict(
        self,
        sim: Simulation,
        include_results: bool = False
    ) -> Dict[str, Any]:
        """Convert Simulation model to dictionary"""
        data = {
            'simulation_id': sim.id,
            'status': sim.status.value,
            'tournament_format': sim.tournament_format.value,
            'teams_count': sim.teams_count,
            'num_simulations': sim.num_simulations,
            'best_of': sim.best_of,
            'elo_sigma': sim.elo_sigma,
            'created_at': sim.created_at.isoformat() if sim.created_at else None,
            'started_at': sim.started_at.isoformat() if sim.started_at else None,
            'completed_at': sim.completed_at.isoformat() if sim.completed_at else None,
            'error_message': sim.error_message
        }
        
        if include_results and sim.results:
            data['results'] = json.loads(sim.results)
        
        if sim.sim_metadata:
            data['metadata'] = json.loads(sim.sim_metadata)
        
        return data