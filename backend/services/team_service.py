"""
Team Service - Handles team data operations
"""

import json
import sys
import os
from typing import List, Optional, Dict, Any
from datetime import datetime

# Add parent directory to path to import from src/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from ..database import SessionLocal, Team


class TeamService:
    """Service for managing team data"""
    
    def __init__(self):
        self.db = SessionLocal()
    
    def get_teams(
        self,
        region: Optional[str] = None,
        min_rating: Optional[float] = None,
        max_rating: Optional[float] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get teams with optional filtering
        
        Args:
            region: Filter by region
            min_rating: Minimum ELO rating
            max_rating: Maximum ELO rating
            limit: Maximum number of results
            
        Returns:
            List of team dictionaries
        """
        query = self.db.query(Team)
        
        # Apply filters
        if region:
            query = query.filter(Team.region == region)
        if min_rating is not None:
            query = query.filter(Team.elo_rating >= min_rating)
        if max_rating is not None:
            query = query.filter(Team.elo_rating <= max_rating)
        
        # Order by rating (highest first)
        query = query.order_by(Team.elo_rating.desc())
        
        # Apply limit
        if limit:
            query = query.limit(limit)
        
        teams = query.all()
        
        return [self._team_to_dict(team) for team in teams]
    
    def get_team_by_id(self, team_id: str) -> Optional[Dict[str, Any]]:
        """Get a single team by ID"""
        team = self.db.query(Team).filter(Team.id == team_id).first()
        if team:
            return self._team_to_dict(team)
        return None
    
    def get_team_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a single team by name"""
        team = self.db.query(Team).filter(Team.name == name).first()
        if team:
            return self._team_to_dict(team)
        return None
    
    def create_team(self, team_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new team"""
        team = Team(
            id=team_data.get('id'),
            name=team_data['name'],
            region=team_data['region'],
            elo_rating=team_data.get('elo_rating', 1500.0),
            vlr_rating=team_data.get('vlr_rating'),
            rank=team_data.get('rank'),
            matches_played=team_data.get('matches_played', 0)
        )
        
        self.db.add(team)
        self.db.commit()
        self.db.refresh(team)
        
        return self._team_to_dict(team)
    
    def update_team(self, team_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update team data"""
        team = self.db.query(Team).filter(Team.id == team_id).first()
        if not team:
            return None
        
        for key, value in updates.items():
            if hasattr(team, key):
                setattr(team, key, value)
        
        team.last_updated = datetime.utcnow()
        self.db.commit()
        self.db.refresh(team)
        
        return self._team_to_dict(team)
    
    def delete_team(self, team_id: str) -> bool:
        """Delete a team"""
        team = self.db.query(Team).filter(Team.id == team_id).first()
        if not team:
            return False
        
        self.db.delete(team)
        self.db.commit()
        return True
    
    def get_team_count(self) -> int:
        """Get total number of teams"""
        return self.db.query(Team).count()
    
    def get_average_elo(self) -> float:
        """Get average ELO rating across all teams"""
        from sqlalchemy import func
        result = self.db.query(func.avg(Team.elo_rating)).scalar()
        return round(result, 2) if result else 1500.0
    
    def get_region_distribution(self) -> Dict[str, int]:
        """Get count of teams per region"""
        from sqlalchemy import func
        results = self.db.query(
            Team.region,
            func.count(Team.id)
        ).group_by(Team.region).all()
        
        return {region: count for region, count in results}
    
    def refresh_team_data(self):
        """
        Refresh team data from source files
        This loads data from the existing JSON files
        """
        # Load from team_ratings.json
        ratings_file = os.path.join(
            os.path.dirname(__file__),
            '../../data/team_ratings.json'
        )
        
        if os.path.exists(ratings_file):
            with open(ratings_file, 'r') as f:
                data = json.load(f)
                teams_data = data.get('teams', [])
                
                for team_data in teams_data:
                    # Check if team exists
                    existing = self.db.query(Team).filter(
                        Team.name == team_data['name']
                    ).first()
                    
                    if existing:
                        # Update existing team
                        self.update_team(existing.id, {
                            'elo_rating': team_data['elo_rating'],
                            'matches_played': team_data.get('matches_played', 0),
                            'rank': team_data.get('rank')
                        })
                    else:
                        # Create new team
                        self.create_team({
                            'id': team_data['id'],
                            'name': team_data['name'],
                            'region': team_data.get('region', 'Unknown'),
                            'elo_rating': team_data['elo_rating'],
                            'matches_played': team_data.get('matches_played', 0),
                            'rank': team_data.get('rank')
                        })
                
                print(f"✓ Refreshed {len(teams_data)} teams from {ratings_file}")
        else:
            print(f"⚠ Warning: {ratings_file} not found")
    
    def _team_to_dict(self, team: Team) -> Dict[str, Any]:
        """Convert Team model to dictionary"""
        return {
            'id': team.id,
            'name': team.name,
            'region': team.region,
            'elo_rating': team.elo_rating,
            'vlr_rating': team.vlr_rating,
            'rank': team.rank,
            'matches_played': team.matches_played,
            'last_updated': team.last_updated.isoformat() if team.last_updated else None,
            'created_at': team.created_at.isoformat() if team.created_at else None
        }
