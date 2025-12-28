"""Backend package initialization"""
from .database import init_db, get_db
from .main import app

__all__ = ['app', 'init_db', 'get_db']
