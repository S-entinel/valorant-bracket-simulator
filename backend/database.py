"""
Database configuration and models using SQLAlchemy
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import enum
import os

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./valorant_simulator.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Enums
class SimulationStatus(str, enum.Enum):
    """Simulation status enum"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class TournamentFormat(str, enum.Enum):
    """Tournament format enum"""
    SINGLE_ELIMINATION = "single_elimination"
    DOUBLE_ELIMINATION = "double_elimination"
    SWISS = "swiss"


# Database Models
class Team(Base):
    """Team model"""
    __tablename__ = "teams"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    region = Column(String, nullable=False, index=True)
    elo_rating = Column(Float, nullable=False, default=1500.0)
    vlr_rating = Column(String, nullable=True)
    rank = Column(Integer, nullable=True)
    matches_played = Column(Integer, default=0)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)


class Simulation(Base):
    """Simulation run model"""
    __tablename__ = "simulations"
    
    id = Column(String, primary_key=True, index=True)
    status = Column(SQLEnum(SimulationStatus), default=SimulationStatus.PENDING)
    tournament_format = Column(SQLEnum(TournamentFormat), default=TournamentFormat.SINGLE_ELIMINATION)
    
    # Simulation parameters
    teams_count = Column(Integer, nullable=False)
    num_simulations = Column(Integer, nullable=False)
    best_of = Column(Integer, default=3)
    elo_sigma = Column(Float, nullable=True)
    
    # Results stored as JSON
    results = Column(Text, nullable=True)  # JSON string
    sim_metadata = Column(Text, nullable=True)  # JSON string
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Error tracking
    error_message = Column(Text, nullable=True)


class ValidationRun(Base):
    """Historical validation run model"""
    __tablename__ = "validations"
    
    id = Column(String, primary_key=True, index=True)
    tournament_name = Column(String, nullable=False)
    actual_winner = Column(String, nullable=False)
    predicted_winner = Column(String, nullable=True)
    
    # Accuracy metrics
    correct_prediction = Column(Integer, default=0)  # Boolean as int
    actual_winner_rank = Column(Integer, nullable=True)
    actual_winner_probability = Column(Float, nullable=True)
    
    # Results
    results = Column(Text, nullable=True)  # JSON string
    
    created_at = Column(DateTime, default=datetime.utcnow)


# Database initialization
def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Get database session (dependency injection for FastAPI)"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Export all models and functions
__all__ = [
    'Base',
    'Team',
    'Simulation',
    'ValidationRun',
    'SimulationStatus',
    'TournamentFormat',
    'init_db',
    'get_db',
    'engine',
    'SessionLocal'
]