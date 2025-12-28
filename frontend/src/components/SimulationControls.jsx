import { useState } from 'react';

function SimulationControls({ selectedCount, onRunSimulation, simulating, disabled }) {
  const [numSimulations, setNumSimulations] = useState(10000);
  const [bestOf, setBestOf] = useState(3);
  const [eloSigma, setEloSigma] = useState(0);

  const handleSubmit = (e) => {
    e.preventDefault();
    onRunSimulation({
      num_simulations: numSimulations,
      best_of: bestOf,
      elo_sigma: eloSigma > 0 ? eloSigma : null,
    });
  };

  return (
    <div className="bg-valorant-gray rounded-lg p-6">
      <h2 className="text-2xl font-bold mb-4">Simulation Parameters</h2>

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Number of Simulations */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Number of Simulations
          </label>
          <select
            value={numSimulations}
            onChange={(e) => setNumSimulations(Number(e.target.value))}
            className="w-full px-4 py-2 bg-valorant-dark text-white rounded-lg border border-gray-600 focus:border-valorant-red focus:outline-none"
          >
            <option value={1000}>1,000 (Fast)</option>
            <option value={5000}>5,000</option>
            <option value={10000}>10,000 (Recommended)</option>
            <option value={25000}>25,000</option>
            <option value={50000}>50,000 (Slow)</option>
          </select>
          <p className="mt-1 text-xs text-gray-400">
            More simulations = more accurate predictions
          </p>
        </div>

        {/* Match Format */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Match Format
          </label>
          <div className="grid grid-cols-3 gap-2">
            {[1, 3, 5].map(value => (
              <button
                key={value}
                type="button"
                onClick={() => setBestOf(value)}
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                  bestOf === value
                    ? 'bg-valorant-red text-white'
                    : 'bg-valorant-dark text-gray-300 hover:bg-gray-700'
                }`}
              >
                BO{value}
              </button>
            ))}
          </div>
          <p className="mt-1 text-xs text-gray-400">
            Best-of format affects prediction accuracy
          </p>
        </div>

        {/* Performance Variance */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Performance Variance (ELO Sigma): {eloSigma}
          </label>
          <input
            type="range"
            min="0"
            max="100"
            step="10"
            value={eloSigma}
            onChange={(e) => setEloSigma(Number(e.target.value))}
            className="w-full"
          />
          <div className="flex justify-between text-xs text-gray-400 mt-1">
            <span>0 (Deterministic)</span>
            <span>50 (Realistic)</span>
            <span>100 (High Variance)</span>
          </div>
          <p className="mt-1 text-xs text-gray-400">
            Models "hot" and "cold" team performances
          </p>
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={disabled || simulating}
          className={`w-full py-3 rounded-lg font-bold text-white transition-all ${
            disabled || simulating
              ? 'bg-gray-600 cursor-not-allowed'
              : 'bg-valorant-red hover:bg-red-600 hover:shadow-lg'
          }`}
        >
          {simulating ? (
            <span className="flex items-center justify-center gap-2">
              <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
              Running {numSimulations.toLocaleString()} simulations...
            </span>
          ) : (
            `Run Simulation (${selectedCount} teams)`
          )}
        </button>

        {disabled && !simulating && (
          <p className="text-center text-sm text-red-400">
            Select at least 2 teams to run simulation
          </p>
        )}
      </form>
    </div>
  );
}

export default SimulationControls;
