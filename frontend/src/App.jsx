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
      
      if (retryCount < 2) {
        console.log(`Retrying... (${retryCount + 1}/2)`);
        addToast('Connection failed, retrying...', 'warning', 2000);
        setLoading(false);
        await new Promise(resolve => setTimeout(resolve, 2000));
        return loadTeams(retryCount + 1);
      }
      
      setError('Failed to load teams. Please check that the backend is running.');
      addToast('Could not connect to backend', 'error', 5000);
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
      }
      if (prev.length >= 16) {
        addToast('Maximum 16 teams allowed', 'warning');
        return prev;
      }
      return [...prev, teamId];
    });
  };

  const handleRunSimulation = async (params) => {
    try {
      setSimulating(true);
      setError(null);
      
      const response = await simulationsAPI.run({
        team_ids: selectedTeams,
        num_simulations: params.numSimulations,
        best_of: params.bestOf,
        elo_sigma: params.eloSigma || null,
      });
      
      setResults(response.data);
      setViewMode('results');
      addToast('Simulation completed', 'success');
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
    <div className="min-h-screen bg-black">
      <ToastContainer toasts={toasts} removeToast={removeToast} />

      <header className="bg-neutral-900 border-b border-neutral-800">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <h1 className="text-3xl font-semibold text-white tracking-tight">
            Valorant Tournament Simulator
          </h1>
          <p className="text-neutral-400 mt-1 text-sm">
            Monte Carlo simulation engine for tournament predictions
          </p>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        {error && (
          <div className="mb-6 bg-red-950/50 border border-red-800 text-red-200 px-4 py-3 rounded-lg flex items-center justify-between">
            <div className="text-sm">
              <strong className="font-medium">Error:</strong> {error}
            </div>
            <button
              onClick={handleRetryConnection}
              className="px-3 py-1.5 bg-red-900 hover:bg-red-800 rounded text-sm font-medium transition-colors"
            >
              Retry
            </button>
          </div>
        )}

        {stats && !loading && (
          <Statistics stats={stats} />
        )}

        {loading ? (
          <div className="mt-6">
            <div className="bg-neutral-900 rounded-lg p-16 text-center border border-neutral-800">
              <div className="flex flex-col items-center gap-4">
                <div className="w-12 h-12 border-2 border-neutral-700 border-t-white rounded-full animate-spin"></div>
                <p className="text-neutral-400 text-sm">Loading teams...</p>
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
                <div className="flex items-center justify-between bg-neutral-900 rounded-lg p-3 border border-neutral-800">
                  <div className="flex gap-2">
                    <button
                      onClick={() => setViewMode('results')}
                      className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                        viewMode === 'results'
                          ? 'bg-white text-black'
                          : 'bg-neutral-800 text-neutral-300 hover:bg-neutral-700'
                      }`}
                    >
                      Results & Charts
                    </button>
                    <button
                      onClick={() => setViewMode('bracket')}
                      className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                        viewMode === 'bracket'
                          ? 'bg-white text-black'
                          : 'bg-neutral-800 text-neutral-300 hover:bg-neutral-700'
                      }`}
                    >
                      Tournament Bracket
                    </button>
                  </div>
                  <button
                    onClick={handleClearResults}
                    className="px-3 py-2 bg-neutral-800 hover:bg-neutral-700 text-white rounded-md transition-colors text-sm"
                  >
                    Clear
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
                <div className="bg-neutral-900 rounded-lg p-12 text-center border border-neutral-800">
                  <div className="text-neutral-400 text-sm space-y-2">
                    <p>Select teams from the left panel</p>
                    <p>Configure parameters above</p>
                    <p className="mt-4 text-xs text-neutral-500">
                      Click "Run Simulation" to predict tournament outcomes
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </main>

      <footer className="bg-neutral-900 border-t border-neutral-800 mt-12 py-6">
        <div className="max-w-7xl mx-auto px-4 text-center text-neutral-500 text-xs">
          <p>ELO-based Monte Carlo Simulation</p>
        </div>
      </footer>
    </div>
  );
}

export default App;