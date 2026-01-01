import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';

function SimulationResults({ results, onClear }) {
  if (!results || !results.results) {
    return null;
  }

  const topTeams = results.results.slice(0, 8);

  const chartData = topTeams.map(team => ({
    name: team.name.length > 15 ? team.name.substring(0, 15) + '...' : team.name,
    probability: team.championship_prob,
    fullName: team.name,
  }));

  const getBarColor = (index) => {
    const grays = [
      '#FFFFFF',
      '#E5E5E5',
      '#D4D4D4',
      '#A3A3A3',
      '#737373',
      '#525252',
      '#404040',
      '#262626',
    ];
    return grays[index] || grays[grays.length - 1];
  };

  const exportToCSV = () => {
    const headers = ['Rank', 'Team', 'Seed', 'ELO Rating', 'Championship %', 'Finals %', 'Semifinals %'];
    const rows = results.results.map((team, index) => [
      index + 1,
      team.name,
      team.seed,
      Math.round(team.elo_rating),
      team.championship_prob.toFixed(2),
      team.finals_prob.toFixed(2),
      team.semifinals_prob.toFixed(2)
    ]);

    const csvContent = [
      headers.join(','),
      ...rows.map(row => row.join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `valorant-simulation-${Date.now()}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  };

  const copyToClipboard = () => {
    const text = results.results.map((team, index) => 
      `${index + 1}. ${team.name} - ${team.championship_prob.toFixed(2)}% win chance`
    ).join('\n');

    navigator.clipboard.writeText(text).then(() => {
      alert('Results copied to clipboard!');
    }).catch(err => {
      console.error('Failed to copy:', err);
    });
  };

  return (
    <div className="bg-neutral-900 rounded-lg p-6 border border-neutral-800">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-xl font-semibold">Simulation Results</h2>
          <p className="text-neutral-500 text-xs mt-1">
            {results.num_simulations.toLocaleString()} simulations • {results.teams_count} teams • BO{results.best_of}
          </p>
        </div>
        <div className="flex gap-2">
          <div className="relative group">
            <button className="px-3 py-1.5 bg-white hover:bg-neutral-200 text-black rounded-md transition-colors flex items-center gap-2 text-sm font-medium">
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clipRule="evenodd" />
              </svg>
              Export
            </button>
            <div className="absolute right-0 mt-2 w-48 bg-black rounded-md shadow-lg border border-neutral-700 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all z-10">
              <button
                onClick={exportToCSV}
                className="w-full text-left px-3 py-2 hover:bg-neutral-800 text-white rounded-t-md transition-colors flex items-center gap-2 text-sm"
              >
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M9 2a2 2 0 00-2 2v8a2 2 0 002 2h6a2 2 0 002-2V6.414A2 2 0 0016.414 5L14 2.586A2 2 0 0012.586 2H9z" />
                </svg>
                Download CSV
              </button>
              <button
                onClick={copyToClipboard}
                className="w-full text-left px-3 py-2 hover:bg-neutral-800 text-white rounded-b-md transition-colors flex items-center gap-2 text-sm"
              >
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M8 3a1 1 0 011-1h2a1 1 0 110 2H9a1 1 0 01-1-1z" />
                  <path d="M6 3a2 2 0 00-2 2v11a2 2 0 002 2h8a2 2 0 002-2V5a2 2 0 00-2-2 3 3 0 01-3 3H9a3 3 0 01-3-3z" />
                </svg>
                Copy to Clipboard
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="mb-8">
        <h3 className="text-sm font-medium mb-4 text-neutral-300">Championship Probability</h3>
        <div className="bg-black rounded-lg p-4 border border-neutral-800">
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#262626" />
              <XAxis 
                dataKey="name" 
                stroke="#737373"
                angle={-45}
                textAnchor="end"
                height={80}
                tick={{ fontSize: 12 }}
              />
              <YAxis stroke="#737373" tick={{ fontSize: 12 }} />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#171717', 
                  border: '1px solid #404040',
                  borderRadius: '6px'
                }}
                formatter={(value) => `${value.toFixed(2)}%`}
                labelFormatter={(label, payload) => payload[0]?.payload.fullName || label}
              />
              <Bar dataKey="probability" radius={[4, 4, 0, 0]}>
                {chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={getBarColor(index)} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div>
        <h3 className="text-sm font-medium mb-3 text-neutral-300">Team Probabilities</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="border-b border-neutral-800">
                <th className="pb-3 font-medium text-neutral-400">Rank</th>
                <th className="pb-3 font-medium text-neutral-400">Team</th>
                <th className="pb-3 text-right font-medium text-neutral-400">Seed</th>
                <th className="pb-3 text-right font-medium text-neutral-400">ELO</th>
                <th className="pb-3 text-right font-medium text-neutral-400">Win</th>
                <th className="pb-3 text-right font-medium text-neutral-400">Finals</th>
                <th className="pb-3 text-right font-medium text-neutral-400">Semis</th>
              </tr>
            </thead>
            <tbody>
              {topTeams.map((team, index) => (
                <tr key={team.name} className="border-b border-neutral-900">
                  <td className="py-3 text-neutral-500">{index + 1}</td>
                  <td className="py-3 font-medium text-white">{team.name}</td>
                  <td className="py-3 text-right text-neutral-400">#{team.seed}</td>
                  <td className="py-3 text-right text-neutral-400">{Math.round(team.elo_rating)}</td>
                  <td className="py-3 text-right">
                    <span className={`font-medium ${
                      team.championship_prob > 20 ? 'text-white' :
                      team.championship_prob > 10 ? 'text-neutral-300' :
                      'text-neutral-500'
                    }`}>
                      {team.championship_prob.toFixed(2)}%
                    </span>
                  </td>
                  <td className="py-3 text-right text-neutral-400">
                    {team.finals_prob.toFixed(2)}%
                  </td>
                  <td className="py-3 text-right text-neutral-400">
                    {team.semifinals_prob.toFixed(2)}%
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {results.results.length > 8 && (
          <p className="text-center text-neutral-500 text-xs mt-4">
            Showing top 8 of {results.results.length} teams
          </p>
        )}
      </div>

      <div className="mt-6 p-4 bg-black rounded-md border border-neutral-800">
        <h4 className="font-medium text-sm mb-2 text-neutral-300">Analysis</h4>
        <ul className="space-y-2 text-xs text-neutral-400">
          <li>
            <strong className="text-white">{topTeams[0].name}</strong> has the highest win probability at{' '}
            <strong className="text-white">{topTeams[0].championship_prob.toFixed(2)}%</strong>
          </li>
          <li>
            Top 3 teams ({topTeams.slice(0, 3).map(t => t.name).join(', ')}) account for{' '}
            <strong className="text-white">
              {topTeams.slice(0, 3).reduce((sum, t) => sum + t.championship_prob, 0).toFixed(2)}%
            </strong>{' '}
            of total probability
          </li>
          {topTeams[0].championship_prob < 25 && (
            <li className="text-neutral-300">
              No clear favorite - tournament is highly competitive
            </li>
          )}
        </ul>
      </div>
    </div>
  );
}

export default SimulationResults;