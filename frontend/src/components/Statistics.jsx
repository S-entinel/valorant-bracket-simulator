function Statistics({ stats }) {
  if (!stats) return null;

  const regionData = Object.entries(stats.regions || {}).map(([region, count]) => ({
    region,
    count,
  }));

  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
      {/* Total Teams */}
      <div className="bg-valorant-gray rounded-lg p-6">
        <div className="text-gray-400 text-sm mb-1">Total Teams</div>
        <div className="text-3xl font-bold text-white">{stats.total_teams}</div>
      </div>

      {/* Average ELO */}
      <div className="bg-valorant-gray rounded-lg p-6">
        <div className="text-gray-400 text-sm mb-1">Average ELO</div>
        <div className="text-3xl font-bold text-white">{Math.round(stats.avg_elo)}</div>
      </div>

      {/* Simulations Run */}
      <div className="bg-valorant-gray rounded-lg p-6">
        <div className="text-gray-400 text-sm mb-1">Simulations Run</div>
        <div className="text-3xl font-bold text-valorant-red">{stats.total_simulations}</div>
      </div>

      {/* Regions */}
      <div className="bg-valorant-gray rounded-lg p-6">
        <div className="text-gray-400 text-sm mb-1">Regions</div>
        <div className="flex flex-wrap gap-2 mt-2">
          {regionData.map(({ region, count }) => (
            <span 
              key={region}
              className="px-2 py-1 bg-valorant-dark rounded text-xs text-gray-300"
            >
              {region}: {count}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}

export default Statistics;
