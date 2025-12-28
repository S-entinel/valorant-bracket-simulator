#!/usr/bin/env python3
"""
Startup script for Valorant Tournament Simulator API
Run with: python run_backend.py
"""

import sys
import os
import uvicorn

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

from backend.main import app
from backend.database import init_db
from backend.services.team_service import TeamService

def initialize_data():
    """Initialize database and load initial team data"""
    print("\n" + "=" * 70)
    print(" " * 15 + "VALORANT TOURNAMENT SIMULATOR API")
    print("=" * 70)
    
    # Initialize database
    print("\n[1/3] Initializing database...")
    init_db()
    print("✓ Database tables created")
    
    # Load team data
    print("\n[2/3] Loading team data...")
    team_service = TeamService()
    team_service.refresh_team_data()
    
    team_count = team_service.get_team_count()
    avg_elo = team_service.get_average_elo()
    
    print(f"✓ Loaded {team_count} teams")
    print(f"✓ Average ELO: {avg_elo}")
    
    print("\n[3/3] Starting API server...")
    print("=" * 70)
    print("\nAPI Documentation: http://localhost:8000/docs")
    print("API Status: http://localhost:8000")
    print("\nPress CTRL+C to stop the server")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    # Initialize
    initialize_data()
    
    # Run server
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
