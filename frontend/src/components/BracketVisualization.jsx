import { useState } from 'react';

function BracketVisualization({ results, teamsCount, bestOf }) {
  const [showProbabilities, setShowProbabilities] = useState(true);

  if (!results || results.length === 0) {
    return (
      <div className="bg-valorant-gray rounded-lg p-12 text-center">
        <p className="text-gray-400">No bracket data available</p>
      </div>
    );
  }

  // Calculate number of rounds based on team count
  const numRounds = Math.ceil(Math.log2(teamsCount));
  
  // Seed teams by their championship probability (highest = #1 seed)
  const seededTeams = [...results].sort((a, b) => b.elo_rating - a.elo_rating);

  // Generate bracket structure
  const generateBracket = () => {
    const bracket = {};
    
    // Round 1: Initial matchups based on seeding
    bracket[1] = [];
    const pairCount = Math.ceil(teamsCount / 2);
    
    for (let i = 0; i < pairCount; i++) {
      const team1 = seededTeams[i * 2];
      const team2 = seededTeams[i * 2 + 1];
      
      if (team1 && team2) {
        // Calculate head-to-head probability
        const team1Prob = team1.championship_prob / (team1.championship_prob + team2.championship_prob) * 100;
        const team2Prob = 100 - team1Prob;
        
        bracket[1].push({
          team1,
          team2,
          team1Prob: team1Prob.toFixed(1),
          team2Prob: team2Prob.toFixed(1)
        });
      } else if (team1) {
        // Bye
        bracket[1].push({
          team1,
          team2: null,
          team1Prob: 100,
          team2Prob: 0
        });
      }
    }

    // Future rounds - show probable matchups
    for (let round = 2; round <= numRounds; round++) {
      bracket[round] = [];
      const prevRoundMatchups = bracket[round - 1];
      
      for (let i = 0; i < prevRoundMatchups.length; i += 2) {
        const match1 = prevRoundMatchups[i];
        const match2 = prevRoundMatchups[i + 1];
        
        if (match1 && match2) {
          // Most likely winners advance
          const winner1 = parseFloat(match1.team1Prob) > parseFloat(match1.team2Prob) 
            ? match1.team1 
            : match1.team2;
          const winner2 = parseFloat(match2.team1Prob) > parseFloat(match2.team2Prob) 
            ? match2.team1 
            : match2.team2;
          
          if (winner1 && winner2) {
            const w1Prob = winner1.championship_prob / (winner1.championship_prob + winner2.championship_prob) * 100;
            const w2Prob = 100 - w1Prob;
            
            bracket[round].push({
              team1: winner1,
              team2: winner2,
              team1Prob: w1Prob.toFixed(1),
              team2Prob: w2Prob.toFixed(1)
            });
          }
        } else if (match1) {
          // Bye advances
          const winner = parseFloat(match1.team1Prob) > parseFloat(match1.team2Prob) 
            ? match1.team1 
            : match1.team2;
          bracket[round].push({
            team1: winner,
            team2: null,
            team1Prob: 100,
            team2Prob: 0
          });
        }
      }
    }

    return bracket;
  };

  const bracket = generateBracket();

  // Get round names
  const getRoundName = (round) => {
    const remaining = Math.pow(2, numRounds - round + 1);
    if (round === numRounds) return 'Finals';
    if (round === numRounds - 1) return 'Semifinals';
    if (round === numRounds - 2) return 'Quarterfinals';
    return `Round ${round}`;
  };

  return (
    <div className="bg-valorant-gray rounded-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold">Tournament Bracket</h2>
          <p className="text-gray-400 text-sm mt-1">
            Probable matchups based on {results[0].num_simulations?.toLocaleString() || '10,000'} simulations • BO{bestOf}
          </p>
        </div>
        <button
          onClick={() => setShowProbabilities(!showProbabilities)}
          className="px-4 py-2 bg-valorant-dark hover:bg-gray-700 text-white rounded-lg transition-colors text-sm"
        >
          {showProbabilities ? 'Hide' : 'Show'} Probabilities
        </button>
      </div>

      {/* Bracket Grid */}
      <div className="overflow-x-auto pb-4">
        <div className="flex gap-8 min-w-max">
          {Object.keys(bracket).map(round => (
            <div key={round} className="flex flex-col" style={{ minWidth: '280px' }}>
              {/* Round Header */}
              <div className="text-center mb-4 pb-2 border-b border-gray-700">
                <h3 className="font-bold text-lg">{getRoundName(parseInt(round))}</h3>
              </div>

              {/* Matchups */}
              <div className="flex flex-col justify-around flex-1 gap-4">
                {bracket[round].map((matchup, idx) => (
                  <div 
                    key={idx} 
                    className="bg-valorant-dark rounded-lg p-4 border-2 border-gray-700 hover:border-valorant-red transition-colors"
                    style={{
                      marginTop: idx > 0 ? `${Math.pow(2, parseInt(round) - 1) * 20}px` : '0'
                    }}
                  >
                    {/* Team 1 */}
                    <div className={`flex items-center justify-between p-2 rounded ${
                      parseFloat(matchup.team1Prob) > parseFloat(matchup.team2Prob || 0)
                        ? 'bg-valorant-red/20 border-l-4 border-valorant-red'
                        : 'bg-gray-800'
                    }`}>
                      <div className="flex-1">
                        <div className="font-medium text-sm">
                          #{matchup.team1.seed} {matchup.team1.name}
                        </div>
                        {showProbabilities && (
                          <div className="text-xs text-gray-400 mt-1">
                            ELO: {Math.round(matchup.team1.elo_rating)}
                          </div>
                        )}
                      </div>
                      {showProbabilities && (
                        <div className="ml-3 font-bold text-white">
                          {matchup.team1Prob}%
                        </div>
                      )}
                    </div>

                    {/* VS Divider */}
                    <div className="text-center text-xs text-gray-500 my-1">vs</div>

                    {/* Team 2 */}
                    {matchup.team2 ? (
                      <div className={`flex items-center justify-between p-2 rounded ${
                        parseFloat(matchup.team2Prob) > parseFloat(matchup.team1Prob)
                          ? 'bg-valorant-red/20 border-l-4 border-valorant-red'
                          : 'bg-gray-800'
                      }`}>
                        <div className="flex-1">
                          <div className="font-medium text-sm">
                            #{matchup.team2.seed} {matchup.team2.name}
                          </div>
                          {showProbabilities && (
                            <div className="text-xs text-gray-400 mt-1">
                              ELO: {Math.round(matchup.team2.elo_rating)}
                            </div>
                          )}
                        </div>
                        {showProbabilities && (
                          <div className="ml-3 font-bold text-white">
                            {matchup.team2Prob}%
                          </div>
                        )}
                      </div>
                    ) : (
                      <div className="flex items-center justify-center p-2 rounded bg-gray-800 text-gray-500 text-sm italic">
                        Bye
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          ))}

          {/* Champion Column */}
          <div className="flex flex-col" style={{ minWidth: '280px' }}>
            <div className="text-center mb-4 pb-2 border-b border-gray-700">
              <h3 className="font-bold text-lg">Champion</h3>
            </div>
            <div className="flex items-center justify-center flex-1">
              <div className="bg-gradient-to-br from-valorant-red to-red-700 rounded-lg p-6 border-4 border-valorant-red shadow-lg w-full">
                <div className="text-center">
                  <div className="text-2xl font-bold mb-2">
                    #{results[0].seed} {results[0].name}
                  </div>
                  <div className="text-4xl font-black mb-2">
                    {results[0].championship_prob.toFixed(1)}%
                  </div>
                  <div className="text-sm text-gray-200">
                    Most Likely Winner
                  </div>
                  <div className="text-xs text-gray-300 mt-2">
                    ELO: {Math.round(results[0].elo_rating)}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Legend */}
      <div className="mt-6 pt-4 border-t border-gray-700">
        <div className="flex items-center gap-6 text-sm text-gray-400">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 bg-valorant-red/20 border-l-4 border-valorant-red rounded"></div>
            <span>Favorite (higher win probability)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 bg-gray-800 rounded"></div>
            <span>Underdog</span>
          </div>
        </div>
        <p className="text-xs text-gray-500 mt-2">
          * Bracket shows most probable matchups. Actual results may vary based on simulation outcomes.
        </p>
      </div>
    </div>
  );
}

export default BracketVisualization;