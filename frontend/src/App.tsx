import React, { useState, useEffect } from 'react';
import { CharacterData, ItemData } from './types';
import * as api from './api';
import { CharacterCard } from './components/CharacterCard';
import { InventoryView } from './components/InventoryView';
import { ItemPoolView } from './components/ItemPoolView';
import { GameControls } from './components/GameControls';
import { AttackModal } from './components/AttackModal';

export const App: React.FC = () => {
  const [characters, setCharacters] = useState<CharacterData[]>([]);
  const [itemPool, setItemPool] = useState<ItemData[]>([]);
  const [selectedCharId, setSelectedCharId] = useState<number | null>(null);
  const [currentTurnId, setCurrentTurnId] = useState<number | null>(null);
  const [attackModalAttacker, setAttackModalAttacker] = useState<CharacterData | null>(null);
  const [gameStarted, setGameStarted] = useState<boolean>(false);
  const [isSaving, setIsSaving] = useState<boolean>(false);
  const [toastMessage, setToastMessage] = useState<string | null>(null);
  const [toastTimer, setToastTimer] = useState<any>(null);

  const showToast = (msg: string) => {
    if (toastTimer) clearTimeout(toastTimer);
    setToastMessage(msg);
    const timer = setTimeout(() => setToastMessage(null), 3500);
    setToastTimer(timer);
  };

  // Initial load
  const loadState = async () => {
    try {
      const state = await api.fetchGameState();
      setCharacters(state.characters);
      setItemPool(state.item_pool);
      setGameStarted(state.game_started);
      setCurrentTurnId(state.current_turn_character_id);
    } catch (err: any) {
      console.error('Failed to load game state:', err);
      showToast(`Error connecting to backend: ${err.message}`);
    }
  };

  useEffect(() => {
    loadState();
  }, []);

  // Selected character reference
  const selectedCharacter = characters.find((c) => c.id === selectedCharId) || null;

  // Active turn character reference
  const activeTurnCharacter = characters.find((c) => c.id === currentTurnId) || null;

  // Split into players and enemies
  const players = characters.filter((c) => c.side === 'player');
  const enemies = characters.filter((c) => c.side === 'enemy');

  // Handle Add Player / Add Enemy
  const handleAddNewCharacter = async (side: 'player' | 'enemy') => {
    try {
      const randomTraits = await api.generateRandomTraits(3);
      // Create a temporary client-side draft character with negative id
      const tempId = -Date.now();
      const draft: CharacterData = {
        id: tempId,
        name: '',
        side,
        status: side,
        strength: randomTraits.strength ?? 5,
        dexterity: randomTraits.dexterity ?? 5,
        toughness: randomTraits.toughness ?? 5,
        perseverance: randomTraits.perseverance ?? 5,
        brilliance: randomTraits.brilliance ?? 5,
        senses: randomTraits.senses ?? 5,
        presence: randomTraits.presence ?? 5,
        sharpstrike: randomTraits.sharpstrike ?? 0,
        ravage: randomTraits.ravage ?? 0,
        melee: randomTraits.melee ?? 0,
        special: randomTraits.special ?? 0,
        stealth: randomTraits.stealth ?? 0,
        hardware: randomTraits.hardware ?? 0,
        ordnance: randomTraits.ordnance ?? 0,
        medical: randomTraits.medical ?? 0,
        health: 5,
        head: 1,
        torso: 3,
        right_arm: 2,
        left_arm: 2,
        right_leg: 2,
        left_leg: 2,
        full_cover: 0,
        head_cover: 0,
        torso_cover: 0,
        right_arm_cover: 0,
        left_arm_cover: 0,
        right_leg_cover: 0,
        left_leg_cover: 0,
        mental: 0,
        movement_stat: 0,
        stamina: randomTraits.dexterity ?? 5,
        injury: {
          head: null,
          torso: null,
          right_arm: null,
          left_arm: null,
          right_leg: null,
          left_leg: null,
          general: [],
        },
        effects: [],
        inventory: [],
        isNewDraft: true,
      };

      setCharacters((prev) => [draft, ...prev]);
      setSelectedCharId(tempId);
      showToast(`New ${side} created! Please enter a name to save.`);
    } catch (err: any) {
      showToast(`Error initializing new character: ${err.message}`);
    }
  };

  // Once name is given to draft character, save it to the backend!
  const handleSaveNewCharacter = async (draft: CharacterData) => {
    try {
      const created = await api.createCharacter({
        name: draft.name,
        side: draft.side,
        difficulty: 3,
        traits: {
          strength: draft.strength,
          dexterity: draft.dexterity,
          toughness: draft.toughness,
          perseverance: draft.perseverance,
          brilliance: draft.brilliance,
          senses: draft.senses,
          presence: draft.presence,
          sharpstrike: draft.sharpstrike,
          ravage: draft.ravage,
          melee: draft.melee,
          special: draft.special,
          stealth: draft.stealth,
          hardware: draft.hardware,
          ordnance: draft.ordnance,
          medical: draft.medical,
          health: draft.health,
          head: draft.head,
          torso: draft.torso,
          right_arm: draft.right_arm,
          left_arm: draft.left_arm,
          right_leg: draft.right_leg,
          left_leg: draft.left_leg,
        },
      });

      // Replace draft with persisted character
      setCharacters((prev) =>
        prev.map((c) => (c.id === draft.id ? { ...created, isNewDraft: false } : c))
      );
      setSelectedCharId(created.id);
      showToast(`Character "${created.name}" saved successfully!`);
    } catch (err: any) {
      showToast(`Error saving character: ${err.message}`);
    }
  };

  // Update existing character
  const handleUpdateCharacter = async (id: number, updates: Partial<CharacterData>) => {
    // Optimistic local update
    setCharacters((prev) =>
      prev.map((c) => (c.id === id ? { ...c, ...updates } : c))
    );

    try {
      const updated = await api.updateCharacter(id, updates);
      setCharacters((prev) =>
        prev.map((c) => (c.id === id ? updated : c))
      );
    } catch (err: any) {
      showToast(`Error updating character: ${err.message}`);
      loadState();
    }
  };

  // Randomize traits for character
  const handleRandomizeTraits = async (id: number, difficulty: number) => {
    try {
      const updated = await api.randomizeCharacterTraits(id, difficulty);
      setCharacters((prev) =>
        prev.map((c) => (c.id === id ? updated : c))
      );
      showToast(`Traits randomized for "${updated.name}" (Difficulty ${difficulty})`);
    } catch (err: any) {
      showToast(`Failed to randomize traits: ${err.message}`);
    }
  };

  // Delete character
  const handleDeleteCharacter = async (id: number) => {
    try {
      await api.deleteCharacter(id);
      setCharacters((prev) => prev.filter((c) => c.id !== id));
      if (selectedCharId === id) setSelectedCharId(null);
      if (currentTurnId === id) setCurrentTurnId(null);
      showToast('Character removed.');
    } catch (err: any) {
      showToast(`Error deleting character: ${err.message}`);
    }
  };

  // Inventory: Randomize
  const handleRandomizeInventory = async (charId: number, difficulty: number) => {
    try {
      const newItems = await api.randomizeInventory(charId, difficulty);
      setCharacters((prev) =>
        prev.map((c) => (c.id === charId ? { ...c, inventory: newItems } : c))
      );
      showToast('Inventory randomized!');
    } catch (err: any) {
      showToast(`Error randomizing inventory: ${err.message}`);
    }
  };

  // Inventory: Delete item
  const handleDeleteItem = async (charId: number, itemId: string) => {
    try {
      const updatedInventory = await api.deleteItemFromInventory(charId, itemId);
      setCharacters((prev) =>
        prev.map((c) => (c.id === charId ? { ...c, inventory: updatedInventory } : c))
      );
      showToast('Item removed from inventory.');
    } catch (err: any) {
      showToast(`Error deleting item: ${err.message}`);
    }
  };

  // Inventory: Reload weapon
  const handleReloadWeapon = async (charId: number, itemId: string) => {
    try {
      const res = await api.reloadWeapon(charId, itemId);
      showToast(res.message);
      await loadState();
    } catch (err: any) {
      showToast(`Reload failed: ${err.message}`);
    }
  };

  // Inventory: Equip weapon
  const handleEquipWeapon = async (charId: number, itemId: string) => {
    try {
      const res = await api.equipWeapon(charId, itemId);
      showToast(res.message);
      await loadState();
    } catch (err: any) {
      showToast(`Equip failed: ${err.message}`);
    }
  };

  // Inventory: Drop / Add item from Pool
  const handleAddItemToInventory = async (charId: number, itemName: string) => {
    try {
      const updatedInventory = await api.addItemToInventory(charId, itemName);
      setCharacters((prev) =>
        prev.map((c) => (c.id === charId ? { ...c, inventory: updatedInventory } : c))
      );
      showToast(`Added ${itemName} to inventory.`);
    } catch (err: any) {
      showToast(`Error adding item: ${err.message}`);
    }
  };

  // Game Controls: Start Game
  const handleStartGame = async () => {
    if (characters.length === 0) {
      showToast('Please add at least one character to start the game.');
      return;
    }
    try {
      const res = await api.startGame();
      setGameStarted(true);
      setCurrentTurnId(res.current_turn_character_id);
      showToast('Game started! Initiative rounds determined.');
    } catch (err: any) {
      showToast(`Cannot start game: ${err.message}`);
    }
  };

  // Game Controls: Next Turn
  const handleNextTurn = async () => {
    try {
      const res = await api.nextTurn();
      if (res.game_over) {
        showToast(res.message || 'Game over!');
        setCurrentTurnId(null);
      } else {
        setCurrentTurnId(res.current_turn_character_id);
        const nextChar = characters.find((c) => c.id === res.current_turn_character_id);
        showToast(`Next turn: ${nextChar ? nextChar.name : 'Unknown'}`);
      }
    } catch (err: any) {
      showToast(`Failed to advance turn: ${err.message}`);
    }
  };

  // Game Controls: Stop Game
  const handleStopGame = async () => {
    try {
      const res = await api.stopGame();
      setGameStarted(false);
      setCurrentTurnId(null);
      showToast(res.message || 'Game stopped.');
      await loadState();
    } catch (err: any) {
      showToast(`Failed to stop game: ${err.message}`);
    }
  };

  // Attack Execution
  const handleExecuteAttack = async (attackerId: number, targetId: number, bodypart: string) => {
    try {
      const res = await api.attackCharacter(attackerId, targetId, bodypart);
      showToast(res.message);
      await loadState();
    } catch (err: any) {
      showToast(`Attack failed: ${err.message}`);
    }
  };

  // Game Controls: Save Game
  const handleSaveGame = async () => {
    setIsSaving(true);
    try {
      const res = await api.saveGame();
      showToast(res.message || 'Game saved to backend database.');
    } catch (err: any) {
      showToast(`Save failed: ${err.message}`);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="app-container">
      {/* Top Bar Header */}
      <header className="app-header">
        <div className="app-title-group">
          <span className="app-title">Tabletop RPG Combat Engine</span>
          {gameStarted && (
            <div className={`turn-badge ${currentTurnId ? 'active-pulse' : ''}`}>
              <span>Round Active</span>
              {activeTurnCharacter && <span>• {activeTurnCharacter.name}</span>}
            </div>
          )}
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <span style={{ fontSize: '0.8rem', color: '#9aa4b2' }}>
            Players: {players.length} | Enemies: {enemies.length}
          </span>
        </div>
      </header>

      {/* Main Layout Area: Players | Center Area (Inventory + Item pool + Controls) | Enemies */}
      <main className="app-main">
        {/* Left Column: Players */}
        <section className="column-panel">
          <div className="column-header">
            <span className="column-title players">
              <img
                src="/images/character.png"
                alt="Players"
                style={{ width: '22px', height: '22px', objectFit: 'contain' }}
              />
              Players
            </span>
            <span style={{ fontSize: '0.75rem', color: '#9aa4b2' }}>{players.length} units</span>
          </div>

          <div className="character-list">
            {players.length === 0 ? (
              <div style={{ textAlign: 'center', color: '#647082', marginTop: '40px', fontSize: '0.85rem' }}>
                No players added yet.<br />Use "+ [player]" below.
              </div>
            ) : (
              players.map((char) => (
                <CharacterCard
                  key={char.id}
                  character={char}
                  isSelected={selectedCharId === char.id}
                  isCurrentTurn={currentTurnId === char.id}
                  onSelect={() => setSelectedCharId(char.id)}
                  onUpdate={handleUpdateCharacter}
                  onRandomizeTraits={handleRandomizeTraits}
                  onSaveNewCharacter={handleSaveNewCharacter}
                  onDeleteCharacter={handleDeleteCharacter}
                  onOpenAttackModal={(c) => setAttackModalAttacker(c)}
                  onToast={showToast}
                />
              ))
            )}
          </div>
        </section>

        {/* Center Column: Item pool + sliding inventory + game controls */}
        <section className="center-panel">
          <div className="center-content-area">
            {/* Sliding inventory for selected Player (slides on the left side of center area) */}
            {selectedCharacter && selectedCharacter.side === 'player' && (
              <InventoryView
                character={selectedCharacter}
                onRandomizeInventory={handleRandomizeInventory}
                onDeleteItem={handleDeleteItem}
                onReloadWeapon={handleReloadWeapon}
                onEquipWeapon={handleEquipWeapon}
                onDropItem={handleAddItemToInventory}
                onClose={() => setSelectedCharId(null)}
              />
            )}

            {/* Item Pool Panel in the center */}
            <ItemPoolView
              items={itemPool}
              selectedCharacterName={selectedCharacter?.name}
              onAddItemToSelected={
                selectedCharacter
                  ? (name) => handleAddItemToInventory(selectedCharacter.id, name)
                  : undefined
              }
            />

            {/* Sliding inventory for selected Enemy (slides on the right side of center area) */}
            {selectedCharacter && selectedCharacter.side === 'enemy' && (
              <InventoryView
                character={selectedCharacter}
                onRandomizeInventory={handleRandomizeInventory}
                onDeleteItem={handleDeleteItem}
                onReloadWeapon={handleReloadWeapon}
                onEquipWeapon={handleEquipWeapon}
                onDropItem={handleAddItemToInventory}
                onClose={() => setSelectedCharId(null)}
              />
            )}
          </div>

          {/* Game Controls at lower middle */}
          <GameControls
            onAddPlayer={() => handleAddNewCharacter('player')}
            onAddEnemy={() => handleAddNewCharacter('enemy')}
            onStartGame={handleStartGame}
            onNextTurn={handleNextTurn}
            onStopGame={handleStopGame}
            onSaveGame={handleSaveGame}
            gameStarted={gameStarted}
            isSaving={isSaving}
            activeCharacterName={activeTurnCharacter?.name}
          />
        </section>

        {/* Right Column: Enemies */}
        <section className="column-panel">
          <div className="column-header">
            <span className="column-title enemies">
              <img
                src="/images/enemy.png"
                alt="Enemies"
                style={{ width: '22px', height: '22px', objectFit: 'contain' }}
              />
              Enemies
            </span>
            <span style={{ fontSize: '0.75rem', color: '#9aa4b2' }}>{enemies.length} units</span>
          </div>

          <div className="character-list">
            {enemies.length === 0 ? (
              <div style={{ textAlign: 'center', color: '#647082', marginTop: '40px', fontSize: '0.85rem' }}>
                No enemies added yet.<br />Use "+ [enemy]" below.
              </div>
            ) : (
              enemies.map((char) => (
                <CharacterCard
                  key={char.id}
                  character={char}
                  isSelected={selectedCharId === char.id}
                  isCurrentTurn={currentTurnId === char.id}
                  onSelect={() => setSelectedCharId(char.id)}
                  onUpdate={handleUpdateCharacter}
                  onRandomizeTraits={handleRandomizeTraits}
                  onSaveNewCharacter={handleSaveNewCharacter}
                  onDeleteCharacter={handleDeleteCharacter}
                  onOpenAttackModal={(c) => setAttackModalAttacker(c)}
                  onToast={showToast}
                />
              ))
            )}
          </div>
        </section>
      </main>

      {/* Attack Targeting Modal */}
      <AttackModal
        attacker={attackModalAttacker}
        characters={characters}
        isOpen={!!attackModalAttacker}
        onClose={() => setAttackModalAttacker(null)}
        onExecuteAttack={handleExecuteAttack}
      />

      {/* Toast Notification Bar */}
      {toastMessage && (
        <div className="toast-bar">
          <span></span>
          <span>{toastMessage}</span>
        </div>
      )}
    </div>
  );
};
export default App;
