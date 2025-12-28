import { useState } from 'react';

const REGIONS = ['All', 'Americas', 'EMEA', 'Pacific', 'China'];

function TeamSelector({ teams, selectedTeams, onTeamToggle, onClearSelection, loading }) {
  const [regionFilter, setRegionFilter] = useState('All');
  const [searchQuery, setSearchQuery] = useState('');

  // Filter teams
  const filteredTeams = teams.filter(team => {
    const matchesRegion = regionFilter === 'All' || team.region === regionFilter;
    const matchesSearch = team.name.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesRegion && matchesSearch;
  });

  // Sort teams by ELO (highest first)
  const sortedTeams = [...filteredTeams].sort((a, b) => b.elo_rating - a.elo_rating);

  if (loading) {
    return (
      <div className="bg-valorant-gray rounded-lg p-6">
        <h2 className="text-2xl font-bold mb-4">Select Teams</h2>
        <div className="text-center py-12 text-gray-400">
          Loading teams...
        </div>
      </div>
    );
  }

  return (
    <div className="bg-valorant-gray rounded-lg p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-bold">Select Teams</h2>
        <span className="bg-valorant-red text-white px-3 py-1 rounded-full text-sm font-bold">
          {selectedTeams.length} selected
        </span>
      </div>

      {/* Search */}
      <input
        type="text"
        placeholder="Search teams..."
        value={searchQuery}
        onChange={(e) => setSearchQuery(e.target.value)}
        className="w-full px-4 py-2 bg-valorant-dark text-white rounded-lg border border-gray-600 focus:border-valorant-red focus:outline-none mb-4"
      />

      {/* Region Filter */}
      <div className="flex flex-wrap gap-2 mb-4">
        {REGIONS.map(region => (
          <button
            key={region}
            onClick={() => setRegionFilter(region)}
            className={`px-3 py-1 rounded-lg text-sm font-medium transition-colors ${
              regionFilter === region
                ? 'bg-valorant-red text-white'
                : 'bg-valorant-dark text-gray-300 hover:bg-gray-700'
            }`}
          >
            {region}
          </button>
        ))}
      </div>

      {/* Clear Selection Button */}
      {selectedTeams.length > 0 && (
        <button
          onClick={onClearSelection}
          className="w-full mb-4 px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors"
        >
          Clear Selection ({selectedTeams.length})
        </button>
      )}

      {/* Team List */}
      <div className="space-y-2 max-h-[600px] overflow-y-auto">
        {sortedTeams.length === 0 ? (
          <div className="text-center py-8 text-gray-400">
            No teams found
          </div>
        ) : (
          sortedTeams.map(team => {
            const isSelected = selectedTeams.includes(team.id);
            return (
              <div
                key={team.id}
                onClick={() => onTeamToggle(team.id)}
                className={`p-4 rounded-lg cursor-pointer transition-all border-2 ${
                  isSelected
                    ? 'bg-valorant-red/20 border-valorant-red'
                    : 'bg-valorant-dark border-transparent hover:border-gray-600'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <span className="text-white font-bold">{team.name}</span>
                      <span className="text-xs px-2 py-0.5 bg-gray-700 rounded text-gray-300">
                        {team.region}
                      </span>
                    </div>
                    <div className="flex items-center gap-4 mt-1 text-sm text-gray-400">
                      <span>ELO: <strong className="text-white">{Math.round(team.elo_rating)}</strong></span>
                      <span>Rank: #{team.rank}</span>
                    </div>
                  </div>
                  <div className="ml-4">
                    {isSelected && (
                      <div className="w-6 h-6 bg-valorant-red rounded-full flex items-center justify-center">
                        <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
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
