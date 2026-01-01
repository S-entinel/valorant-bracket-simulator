# 🎯 Valorant Tournament Simulator

Monte Carlo simulation engine for predicting VCT tournament outcomes using ELO ratings and real match data.

[![Live Demo](https://img.shields.io/badge/demo-live-success)](https://valorant-bracket-simulator.vercel.app)
[![API](https://img.shields.io/badge/API-docs-blue)](https://valorant-simulator-api-production.up.railway.app/docs)
[![Python](https://img.shields.io/badge/python-3.11-blue)](https://www.python.org/)
[![React](https://img.shields.io/badge/react-18-61dafb)](https://reactjs.org/)

## 🔗 Live Demo

**Demo:** [https://valorant-bracket-simulator.vercel.app](https://valorant-bracket-simulator.vercel.app)

---

## 📊 Project Overview

A full-stack web application that simulates Valorant esports tournaments by:
- Running 10,000+ Monte Carlo simulations per tournament
- Using ELO ratings calculated from 387 real VCT 2024 matches
- Predicting championship probabilities for 79 professional teams
- Visualizing results with interactive charts and tournament brackets
---

## ✨ Features

### **Data-Driven Predictions**
- **387 VCT matches** analyzed from 15 tournaments (Champions, Masters, Regional Leagues)
- **79 professional teams** with ELO ratings across 4 regions
- **Real match results** from VCT 2024 season

### **Monte Carlo Simulation Engine**
- Configurable simulation count (1,000 to 100,000 iterations)
- Multiple match formats (Best-of-1, Best-of-3, Best-of-5)
- Performance variance modeling (ELO sigma)
- Single-elimination bracket simulation

### **Interactive Web Interface**
- Team selection with region filtering
- Real-time simulation controls
- Probability charts and data tables
- Tournament bracket visualization
- Export results functionality

### **Historical Validation**
- Model tested against VCT Champions 2024
- Time-series validation (trained on pre-tournament data)
---

## 🛠️ Tech Stack

### **Backend**
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - ORM for database management
- **SQLite** - Lightweight embedded database
- **Uvicorn** - ASGI server
- **Pytest** - Testing framework (94% coverage, 60/60 tests passing)

### **Frontend**
- **React 18** - UI framework
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Utility-first styling
- **Recharts** - Data visualization library
- **Axios** - HTTP client

### **Deployment**
- **Railway** - Backend hosting (Python)
- **Vercel** - Frontend hosting (React)
- **GitHub Actions** - CI/CD (auto-deploy on push)

---

## 📁 Project Structure

```
valorant-bracket-simulator/
├── backend/                   # FastAPI backend
│   ├── main.py               # Application entry point
│   ├── database.py           # Database models & config
│   ├── models.py             # Pydantic schemas
│   └── services/             # Business logic
│       ├── simulation_service.py
│       └── team_service.py
├── frontend/                  # React frontend
│   ├── src/
│   │   ├── components/       # React components
│   │   │   ├── TeamSelector.jsx
│   │   │   ├── SimulationControls.jsx
│   │   │   ├── SimulationResults.jsx
│   │   │   ├── BracketVisualization.jsx
│   │   │   └── Statistics.jsx
│   │   ├── services/
│   │   │   └── api.js        # API client
│   │   ├── App.jsx           # Main component
│   │   └── main.jsx          # Entry point
│   └── public/
├── data/                      # Team data
│   ├── team_ratings.json     # ELO ratings for 79 teams
│   └── vct_matches_2024.json # 387 match results
├── src/                       # Core simulation engine
│   └── bracket_simulator.py  # Monte Carlo logic
├── scripts/                   # Utility scripts
│   ├── calculate_elo_ratings.py
│   ├── vct_match_scraper.py
│   └── historical_validation.py
├── tests/                     # Test suite
│   └── test_api.py
├── requirements.txt           # Python dependencies
├── railway.toml              # Railway deployment config
└── README.md
```

---

## 🚀 Quick Start (Local Development)

### **Prerequisites**
- Python 3.11+
- Node.js 18+
- npm or yarn

### **Backend Setup**

```bash
# Install dependencies
pip install -r requirements.txt

# Run backend server
uvicorn backend.main:app --reload

# Backend runs at http://localhost:8000
# API docs at http://localhost:8000/docs
```

### **Frontend Setup**

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev

# Frontend runs at http://localhost:5173
```

---

## 🎮 How to Use

1. **Select Teams**: Choose 2-16 teams from the 79 available VCT teams
2. **Configure Simulation**: 
   - Number of simulations (1K - 100K)
   - Match format (BO1, BO3, BO5)
   - Performance variance (ELO sigma)
3. **Run Simulation**: Click "Run Simulation" to start Monte Carlo analysis
4. **View Results**: 
   - Championship probabilities table
   - Interactive probability charts
   - Tournament bracket visualization with win percentages

---

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=backend tests/

# Current Status
✓ 60/60 tests passing
✓ 94% code coverage
```

---

## 🎯 API Endpoints

### **Teams**
- `GET /api/teams` - List all teams (with filters)
- `GET /api/teams/{id}` - Get specific team
- `POST /api/teams/refresh` - Update team data

### **Simulations**
- `POST /api/simulate` - Run tournament simulation
- `GET /api/simulations/{id}` - Get simulation results
- `GET /api/simulations` - List all simulations

### **Statistics**
- `GET /api/stats/summary` - Overall statistics
- `GET /api/stats/regions` - Regional breakdown

**Full API documentation:** [https://valorant-simulator-api-production.up.railway.app/docs](https://valorant-simulator-api-production.up.railway.app/docs)

---

## 📊 Data Sources

### **Match Data:**
- **Source:** VLR.gg (Valorant esports statistics)
- **Total Matches:** 387
- **Tournaments:** 15 (VCT 2024 season)
- **Coverage:**
  - VCT Champions (34 matches)
  - Masters Shanghai (38 matches)
  - Masters Madrid (17 matches)
  - Regional Leagues (278 matches)

### **Teams:**
- **Total Teams:** 79
- **Regions:** Americas, EMEA, Pacific, China
- **Rating Range:** 1400-1700 ELO

### **Collection Method:**
- Web scraping from VLR.gg match pages
- ELO calculations using standard chess formula
- K-factor: 32 (balanced for esports volatility)

---

## 🔮 Methodology

### **ELO Rating System**

Standard ELO formula adapted for Valorant:

```
Expected Win Rate = 1 / (1 + 10^((Rating_B - Rating_A) / 400))
New Rating = Old Rating + K × (Actual - Expected)
```

- **K-factor:** 32 (higher than chess due to esports variance)
- **Base Rating:** 1500
- **Map-based:** Ratings updated per map, not per match

### **Monte Carlo Simulation**

1. **Bracket Generation:** Seed teams based on ELO ratings
2. **Match Simulation:** Calculate win probabilities using ELO difference
3. **Variance Modeling:** Optional Gaussian noise (σ = 0-200)
4. **Iteration:** Repeat 10,000+ times
5. **Aggregation:** Calculate championship/finals/semis probabilities

### **Best-of-N Implementation**

For BO3 and BO5 matches:
- Calculate map-level win probability
- Use binomial distribution for series outcome
- Account for map advantage/disadvantage

---

## 🤝 Contributing

This is a portfolio project, but suggestions and feedback are welcome!

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📝 License

MIT License - feel free to use this project for learning and portfolio purposes.

---

**🔗 Live Demo:** [https://valorant-bracket-simulator.vercel.app](https://valorant-bracket-simulator.vercel.app)