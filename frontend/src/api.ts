import { CharacterData, GameState, ItemData } from './types';

const API_BASE = '/api';

export async function fetchGameState(): Promise<GameState> {
  const res = await fetch(`${API_BASE}/game/state`);
  if (!res.ok) throw new Error(`Failed to fetch game state: ${res.statusText}`);
  return res.json();
}

export async function generateRandomTraits(difficulty: number = 3): Promise<Record<string, number>> {
  const res = await fetch(`${API_BASE}/characters/generate-traits`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ difficulty }),
  });
  if (!res.ok) throw new Error(`Failed to generate traits: ${res.statusText}`);
  return res.json();
}

export async function createCharacter(params: {
  name: string;
  side: 'player' | 'enemy';
  difficulty?: number;
  traits?: Record<string, any>;
}): Promise<CharacterData> {
  const res = await fetch(`${API_BASE}/characters`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  });
  if (!res.ok) throw new Error(`Failed to create character: ${res.statusText}`);
  return res.json();
}

export async function updateCharacter(
  id: number,
  updates: Partial<CharacterData>
): Promise<CharacterData> {
  const res = await fetch(`${API_BASE}/characters/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(updates),
  });
  if (!res.ok) throw new Error(`Failed to update character ${id}: ${res.statusText}`);
  return res.json();
}

export async function deleteCharacter(id: number): Promise<{ success: boolean }> {
  const res = await fetch(`${API_BASE}/characters/${id}`, {
    method: 'DELETE',
  });
  if (!res.ok) throw new Error(`Failed to delete character ${id}: ${res.statusText}`);
  return res.json();
}

export async function randomizeCharacterTraits(
  id: number,
  difficulty: number
): Promise<CharacterData> {
  const res = await fetch(`${API_BASE}/characters/${id}/randomize`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ difficulty }),
  });
  if (!res.ok) throw new Error(`Failed to randomize traits for character ${id}: ${res.statusText}`);
  return res.json();
}

export async function randomizeInventory(
  id: number,
  difficulty: number
): Promise<ItemData[]> {
  const res = await fetch(`${API_BASE}/characters/${id}/inventory/randomize`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ difficulty }),
  });
  if (!res.ok) throw new Error(`Failed to randomize inventory for character ${id}: ${res.statusText}`);
  return res.json();
}

export async function addItemToInventory(
  charId: number,
  itemName: string
): Promise<ItemData[]> {
  const res = await fetch(`${API_BASE}/characters/${charId}/inventory/add`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ item_name: itemName }),
  });
  if (!res.ok) throw new Error(`Failed to add ${itemName} to character ${charId}: ${res.statusText}`);
  return res.json();
}

export async function deleteItemFromInventory(
  charId: number,
  itemId: string
): Promise<ItemData[]> {
  const res = await fetch(`${API_BASE}/characters/${charId}/inventory/${itemId}`, {
    method: 'DELETE',
  });
  if (!res.ok) throw new Error(`Failed to delete item ${itemId} from character ${charId}: ${res.statusText}`);
  return res.json();
}

export async function reloadWeapon(
  charId: number,
  itemId: string
): Promise<{ success: boolean; message: string; magazine_bullets?: number; inventory?: ItemData[]; current_turn_character_id?: number | null }> {
  const res = await fetch(`${API_BASE}/characters/${charId}/inventory/${itemId}/reload`, {
    method: 'POST',
  });
  if (!res.ok) throw new Error(`Failed to reload weapon ${itemId}: ${res.statusText}`);
  return res.json();
}

export async function equipWeapon(
  charId: number,
  itemId: string
): Promise<{
  success: boolean;
  message: string;
  held_weapon_id?: string;
  current_turn_character_id?: number | null;
  character?: CharacterData;
  inventory?: ItemData[];
}> {
  const res = await fetch(`${API_BASE}/characters/${charId}/inventory/${itemId}/equip`, {
    method: 'POST',
  });
  if (!res.ok) throw new Error(`Failed to equip weapon ${itemId}: ${res.statusText}`);
  return res.json();
}

export async function startGame(): Promise<{
  success: boolean;
  game_started: boolean;
  current_turn_character_id: number | null;
  round_table: number[];
}> {
  const res = await fetch(`${API_BASE}/game/start`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({}),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || 'Failed to start game');
  }
  return res.json();
}

export async function nextTurn(): Promise<{
  success?: boolean;
  game_over?: boolean;
  message?: string;
  current_turn_character_id: number | null;
}> {
  const res = await fetch(`${API_BASE}/game/next-turn`, {
    method: 'POST',
  });
  if (!res.ok) throw new Error(`Failed to step turn: ${res.statusText}`);
  return res.json();
}

export async function stopGame(): Promise<{
  success: boolean;
  message: string;
  game_started: boolean;
  current_turn_character_id: number | null;
}> {
  const res = await fetch(`${API_BASE}/game/stop`, {
    method: 'POST',
  });
  if (!res.ok) throw new Error(`Failed to stop game: ${res.statusText}`);
  return res.json();
}

export async function attackCharacter(
  attackerId: number,
  targetId: number,
  bodypart: string
): Promise<{
  success: boolean;
  hit: boolean;
  damage_dealt: number;
  message: string;
  attacker: CharacterData;
  target: CharacterData;
}> {
  const res = await fetch(`${API_BASE}/characters/${attackerId}/attack`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ target_id: targetId, bodypart }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || 'Attack request failed');
  }
  return res.json();
}

export async function saveGame(): Promise<{ success: boolean; message: string }> {
  const res = await fetch(`${API_BASE}/game/save`, {
    method: 'POST',
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || 'Failed to save game');
  }
  return res.json();
}
