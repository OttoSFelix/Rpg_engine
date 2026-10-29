import React from 'react';

interface GameControlsProps {
  onAddPlayer: () => void;
  onAddEnemy: () => void;
  onStartGame: () => void;
  onNextTurn: () => void;
  onStopGame: () => void;
  onSaveGame: () => void;
  gameStarted: boolean;
  isSaving: boolean;
  activeCharacterName?: string;
}

export const GameControls: React.FC<GameControlsProps> = ({
  onAddPlayer,
  onAddEnemy,
  onStartGame,
  onNextTurn,
  onStopGame,
  onSaveGame,
  gameStarted,
  isSaving,
  activeCharacterName,
}) => {
  return (
    <div className="game-controls-card">
      <div className="controls-label">
        Game controls {gameStarted && activeCharacterName ? `• Turn: ${activeCharacterName}` : ''}
      </div>

      <div className="controls-row-top">
        {/* Add Player / Teammate Button */}
        <button
          className="btn-ctrl add-player"
          onClick={onAddPlayer}
          title="Add a new player / teammate"
        >
          <span style={{ fontSize: '1.1rem', fontWeight: 900 }}>+</span>
          <img
            src="/images/character.png"
            alt="Player"
            style={{ width: '22px', height: '22px', objectFit: 'contain' }}
          />
        </button>

        {/* Start Game / Next Turn Button */}
        {!gameStarted ? (
          <button className="btn-ctrl start-game" onClick={onStartGame} title="Start Game">
            Start
          </button>
        ) : (
          <button
            className="btn-ctrl next-turn"
            onClick={onNextTurn}
            title="Advance to next turn"
          >
            Next Turn ❯
          </button>
        )}

        {/* Add Enemy Button */}
        <button className="btn-ctrl add-enemy" onClick={onAddEnemy} title="Add a new enemy">
          <span style={{ fontSize: '1.1rem', fontWeight: 900 }}>+</span>
          <img
            src="/images/enemy.png"
            alt="Enemy"
            style={{ width: '22px', height: '22px', objectFit: 'contain' }}
          />
        </button>
      </div>

      {/* Save & Stop Buttons */}
      <div className="controls-row-bottom" style={{ display: 'flex', gap: '12px', justifyContent: 'center' }}>
        <button
          className="btn-ctrl save-game"
          onClick={onSaveGame}
          disabled={isSaving}
          title="Save game to backend database"
        >
          {isSaving ? 'Saving...' : 'Save'}
        </button>

        <button
          className="btn-ctrl stop-game"
          onClick={onStopGame}
          disabled={!gameStarted}
          title={gameStarted ? 'Stop the current game' : 'Game has not started yet'}
        >
          Stop
        </button>
      </div>
    </div>
  );
};
