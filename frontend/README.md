# Valorant Tournament Simulator - Frontend

React frontend for the Valorant tournament prediction system.

## Features

- 🎯 **Team Selection** - Browse and select teams with region filtering
- ⚙️ **Simulation Controls** - Configure tournament parameters
- 📊 **Results Visualization** - Interactive charts and probability tables
- 📈 **Statistics Dashboard** - Real-time stats from backend API

## Quick Start

### 1. Install Dependencies

```bash
npm install
```

### 2. Start Development Server

```bash
npm run dev
```

The app will be available at `http://localhost:5173`

### 3. Make Sure Backend is Running

The frontend connects to the backend API at `http://localhost:8000`.

Start the backend first:
```bash
# From project root
python run_backend.py
```

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── TeamSelector.jsx       # Team selection UI
│   │   ├── SimulationControls.jsx # Parameter controls
│   │   ├── SimulationResults.jsx  # Results display
│   │   └── Statistics.jsx         # Stats dashboard
│   ├── services/
│   │   └── api.js                 # API client
│   ├── App.jsx                    # Main app component
│   ├── main.jsx                   # Entry point
│   └── index.css                  # Global styles
├── .env                           # Environment variables
├── tailwind.config.js             # Tailwind configuration
└── vite.config.js                 # Vite configuration
```

## Environment Variables

Create a `.env` file:

```env
VITE_API_URL=http://localhost:8000
```

## Available Scripts

```bash
npm run dev      # Start development server
npm run build    # Build for production
npm run preview  # Preview production build
```

## Technologies Used

- **React 18** - UI framework
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Styling
- **Axios** - HTTP client
- **Recharts** - Data visualization

## How It Works

1. **Team Selection**: Browse 24 VCT teams, filter by region
2. **Configure Parameters**: Choose simulation count, match format (BO1/3/5), variance
3. **Run Simulation**: Click button to trigger Monte Carlo simulation
4. **View Results**: See championship probabilities, advancement stats, interactive charts

## API Integration

The frontend communicates with the FastAPI backend:

- `GET /api/teams` - Load teams
- `POST /api/simulate` - Run simulation
- `GET /api/stats/summary` - Get statistics

## Customization

### Colors

Edit `tailwind.config.js` to change the Valorant theme:

```js
colors: {
  valorant: {
    red: '#FF4655',
    dark: '#0F1923',
    // ...
  }
}
```

### API URL

Change backend URL in `.env`:

```env
VITE_API_URL=http://your-backend-url:8000
```

## Build for Production

```bash
npm run build
```

Output in `dist/` folder. Deploy with any static hosting service (Vercel, Netlify, etc.)

## Troubleshooting

**Teams not loading?**
- Make sure backend is running at `http://localhost:8000`
- Check browser console for CORS errors
- Verify `.env` file has correct API URL

**CORS errors?**
- Backend should allow `http://localhost:5173` in CORS origins
- Check `backend/main.py` CORS middleware configuration

**Simulation not working?**
- Select at least 2 teams
- Backend must be running
- Check network tab for failed requests

## Next Steps

- [ ] Add bracket visualization component
- [ ] Implement historical validation UI
- [ ] Add team comparison feature
- [ ] Export results to PDF/CSV
- [ ] Add authentication
