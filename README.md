# Valorant Tournament Prediction System

A Monte Carlo simulation engine that predicts tournament outcomes for Valorant esports competitions using ELO ratings and statistical modeling.

## What It Does

This system scrapes live team rankings from VLR.gg, calculates match probabilities using ELO ratings, and runs thousands of tournament simulations to predict which teams are most likely to win. It accounts for performance variance and different match formats (BO1, BO3, BO5).

## Technical Approach

- **ELO Probability Model**: Converts team ratings into map-level win probabilities using the standard ELO formula
- **Binomial Distribution**: Calculates series outcomes for best-of-N matches
- **Monte Carlo Simulation**: Runs 10,000+ tournament brackets to generate statistical predictions
- **Performance Variance**: Optional Gaussian noise models teams having "hot" or "cold" performances

## Setup

```bash
pip install -r requirements.txt
```

## Usage

1. Scrape current team rankings:
```bash
python vlr_http_scraper.py
```

2. Run tournament simulation:
```bash
python run_simulator_live.py
```

3. (Optional) Visualize results:
```bash
python visualise_results.py
```

## Example Output

```
SIMULATION RESULTS (sorted by championship probability):
Team                 Seed ELO    Win%   Finals%    Semis%   Quarters%
------------------------------------------------------------------------
NRG                  2    1700.0  13.80%   32.72%   27.97%     49.60%
FNATIC               1    1700.0  13.78%   32.76%   28.87%     50.40%
G2 Esports           3    1685.0  12.84%   30.85%   28.75%     60.77%
```

## Key Features

- Live data scraping from VLR.gg world rankings
- Configurable tournament parameters (bracket size, match format, performance variance)
- Statistical validation through large-scale Monte Carlo simulation
- Clean separation between data collection and prediction logic

## Project Structure

- `vlr_http_scraper.py` - Web scraper for VLR.gg team rankings
- `bracket_simulator.py` - Core simulation engine with ELO calculations
- `run_simulator_live.py` - Main script for running predictions
- `visualise_results.py` - Generates probability charts
