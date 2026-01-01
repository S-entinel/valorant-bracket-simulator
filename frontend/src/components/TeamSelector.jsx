import { useState } from 'react';

const REGIONS = ['All', 'Americas', 'EMEA', 'Pacific', 'China'];

function TeamSelector({ teams, selectedTeams, onTeamToggle, onClearSelection, loading }) {
  const [regionFilter, setRegionFilter] = useState('All');
  const [searchQuery, setSearchQuery] = useState('');

  const filteredTeams = teams.filter(team => {
    const matchesRegion = regionFilter === 'All' || team.region === regionFilter;
    const matchesSearch = team.name.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesRegion && matchesSearch;
  });

  const sortedTeams = [...filteredTeams].sort((a, b) => b.elo_rating - a.elo_rating);

  if (loading) {
    return (
      <div className="bg-neutral-900 rounded-lg p-6 border border-neutral-800">
        <h2 className="text-xl font-semibold mb-4">Select Teams</h2>
        <div className="text-center py-12 text-neutral-500 text-sm">
          Loading teams...
        </div>
      </div>
    );
  }

  return (
    <div className="bg-neutral-900 rounded-lg p-6 border border-neutral-800">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold">Select Teams</h2>
        <span className="bg-white text-black px-2.5 py-0.5 rounded-full text-xs font-medium">
          {selectedTeams.length} selected
        </span>
      </div>

      <input
        type="text"
        placeholder="Search teams..."
        value={searchQuery}
        onChange={(e) => setSearchQuery(e.target.value)}
        className="w-full px-3 py-2 bg-black text-white text-sm rounded-md border border-neutral-700 focus:border-white focus:outline-none mb-3"
      />

      <div className="flex flex-wrap gap-1.5 mb-3">
        {REGIONS.map(region => (
          <button
            key={region}
            onClick={() => setRegionFilter(region)}
            className={`px-2.5 py-1 rounded-md text-xs font-medium transition-colors ${
              regionFilter === region
                ? 'bg-white text-black'
                : 'bg-neutral-800 text-neutral-400 hover:bg-neutral-700 hover:text-neutral-200'
            }`}
          >
            {region}
          </button>
        ))}
      </div>

      {selectedTeams.length > 0 && (
        <button
          onClick={onClearSelection}
          className="w-full mb-3 px-3 py-2 bg-neutral-800 hover:bg-neutral-700 text-white text-sm rounded-md transition-colors"
        >
          Clear Selection ({selectedTeams.length})
        </button>
      )}

      <div className="space-y-2 max-h-[600px] overflow-y-auto">
        {sortedTeams.length === 0 ? (
          <div className="text-center py-8 text-neutral-500 text-sm">
            No teams found
          </div>
        ) : (
          sortedTeams.map(team => {
            const isSelected = selectedTeams.includes(team.id);
            return (
              <div
                key={team.id}
                onClick={() => onTeamToggle(team.id)}
                className={`p-3 rounded-md cursor-pointer transition-all border ${
                  isSelected
                    ? 'bg-neutral-800 border-white'
                    : 'bg-black border-neutral-800 hover:border-neutral-600'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <span className="text-white font-medium text-sm">{team.name}</span>
                      <span className="text-xs px-1.5 py-0.5 bg-neutral-800 rounded text-neutral-400">
                        {team.region}
                      </span>
                    </div>
                    <div className="flex items-center gap-3 mt-1 text-xs text-neutral-500">
                      <span>ELO: <strong className="text-neutral-300">{Math.round(team.elo_rating)}</strong></span>
                      <span>Rank: #{team.rank}</span>
                    </div>
                  </div>
                  <div className="ml-3">
                    {isSelected && (
                      <div className="w-5 h-5 bg-white rounded-full flex items-center justify-center">
                        <svg className="w-3 h-3 text-black" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                        </svg>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}

export default TeamSelector;