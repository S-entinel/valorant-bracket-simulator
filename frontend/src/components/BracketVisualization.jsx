import { useState } from 'react';

function BracketVisualization({ results, teamsCount, bestOf }) {
  const [showProbabilities, setShowProbabilities] = useState(true);

  if (!results || results.length === 0) {
    return (
      <div className="bg-neutral-900 rounded-lg p-12 text-center border border-neutral-800">
        <p className="text-neutral-500 text-sm">No bracket data available</p>
      </div>
    );
  }

  const numRounds = Math.ceil(Math.log2(teamsCount));
  const seededTeams = [...results].sort((a, b) => b.elo_rating - a.elo_rating);

  const generateBracket = () => {
    const bracket = {};
    
    bracket[1] = [];
    const pairCount = Math.ceil(teamsCount / 2);
    
    for (let i = 0; i < pairCount; i++) {
      const team1 = seededTeams[i * 2];
      const team2 = seededTeams[i * 2 + 1];
      
      if (team1 && team2) {
        const team1Prob = team1.championship_prob / (team1.championship_prob + team2.championship_prob) * 100;
        const team2Prob = 100 - team1Prob;
        
        bracket[1].push({
          team1,
          team2,
          team1Prob: team1Prob.toFixed(1),
          team2Prob: team2Prob.toFixed(1)
        });
      } else if (team1) {
        bracket[1].push({
          team1,
          team2: null,
          team1Prob: 100,
          team2Prob: 0
        });
      }
    }

    for (let round = 2; round <= numRounds; round++) {
      bracket[round] = [];
      const prevRoundMatchups = bracket[round - 1];
      
      for (let i = 0; i < prevRoundMatchups.length; i += 2) {
        const match1 = prevRoundMatchups[i];
        const match2 = prevRoundMatchups[i + 1];
        
        if (match1 && match2) {
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

  const getRoundName = (round) => {
    if (round === numRounds) return 'Finals';
    if (round === numRounds - 1) return 'Semifinals';
    if (round === numRounds - 2) return 'Quarterfinals';
    return `Round ${round}`;
  };

  return (
    <div className="bg-neutral-900 rounded-lg p-6 border border-neutral-800">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-xl font-semibold">Tournament Bracket</h2>
          <p className="text-neutral-500 text-xs mt-1">
            Probable matchups based on {results[0].num_simulations?.toLocaleString() || '10,000'} simulations • BO{bestOf}
          </p>
        </div>
        <button
          onClick={() => setShowProbabilities(!showProbabilities)}
          className="px-3 py-1.5 bg-neutral-800 hover:bg-neutral-700 text-white rounded-md transition-colors text-sm"
        >
          {showProbabilities ? 'Hide' : 'Show'} Probabilities
        </button>
      </div>

      <div className="overflow-x-auto pb-4">
        <div className="flex gap-8 min-w-max">
          {Object.keys(bracket).map(round => (
            <div key={round} className="flex flex-col" style={{ minWidth: '280px' }}>
              <div className="text-center mb-4 pb-2 border-b border-neutral-800">
                <h3 className="font-medium text-sm text-neutral-300">{getRoundName(parseInt(round))}</h3>
              </div>

              <div className="flex flex-col justify-around flex-1 gap-4">
                {bracket[round].map((matchup, idx) => (
                  <div 
                    key={idx} 
                    className="bg-black rounded-md p-3 border border-neutral-800 hover:border-neutral-600 transition-colors"
                    style={{
                      marginTop: idx > 0 ? `${Math.pow(2, parseInt(round) - 1) * 20}px` : '0'
                    }}
                  >
                    <div className={`flex items-center justify-between p-2 rounded-sm ${
                      parseFloat(matchup.team1Prob) > parseFloat(matchup.team2Prob || 0)
                        ? 'bg-neutral-800 border-l-2 border-white'
                        : 'bg-neutral-900'
                    }`}>
                      <div className="flex-1">
                        <div className="font-medium text-xs text-white">
                          #{matchup.team1.seed} {matchup.team1.name}
                        </div>
                        {showProbabilities && (
                          <div className="text-xs text-neutral-500 mt-0.5">
                            ELO: {Math.round(matchup.team1.elo_rating)}
                          </div>
                        )}
                      </div>
                      {showProbabilities && (
                        <div className="ml-2 font-semibold text-white text-xs">
                          {matchup.team1Prob}%
                        </div>
                      )}
                    </div>

                    <div className="text-center text-xs text-neutral-600 my-1">vs</div>

                    {matchup.team2 ? (
                      <div className={`flex items-center justify-between p-2 rounded-sm ${
                        parseFloat(matchup.team2Prob) > parseFloat(matchup.team1Prob)
                          ? 'bg-neutral-800 border-l-2 border-white'
                          : 'bg-neutral-900'
                      }`}>
                        <div className="flex-1">
                          <div className="font-medium text-xs text-white">
                            #{matchup.team2.seed} {matchup.team2.name}
                          </div>
                          {showProbabilities && (
                            <div className="text-xs text-neutral-500 mt-0.5">
                              ELO: {Math.round(matchup.team2.elo_rating)}
                            </div>
                          )}
                        </div>
                        {showProbabilities && (
                          <div className="ml-2 font-semibold text-white text-xs">
                            {matchup.team2Prob}%
                          </div>
                        )}
                      </div>
                    ) : (
                      <div className="flex items-center justify-center p-2 rounded-sm bg-neutral-900 text-neutral-600 text-xs italic">
                        Bye
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          ))}

          <div className="flex flex-col" style={{ minWidth: '280px' }}>
            <div className="text-center mb-4 pb-2 border-b border-neutral-800">
              <h3 className="font-medium text-sm text-neutral-300">Champion</h3>
            </div>
            <div className="flex items-center justify-center flex-1">
              <div className="bg-white rounded-lg p-6 border-2 border-white shadow-lg w-full">
                <div className="text-center">
                  <div className="text-xl font-semibold mb-2 text-black">
                    #{results[0].seed} {results[0].name}
                  </div>
                  <div className="text-4xl font-bold mb-2 text-black">
                    {results[0].championship_prob.toFixed(1)}%
                  </div>
                  <div className="text-xs text-neutral-700">
                    Most Likely Winner
                  </div>
                  <div className="text-xs text-neutral-600 mt-2">
                    ELO: {Math.round(results[0].elo_rating)}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="mt-6 pt-4 border-t border-neutral-800">
        <div className="flex items-center gap-6 text-xs text-neutral-500">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 bg-neutral-800 border-l-2 border-white rounded-sm"></div>
            <span>Favorite (higher win probability)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 bg-neutral-900 border border-neutral-800 rounded-sm"></div>
            <span>Underdog</span>
          </div>
        </div>
        <p className="text-xs text-neutral-600 mt-2">
          Bracket shows most probable matchups. Actual results may vary based on simulation outcomes.
        </p>
      </div>
    </div>
  );
}

export default BracketVisualization;