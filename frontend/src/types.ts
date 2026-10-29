export interface ItemData {
  item_id: string;
  name: string;
  weight: number;
  is_weapon: boolean;
  type: string;
  damage?: number | null;
  damage_type?: string | null;
  range?: number | null;
  power?: number | null;
  precision?: number | null;
  magazine_bullets?: number | null;
  magazine_size?: number | null;
  effect?: string | null;
  wakes_up?: boolean | null;
  is_held?: boolean;
}

export interface Injuries {
  head: string | null;
  torso: string | null;
  right_arm: string | null;
  left_arm: string | null;
  right_leg: string | null;
  left_leg: string | null;
  general: string[];
}

export interface CharacterData {
  id: number;
  name: string;
  side: 'player' | 'enemy';
  status: string;
  // Personal traits
  strength: number;
  dexterity: number;
  toughness: number;
  perseverance: number;
  brilliance: number;
  senses: number;
  presence: number;
  // Skills
  sharpstrike: number;
  ravage: number;
  melee: number;
  special: number;
  stealth: number;
  hardware: number;
  ordnance: number;
  medical: number;
  // Health & Bodyparts
  health: number;
  head: number;
  torso: number;
  right_arm: number;
  left_arm: number;
  right_leg: number;
  left_leg: number;
  // Covers
  full_cover: number;
  head_cover: number;
  torso_cover: number;
  right_arm_cover: number;
  left_arm_cover: number;
  right_leg_cover: number;
  left_leg_cover: number;
  // Other
  mental: number;
  movement_stat: number;
  stamina: number;
  // Injuries & inventory
  injury: Injuries;
  effects: any[];
  inventory: ItemData[];
  held_weapon_id?: string | null;
  held_weapon_name?: string | null;
  // Temporary client-side flag for unsaved characters
  isNewDraft?: boolean;
}

export interface GameState {
  characters: CharacterData[];
  item_pool: ItemData[];
  game_started: boolean;
  current_turn_character_id: number | null;
  round_table: number[];
  round_pointer: number;
}
