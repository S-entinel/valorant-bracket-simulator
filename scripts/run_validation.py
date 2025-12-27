#!/usr/bin/env python3
"""
Run multi-tournament validation.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Change to project root so paths work
os.chdir(os.path.join(os.path.dirname(__file__), '..'))

from src.tournament_validator import main

if __name__ == "__main__":
    main()
