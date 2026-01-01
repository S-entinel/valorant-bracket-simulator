import { useState, useEffect } from 'react';
import TeamSelector from './components/TeamSelector';
import SimulationControls from './components/SimulationControls';
import SimulationResults from './components/SimulationResults';
import BracketVisualization from './components/BracketVisualization';
import Statistics from './components/Statistics';
import { ToastContainer, useToast } from './components/Toast';
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
  const [viewMode, setViewMode] = useState('results');
  const { toasts, addToast, removeToast } = useToast();

  useEffect(() => {
    loadTeams();
    loadStats();
  }, []);

  const loadTeams = async (retryCount = 0) => {
    try {
      setLoading(true);
      setError(null);
      
      // Ensure minimum loading time to show spinner (800ms)
      const [response] = await Promise.all([
        teamsAPI.getAll(),
        new Promise(resolve => setTimeout(resolve, 800))
      ]);
      
      setTeams(response.data);
      if (response.data.length > 0) {
        addToast(`Loaded ${response.data.length} teams successfully`, 'success');
      }
    } catch (err) {
      console.error('Error loading teams:', err);
      
      // Retry logic
      if (retryCount < 2) {
        console.log(`Retrying... (${retryCount + 1}/2)`);
        addToast('Connection failed, retrying...', 'warning', 2000);
        setLoading(false);
        await new Promise(resolve => setTimeout(resolve, 2000));
        return loadTeams(retryCount + 1);
      }
      
      setError('Failed to load teams. Make sure the backend is running at http://localhost:8000');
      addToast('Failed to connect to backend', 'error', 5000);
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
        if (prev.length >= 32) {
          addToast('Maximum 32 teams allowed', 'warning');
          return prev;
        }
        return [...prev, teamId];
      }
    });
  };

  const handleRunSimulation = async (params) => {
    if (selectedTeams.length < 2) {
      setError('Please select at least 2 teams');
      addToast('Select at least 2 teams to run simulation', 'warning');
      return;
    }

    if (selectedTeams.length > 32) {
      setError('Maximum 32 teams allowed');
      addToast('Maximum 32 teams allowed', 'warning');
      return;
    }

    try {
      setSimulating(true);
      setError(null);
      
      addToast(`Running ${params.num_simulations.toLocaleString()} simulations...`, 'info', 2000);
      
      const response = await simulationsAPI.run({
        team_ids: selectedTeams,
        ...params,
      });

      setResults(response.data);
      setViewMode('results');
      loadStats();
      
      addToast('Simulation complete!', 'success');
    } catch (err) {
      const errorMessage = err.response?.data?.detail || 'Simulation failed';
      setError(errorMessage);
      addToast(errorMessage, 'error', 5000);
      console.error('Simulation error:', err);
    } finally {
      setSimulating(false);
    }
  };

  const handleClearResults = () => {
    setResults(null);
    setViewMode('results');
    addToast('Results cleared', 'info');
  };

  const handleClearSelection = () => {
    setSelectedTeams([]);
    addToast('Selection cleared', 'info');
  };

  const handleRetryConnection = () => {
    setError(null);
    loadTeams();
    loadStats();
  };

  return (
    <div className="min-h-screen bg-valorant-darker">
      <ToastContainer toasts={toasts} removeToast={removeToast} />

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

      <main className="max-w-7xl mx-auto px-4 py-8">
        {error && (
          <div className="mb-6 bg-red-900/50 border border-red-500 text-white px-4 py-3 rounded flex items-center justify-between">
            <div>
              <strong>Error:</strong> {error}
            </div>
            <button
              onClick={handleRetryConnection}
              className="px-4 py-2 bg-red-700 hover:bg-red-600 rounded transition-colors text-sm font-medium"
            >
              Retry Connection
            </button>
          </div>
        )}

        {stats && !loading && (
          <Statistics stats={stats} />
        )}

        {/* LOADING STATE - Now more visible */}
        {loading ? (
          <div className="mt-6">
            <div className="bg-valorant-gray rounded-lg p-16 text-center">
              <div className="flex flex-col items-center gap-4">
                <div className="w-16 h-16 border-4 border-gray-700 border-t-valorant-red rounded-full animate-spin"></div>
                <p className="text-gray-400 text-lg animate-pulse">Loading teams...</p>
                <p className="text-gray-500 text-sm">Connecting to backend...</p>
              </div>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-6">
            <div className="lg:col-span-1">
              <TeamSelector
                teams={teams}
                selectedTeams={selectedTeams}
                onTeamToggle={handleTeamToggle}
                onClearSelection={handleClearSelection}
                loading={loading}
              />
            </div>

            <div className="lg:col-span-2 space-y-6">
              <SimulationControls
                selectedCount={selectedTeams.length}
                onRunSimulation={handleRunSimulation}
                simulating={simulating}
                disabled={selectedTeams.length < 2}
              />

              {results && (
                <div className="flex items-center justify-between bg-valorant-gray rounded-lg p-4">
                  <div className="flex gap-2">
                    <button
                      onClick={() => setViewMode('results')}
                      className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                        viewMode === 'results'
                          ? 'bg-valorant-red text-white'
                          : 'bg-valorant-dark text-gray-300 hover:bg-gray-700'
                      }`}
                    >
                      📊 Results & Charts
                    </button>
                    <button
                      onClick={() => setViewMode('bracket')}
                      className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                        viewMode === 'bracket'
                          ? 'bg-valorant-red text-white'
                          : 'bg-valorant-dark text-gray-300 hover:bg-gray-700'
                      }`}
                    >
                      🏆 Tournament Bracket
                    </button>
                  </div>
                  <button
                    onClick={handleClearResults}
                    className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors"
                  >
                    Clear Results
                  </button>
                </div>
              )}

              {results && viewMode === 'results' && (
                <SimulationResults
                  results={results}
                  onClear={handleClearResults}
                />
              )}

              {results && viewMode === 'bracket' && (
                <BracketVisualization
                  results={results.results}
                  teamsCount={results.teams_count}
                  bestOf={results.best_of}
                />
              )}

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
        )}
      </main>

      <footer className="bg-valorant-dark border-t border-valorant-gray mt-12 py-6">
        <div className="max-w-7xl mx-auto px-4 text-center text-gray-400">
          <p>Built with React + FastAPI | ELO-based Monte Carlo Simulation</p>
          <p className="text-sm mt-2">
            Backend: <a href="http://localhost:8000/docs" target="_blank" rel="noopener noreferrer" className="text-valorant-red hover:underline">
              API Docs
            </a> | Frontend: <span className="text-valorant-red">v1.0.0</span>
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;