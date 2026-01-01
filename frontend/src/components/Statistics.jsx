function Statistics({ stats }) {
  if (!stats) return null;

  const regionData = Object.entries(stats.regions || {}).map(([region, count]) => ({
    region,
    count,
  }));

  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
      <div className="bg-neutral-900 rounded-lg p-6 border border-neutral-800">
        <div className="text-neutral-500 text-xs mb-1">Total Teams</div>
        <div className="text-3xl font-semibold text-white">{stats.total_teams}</div>
      </div>

      <div className="bg-neutral-900 rounded-lg p-6 border border-neutral-800">
        <div className="text-neutral-500 text-xs mb-1">Average ELO</div>
        <div className="text-3xl font-semibold text-white">{Math.round(stats.avg_elo)}</div>
      </div>

      <div className="bg-neutral-900 rounded-lg p-6 border border-neutral-800">
        <div className="text-neutral-500 text-xs mb-1">Simulations Run</div>
        <div className="text-3xl font-semibold text-white">{stats.total_simulations}</div>
      </div>

      <div className="bg-neutral-900 rounded-lg p-6 border border-neutral-800">
        <div className="text-neutral-500 text-xs mb-1">Regions</div>
        <div className="flex flex-wrap gap-1.5 mt-2">
          {regionData.map(({ region, count }) => (
            <span 
              key={region}
              className="px-2 py-0.5 bg-black border border-neutral-800 rounded text-xs text-neutral-400"
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