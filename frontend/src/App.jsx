import { useState, useEffect } from 'react';
import TeamSelector from './components/TeamSelector';
import SimulationControls from './components/SimulationControls';
import SimulationResults from './components/SimulationResults';
import Statistics from './components/Statistics';
import { teamsAPI, simulationsAPI, statsAPI } from './services/api';
import './index.css';

function App() {
  const [teams, setTeams] = useState([]);
  const [selectedTeams, setSelectedTeams] = useState([]);
  const [loading, setLoading] = useState(true);
  const [simulating, setSimulating] = useState(false);
  const [results, setResults] = useState(null);
  const [stats, setStats] = useState(null);
  const [error, setError] = useState(null);

  // Load teams on mount
  useEffect(() => {
    loadTeams();
    loadStats();
  }, []);

  const loadTeams = async () => {
    try {
      setLoading(true);
      const response = await teamsAPI.getAll();
      setTeams(response.data);
      setError(null);
    } catch (err) {
      setError('Failed to load teams. Make sure the backend is running.');
      console.error('Error loading teams:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const response = await statsAPI.getSummary();
      setStats(response.data);
    } catch (err) {
      console.error('Error loading stats:', err);
    }
  };

  const handleTeamToggle = (teamId) => {
    setSelectedTeams(prev => {
      if (prev.includes(teamId)) {
        return prev.filter(id => id !== teamId);
      } else {
        return [...prev, teamId];
      }
    });
  };

  const handleRunSimulation = async (params) => {
    if (selectedTeams.length < 2) {
      setError('Please select at least 2 teams');
      return;
    }

    try {
      setSimulating(true);
      setError(null);
      
      const response = await simulationsAPI.run({
        team_ids: selectedTeams,
        ...params,
      });

      setResults(response.data);
      loadStats(); // Refresh stats after simulation
    } catch (err) {
      setError(err.response?.data?.detail || 'Simulation failed');
      console.error('Simulation error:', err);
    } finally {
      setSimulating(false);
    }
  };

  const handleClearResults = () => {
    setResults(null);
  };

  const handleClearSelection = () => {
    setSelectedTeams([]);
  };

  return (
    <div className="min-h-screen bg-valorant-darker">
      {/* Header */}
      <header className="bg-valorant-dark border-b-2 border-valorant-red">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <h1 className="text-4xl font-bold text-white">
            🎯 Valorant Tournament Simulator
          </h1>
          <p className="text-gray-400 mt-2">
            Monte Carlo simulation engine for VCT tournament predictions
          </p>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* Error Banner */}
        {error && (
          <div className="mb-6 bg-red-900/50 border border-red-500 text-white px-4 py-3 rounded">
            <strong>Error:</strong> {error}
          </div>
        )}

        {/* Statistics Dashboard */}
        {stats && !loading && (
          <Statistics stats={stats} />
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-6">
          {/* Left Column: Team Selection */}
          <div className="lg:col-span-1">
            <TeamSelector
              teams={teams}
              selectedTeams={selectedTeams}
              onTeamToggle={handleTeamToggle}
              onClearSelection={handleClearSelection}
              loading={loading}
            />
          </div>

          {/* Right Column: Controls & Results */}
          <div className="lg:col-span-2 space-y-6">
            {/* Simulation Controls */}
            <SimulationControls
              selectedCount={selectedTeams.length}
              onRunSimulation={handleRunSimulation}
              simulating={simulating}
              disabled={selectedTeams.length < 2}
            />

            {/* Results */}
            {results && (
              <SimulationResults
                results={results}
                onClear={handleClearResults}
              />
            )}

            {/* Placeholder when no results */}
            {!results && !simulating && (
              <div className="bg-valorant-gray rounded-lg p-12 text-center">
                <div className="text-gray-400 text-lg">
                  <p className="mb-2">👈 Select teams from the left</p>
                  <p>Configure parameters above</p>
                  <p className="mt-4 text-sm">
                    Then click "Run Simulation" to predict tournament outcomes
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-valorant-dark border-t border-valorant-gray mt-12 py-6">
        <div className="max-w-7xl mx-auto px-4 text-center text-gray-400">
          <p>Built with React + FastAPI | ELO-based Monte Carlo Simulation</p>
          <p className="text-sm mt-2">
            Backend: <a href="http://localhost:8000/docs" target="_blank" rel="noopener noreferrer" className="text-valorant-red hover:underline">
              API Docs
            </a>
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
