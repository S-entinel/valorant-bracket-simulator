"""
FastAPI Backend for Valorant Tournament Simulator
Provides REST API endpoints for running simulations and managing team data
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import json
import uuid

from .services.simulation_service import SimulationService
from .services.team_service import TeamService
from .database import init_db, get_db
from .models import SimulationStatus

# Initialize FastAPI app
app = FastAPI(
    title="Valorant Tournament Simulator API",
    description="Monte Carlo simulation engine for Valorant tournament predictions",
    version="1.0.0"
)

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React/Vite dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
simulation_service = SimulationService()
team_service = TeamService()


# Request/Response Models
class TeamResponse(BaseModel):
    """Team data response model"""
    id: str
    name: str
    region: str
    elo_rating: float
    rank: Optional[int] = None
    matches_played: Optional[int] = None


class SimulationRequest(BaseModel):
    """Request model for running a simulation"""
    team_ids: List[str] = Field(..., min_length=2, max_length=32)
    num_simulations: int = Field(default=10000, ge=100, le=100000)
    best_of: int = Field(default=3, ge=1, le=5)
    elo_sigma: Optional[float] = Field(default=None, ge=0, le=200)
    tournament_format: str = Field(default="single_elimination")


class SimulationResponse(BaseModel):
    """Response model for simulation results"""
    simulation_id: str
    status: str
    created_at: datetime
    teams_count: int
    num_simulations: int
    best_of: int
    results: Optional[List[Dict[str, Any]]] = None
    metadata: Optional[Dict[str, Any]] = None


class ValidationRequest(BaseModel):
    """Request model for historical validation"""
    tournament_name: str
    actual_winner: str
    training_matches: List[Dict[str, Any]]
    tournament_teams: List[str]


# Database initialization
@app.on_event("startup")
async def startup():
    """Initialize database on startup"""
    init_db()
    print("✓ Database initialized")
    print("✓ FastAPI backend ready")


# Health check endpoint
@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "Valorant Tournament Simulator API",
        "version": "1.0.0"
    }


# Team endpoints
@app.get("/api/teams", response_model=List[TeamResponse])
async def get_teams(
    region: Optional[str] = None,
    min_rating: Optional[float] = None,
    max_rating: Optional[float] = None,
    limit: Optional[int] = None
):
    """
    Get list of teams with optional filtering
    
    Query Parameters:
    - region: Filter by region (e.g., "Americas", "EMEA", "Pacific", "China")
    - min_rating: Minimum ELO rating
    - max_rating: Maximum ELO rating
    - limit: Maximum number of teams to return
    """
    try:
        teams = team_service.get_teams(
            region=region,
            min_rating=min_rating,
            max_rating=max_rating,
            limit=limit
        )
        return teams
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/teams/{team_id}", response_model=TeamResponse)
async def get_team(team_id: str):
    """Get a single team by ID"""
    try:
        team = team_service.get_team_by_id(team_id)
        if not team:
            raise HTTPException(status_code=404, detail=f"Team {team_id} not found")
        return team
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/teams/refresh")
async def refresh_teams(background_tasks: BackgroundTasks):
    """
    Refresh team data from VLR.gg
    This runs in the background and returns immediately
    """
    try:
        background_tasks.add_task(team_service.refresh_team_data)
        return {
            "status": "started",
            "message": "Team data refresh initiated in background"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Simulation endpoints
@app.post("/api/simulate", response_model=SimulationResponse)
async def run_simulation(request: SimulationRequest):
    """
    Run a tournament simulation
    
    Body Parameters:
    - team_ids: List of team IDs to include in bracket (2-32 teams)
    - num_simulations: Number of Monte Carlo iterations (100-100,000)
    - best_of: Match format (1, 3, or 5)
    - elo_sigma: Performance variance (optional, 0-200)
    - tournament_format: "single_elimination" (double-elim coming soon)
    """
    try:
        # Validate teams exist
        teams = []
        for team_id in request.team_ids:
            team = team_service.get_team_by_id(team_id)
            if not team:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Team {team_id} not found"
                )
            teams.append(team)
        
        # Run simulation
        result = simulation_service.run_simulation(
            teams=teams,
            num_simulations=request.num_simulations,
            best_of=request.best_of,
            elo_sigma=request.elo_sigma,
            tournament_format=request.tournament_format
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/simulations/{simulation_id}", response_model=SimulationResponse)
async def get_simulation(simulation_id: str):
    """Get simulation results by ID"""
    try:
        result = simulation_service.get_simulation(simulation_id)
        if not result:
            raise HTTPException(
                status_code=404, 
                detail=f"Simulation {simulation_id} not found"
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/simulations", response_model=List[SimulationResponse])
async def list_simulations(limit: int = 10, offset: int = 0):
    """List recent simulations"""
    try:
        results = simulation_service.list_simulations(limit=limit, offset=offset)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/simulations/{simulation_id}")
async def delete_simulation(simulation_id: str):
    """Delete a simulation by ID"""
    try:
        success = simulation_service.delete_simulation(simulation_id)
        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"Simulation {simulation_id} not found"
            )
        return {"status": "deleted", "simulation_id": simulation_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Validation endpoints
@app.post("/api/validate")
async def run_validation(request: ValidationRequest):
    """
    Run historical tournament validation
    
    Body Parameters:
    - tournament_name: Name of the tournament
    - actual_winner: Team that actually won
    - training_matches: Historical match data for ELO calculation
    - tournament_teams: List of team names in the tournament
    """
    try:
        result = simulation_service.run_validation(
            tournament_name=request.tournament_name,
            actual_winner=request.actual_winner,
            training_matches=request.training_matches,
            tournament_teams=request.tournament_teams
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Statistics endpoints
@app.get("/api/stats/summary")
async def get_stats_summary():
    """Get overall statistics summary"""
    try:
        total_teams = team_service.get_team_count()
        total_simulations = simulation_service.get_simulation_count()
        
        return {
            "total_teams": total_teams,
            "total_simulations": total_simulations,
            "avg_elo": team_service.get_average_elo(),
            "regions": team_service.get_region_distribution()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
