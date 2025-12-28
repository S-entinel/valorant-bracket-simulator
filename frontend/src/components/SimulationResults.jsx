import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';

function SimulationResults({ results, onClear }) {
  if (!results || !results.results) {
    return null;
  }

  const topTeams = results.results.slice(0, 8); // Show top 8

  // Prepare chart data
  const chartData = topTeams.map(team => ({
    name: team.name.length > 15 ? team.name.substring(0, 15) + '...' : team.name,
    probability: team.championship_prob,
    fullName: team.name,
  }));

  // Color gradient for bars
  const getBarColor = (index) => {
    const colors = [
      '#FF4655', // Valorant red
      '#FF6B77',
      '#FF8E99',
      '#FFB1BB',
      '#4A5568',
      '#5A6578',
      '#6A7588',
      '#7A8598',
    ];
    return colors[index] || colors[colors.length - 1];
  };

  return (
    <div className="bg-valorant-gray rounded-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold">Simulation Results</h2>
          <p className="text-gray-400 text-sm mt-1">
            {results.num_simulations.toLocaleString()} simulations • {results.teams_count} teams • BO{results.best_of}
          </p>
        </div>
        <button
          onClick={onClear}
          className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors"
        >
          Clear Results
        </button>
      </div>

      {/* Championship Probability Chart */}
      <div className="mb-8">
        <h3 className="text-lg font-bold mb-4">Championship Probability</h3>
        <div className="bg-valorant-dark rounded-lg p-4">
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis 
                dataKey="name" 
                stroke="#9CA3AF"
                angle={-45}
                textAnchor="end"
                height={80}
              />
              <YAxis stroke="#9CA3AF" />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#1C2733', 
                  border: '1px solid #374151',
                  borderRadius: '8px'
                }}
                formatter={(value) => `${value.toFixed(2)}%`}
                labelFormatter={(label, payload) => {
                  if (payload && payload[0]) {
                    return payload[0].payload.fullName;
                  }
                  return label;
                }}
              />
              <Bar dataKey="probability" radius={[8, 8, 0, 0]}>
                {chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={getBarColor(index)} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Detailed Results Table */}
      <div>
        <h3 className="text-lg font-bold mb-4">Detailed Probabilities</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead>
              <tr className="border-b border-gray-700">
                <th className="pb-3 text-gray-400 font-medium">Rank</th>
                <th className="pb-3 text-gray-400 font-medium">Team</th>
                <th className="pb-3 text-gray-400 font-medium">Seed</th>
                <th className="pb-3 text-gray-400 font-medium">ELO</th>
                <th className="pb-3 text-gray-400 font-medium text-right">Win %</th>
                <th className="pb-3 text-gray-400 font-medium text-right">Finals %</th>
                <th className="pb-3 text-gray-400 font-medium text-right">Semis %</th>
              </tr>
            </thead>
            <tbody>
              {topTeams.map((team, index) => (
                <tr 
                  key={team.name}
                  className="border-b border-gray-800 hover:bg-valorant-dark/50 transition-colors"
                >
                  <td className="py-4">
                    <span className={`inline-flex items-center justify-center w-8 h-8 rounded-full font-bold ${
                      index === 0 ? 'bg-valorant-red text-white' :
                      index === 1 ? 'bg-gray-600 text-white' :
                      index === 2 ? 'bg-amber-700 text-white' :
                      'bg-gray-700 text-gray-300'
                    }`}>
                      {index + 1}
                    </span>
                  </td>
                  <td className="py-4 font-medium">{team.name}</td>
                  <td className="py-4 text-gray-400">#{team.seed}</td>
                  <td className="py-4 text-gray-400">{Math.round(team.elo_rating)}</td>
                  <td className="py-4 text-right">
                    <span className={`font-bold ${
                      team.championship_prob > 20 ? 'text-valorant-red' :
                      team.championship_prob > 10 ? 'text-orange-400' :
                      'text-gray-300'
                    }`}>
                      {team.championship_prob.toFixed(2)}%
                    </span>
                  </td>
                  <td className="py-4 text-right text-gray-300">
                    {team.finals_prob.toFixed(2)}%
                  </td>
                  <td className="py-4 text-right text-gray-300">
                    {team.semifinals_prob.toFixed(2)}%
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {results.results.length > 8 && (
          <p className="text-center text-gray-400 text-sm mt-4">
            Showing top 8 of {results.results.length} teams
          </p>
        )}
      </div>

      {/* Insights */}
      <div className="mt-6 p-4 bg-valorant-dark rounded-lg">
        <h4 className="font-bold mb-2">📊 Analysis</h4>
        <ul className="space-y-2 text-sm text-gray-300">
          <li>
            <strong className="text-white">{topTeams[0].name}</strong> has the highest win probability at{' '}
            <strong className="text-valorant-red">{topTeams[0].championship_prob.toFixed(2)}%</strong>
          </li>
          <li>
            Top 3 teams ({topTeams.slice(0, 3).map(t => t.name).join(', ')}) account for{' '}
            <strong className="text-white">
              {topTeams.slice(0, 3).reduce((sum, t) => sum + t.championship_prob, 0).toFixed(2)}%
            </strong>{' '}
            of total probability
          </li>
          {topTeams[0].championship_prob < 25 && (
            <li className="text-yellow-400">
              ⚠️ No clear favorite - tournament is highly competitive!
            </li>
          )}
        </ul>
      </div>
    </div>
  );
}

export default SimulationResults;
