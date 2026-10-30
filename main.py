import builtins
import os
import random
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

class DummyWeapon: pass
class DummyStim: pass
class DummyOrdnance: pass
class DummyTool: pass
class DummyItem: pass

for cls in [DummyWeapon, DummyStim, DummyOrdnance, DummyTool, DummyItem]:
    name = cls.__name__.replace("Dummy", "")
    if not hasattr(builtins, name):
        setattr(builtins, name, cls)

from engine.engine import Game
import engine.items
from engine.character import Character

orig_stim_init = engine.items.Stim.__init__
def safe_stim_init(self, item_id, name, effect, cure=None, duration=0, weight=0, wakes_up=False):
    if cure is None:
        cure = []
    orig_stim_init(self, item_id=item_id, name=name, effect=effect, cure=cure, duration=duration, weight=weight, wakes_up=wakes_up)
engine.items.Stim.__init__ = safe_stim_init

orig_weapon_attack = engine.items.Weapon.attack
def safe_weapon_attack(self, modifier: int) -> list:
    if getattr(self, "bullet_amount", None) is None:
        self.bullet_amount = 1
    return orig_weapon_attack(self, modifier)
engine.items.Weapon.attack = safe_weapon_attack

app = FastAPI(
    title="RPG Engine API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if os.path.exists("images"):
    app.mount("/images", StaticFiles(directory="images"), name="images")

game = Game()
game_started = False
current_turn_character_id: Optional[int] = None

@app.on_event("startup")
def startup_event():
    try:
        game.initialize()
    except Exception as e:
        print(f"Startup database initialization warning (may be empty or connecting): {e}")

def is_character_down(c: Character) -> bool:
    if hasattr(c, "is_down") and callable(c.is_down):
        try:
            if c.is_down():
                return True
        except Exception:
            pass
    if getattr(c, "health", 1) <= 0:
        return True
    if isinstance(getattr(c, "injury", None), dict):
        gen = c.injury.get("general", [])
        if isinstance(gen, list) and "down" in gen:
            return True
        if gen == "down":
            return True
        if c.injury.get("head") == "down":
            return True
    return False

def serialize_item(item: Any, held_id: Optional[str] = None) -> Dict[str, Any]:
    is_weapon = isinstance(item, engine.items.Weapon)
    item_id = getattr(item, "item_id", "")
    data = {
        "item_id": item_id,
        "name": getattr(item, "name", ""),
        "weight": getattr(item, "weight", 0),
        "is_weapon": is_weapon,
        "is_held": is_weapon and (held_id is not None and item_id == held_id),
        "type": getattr(item, "type", "item"),
        "damage": getattr(item, "damage", None),
        "damage_type": getattr(item, "damage_type", None),
        "range": getattr(item, "range", None),
        "power": getattr(item, "power", None),
        "precision": getattr(item, "precision", None),
        "magazine_bullets": getattr(item, "magazine_bullets", None),
        "magazine_size": getattr(item, "magazine_size", None),
        "effect": getattr(item, "effect", None),
        "wakes_up": getattr(item, "wakes_up", None),
    }
    return data

def serialize_character(c: Character) -> Dict[str, Any]:
    side = "enemy" if (c.status and c.status.lower() == "enemy") else "player"
    held_id = getattr(c.held_weapon, "item_id", None)
    held_name = getattr(c.held_weapon, "name", None)
    return {
        "id": c.id,
        "name": c.name,
        "side": side,
        "status": c.status,
        "held_weapon_id": held_id,
        "held_weapon_name": held_name,
        "strength": c.strength,
        "dexterity": c.dexterity,
        "toughness": c.toughness,
        "perseverance": c.perseverance,
        "brilliance": c.brilliance,
        "senses": c.senses,
        "presence": c.presence,
        "sharpstrike": c.sharpstrike,
        "ravage": c.ravage,
        "melee": c.melee,
        "special": c.special,
        "stealth": c.stealth,
        "hardware": c.hardware,
        "ordnance": c.ordnance,
        "medical": c.medical,
        "health": c.health,
        "head": c.head,
        "torso": c.torso,
        "right_arm": c.right_arm,
        "left_arm": c.left_arm,
        "right_leg": c.right_leg,
        "left_leg": c.left_leg,
        "full_cover": c.full_cover,
        "head_cover": c.head_cover,
        "torso_cover": c.torso_cover,
        "right_arm_cover": c.right_arm_cover,
        "left_arm_cover": c.left_arm_cover,
        "right_leg_cover": c.right_leg_cover,
        "left_leg_cover": c.left_leg_cover,
        "mental": c.mental,
        "movement_stat": c.movement_stat,
        "stamina": c.stamina,
        "injury": {
            "head": c.injury.get("head") if isinstance(c.injury, dict) else None,
            "torso": c.injury.get("torso") if isinstance(c.injury, dict) else None,
            "right_arm": c.injury.get("right_arm") if isinstance(c.injury, dict) else None,
            "left_arm": c.injury.get("left_arm") if isinstance(c.injury, dict) else None,
            "right_leg": c.injury.get("right_leg") if isinstance(c.injury, dict) else None,
            "left_leg": c.injury.get("left_leg") if isinstance(c.injury, dict) else None,
            "general": c.injury.get("general", []) if isinstance(c.injury, dict) else [],
        },
        "effects": c.effects,
        "inventory": [serialize_item(item, held_id=held_id) for item in c.inventory],
    }

def get_item_pool_list() -> List[Dict[str, Any]]:
    pool = []
    pool_keys = [
        "MXR-17", "SP-R 208", "CODA-9", "C4", "flash",
        "Hyposhot Injector", "Hyposhot A", "Hyposhot Z",
        "lockpick", "ravage magazine", "sharpstrike magazine"
    ]
    for key in pool_keys:
        try:
            if key in game.gen_item.item_table:
                it = game.gen_item.item_table[key]()
                pool.append(serialize_item(it))
        except Exception as e:
            print(f"Error instantiating pool item {key}: {e}")
    return pool

class CreateCharacterRequest(BaseModel):
    name: str = ""
    side: str = "player"
    difficulty: int = 3
    traits: Optional[Dict[str, Any]] = None

class UpdateCharacterRequest(BaseModel):
    name: Optional[str] = None
    side: Optional[str] = None
    strength: Optional[int] = None
    dexterity: Optional[int] = None
    toughness: Optional[int] = None
    perseverance: Optional[int] = None
    brilliance: Optional[int] = None
    senses: Optional[int] = None
    presence: Optional[int] = None
    sharpstrike: Optional[int] = None
    ravage: Optional[int] = None
    melee: Optional[int] = None
    special: Optional[int] = None
    stealth: Optional[int] = None
    hardware: Optional[int] = None
    ordnance: Optional[int] = None
    medical: Optional[int] = None
    health: Optional[int] = None
    head: Optional[int] = None
    torso: Optional[int] = None
    right_arm: Optional[int] = None
    left_arm: Optional[int] = None
    right_leg: Optional[int] = None
    left_leg: Optional[int] = None
    head_cover: Optional[int] = None
    torso_cover: Optional[int] = None
    right_arm_cover: Optional[int] = None
    left_arm_cover: Optional[int] = None
    right_leg_cover: Optional[int] = None
    left_leg_cover: Optional[int] = None
    mental: Optional[int] = None
    movement_stat: Optional[int] = None
    stamina: Optional[int] = None
    status: Optional[str] = None

class RandomizeTraitsRequest(BaseModel):
    difficulty: int = 3

class AddItemRequest(BaseModel):
    item_name: str

class StartGameRequest(BaseModel):
    initiative_values: Optional[Dict[str, int]] = None

class AttackRequest(BaseModel):
    target_id: int
    bodypart: str


@app.get("/api/health")
def health_check():
    return {"status": "ok", "game_started": game_started}

@app.get("/api/items/pool")
def get_items_pool():
    return get_item_pool_list()

@app.get("/api/game/state")
def get_game_state():
    global current_turn_character_id
    if game_started and current_turn_character_id is not None:
        if current_turn_character_id in game.character_table:
            curr = game.character_table[current_turn_character_id]
            if is_character_down(curr):
                advance_turn_if_game_active()
        else:
            advance_turn_if_game_active()

    characters = [serialize_character(c) for c in game.character_table.values()]
    return {
        "characters": characters,
        "item_pool": get_item_pool_list(),
        "game_started": game_started,
        "current_turn_character_id": current_turn_character_id,
        "round_table": game.round_table,
        "round_pointer": game.round_pointer,
    }

@app.post("/api/characters/generate-traits")
def generate_traits(req: RandomizeTraitsRequest):
    diff = max(1, min(5, req.difficulty))
    traits = game.flush_character_traits(diff)
    return traits

@app.post("/api/characters")
def create_character(req: CreateCharacterRequest):
    diff = max(1, min(5, req.difficulty))
    if req.traits:
        traits = dict(req.traits)
    else:
        traits = game.flush_character_traits(diff)

    traits["name"] = req.name.strip()
    traits["status"] = req.side.lower()

    char_id = game.add_character(traits)
    character = game.character_table[char_id]

    try:
        inv_difficulty = 3 if diff not in [3] else diff
        character.inventory = game.flush_character_inventory(character, inv_difficulty)
    except Exception as e:
        print(f"Notice: flush_character_inventory fallback: {e}")
        try:
            starter = game.gen_item.item_table["CODA-9"]()
            character.inventory = [starter]
            character.equip_weapon(starter)
        except Exception:
            pass

    return serialize_character(character)

@app.put("/api/characters/{char_id}")
def update_character(char_id: int, req: UpdateCharacterRequest):
    if char_id not in game.character_table:
        raise HTTPException(status_code=404, detail="Character not found")

    data = req.dict(exclude_unset=True)

    if "side" in data and data["side"]:
        data["status"] = data["side"].lower()
        del data["side"]

    data["id"] = char_id
    game.set_character_state(data)

    if game_started and current_turn_character_id == char_id:
        if is_character_down(game.character_table[char_id]):
            advance_turn_if_game_active()

    return serialize_character(game.character_table[char_id])

@app.delete("/api/characters/{char_id}")
def delete_character(char_id: int):
    global current_turn_character_id
    if char_id not in game.character_table:
        raise HTTPException(status_code=404, detail="Character not found")

    del game.character_table[char_id]
    if char_id in game.round_table:
        game.round_table.remove(char_id)
    if current_turn_character_id == char_id:
        if game.round_table:
            current_turn_character_id = game.round_table[game.round_pointer % len(game.round_table)]
        else:
            current_turn_character_id = None

    return {"success": True, "deleted_id": char_id}

@app.post("/api/characters/{char_id}/randomize")
def randomize_character_traits(char_id: int, req: RandomizeTraitsRequest):
    if char_id not in game.character_table:
        raise HTTPException(status_code=404, detail="Character not found")

    character = game.character_table[char_id]
    diff = max(1, min(5, req.difficulty))
    new_traits = game.flush_character_traits(diff)
    new_traits["id"] = char_id
    new_traits["name"] = character.name
    new_traits["status"] = character.status

    game.set_character_state(new_traits)
    return serialize_character(character)

@app.post("/api/characters/{char_id}/inventory/randomize")
def randomize_character_inventory(char_id: int, req: RandomizeTraitsRequest):
    if char_id not in game.character_table:
        raise HTTPException(status_code=404, detail="Character not found")

    character = game.character_table[char_id]
    diff = max(1, min(5, req.difficulty))

    inv_diff = 3 if diff not in [3] else diff
    try:
        new_inv = game.flush_character_inventory(character, inv_diff)
        character.inventory = new_inv
    except Exception as e:
        print(f"Inventory randomize error: {e}")
        try:
            starter = game.gen_item.item_table["MXR-17"]()
            character.inventory = [starter]
            character.equip_weapon(starter)
        except Exception:
            pass

    return [serialize_item(item) for item in character.inventory]

@app.post("/api/characters/{char_id}/inventory/add")
def add_inventory_item(char_id: int, req: AddItemRequest):
    if char_id not in game.character_table:
        raise HTTPException(status_code=404, detail="Character not found")

    if req.item_name not in game.gen_item.item_table:
        raise HTTPException(status_code=400, detail=f"Unknown item {req.item_name}")

    game.add_item_to_character_inventory(char_id, req.item_name)
    character = game.character_table[char_id]
    return [serialize_item(item) for item in character.inventory]

@app.delete("/api/characters/{char_id}/inventory/{item_id}")
def delete_inventory_item(char_id: int, item_id: str):
    if char_id not in game.character_table:
        raise HTTPException(status_code=404, detail="Character not found")

    game.delete_item_from_character_inventory(char_id, item_id)
    character = game.character_table[char_id]
    return [serialize_item(item) for item in character.inventory]

def advance_turn_if_game_active() -> Optional[int]:
    global current_turn_character_id
    if not game_started or not game.round_table:
        return None

    available = [
        cid for cid in game.round_table
        if cid in game.character_table and not is_character_down(game.character_table[cid])
    ]
    if not available:
        current_turn_character_id = None
        return None

    try:
        active_char = game.next_turn()
    except Exception:
        active_char = game.character_table[available[0]]

    attempts = 0
    while is_character_down(active_char) and attempts < len(game.round_table):
        try:
            active_char = game.next_turn()
        except Exception:
            break
        attempts += 1

    if is_character_down(active_char):
        current_turn_character_id = available[0]
        if available[0] in game.round_table:
            game.round_pointer = (game.round_table.index(available[0]) + 1) % len(game.round_table)
    else:
        current_turn_character_id = active_char.id

    return current_turn_character_id

@app.post("/api/characters/{char_id}/inventory/{item_id}/reload")
def reload_weapon(char_id: int, item_id: str):
    char_key = char_id if char_id in game.character_table else int(char_id)
    if char_key not in game.character_table:
        raise HTTPException(status_code=404, detail="Character not found")

    character: Character = game.character_table[char_key]
    target_item = game.item_table[item_id]

    if not character.is_in_inventory(item_id):
        raise HTTPException(status_code=404, detail="Item not found in character inventory")

    if not isinstance(target_item, engine.items.Weapon):
        raise HTTPException(status_code=400, detail="Item is not a weapon")

    success = game.character_reload(char_key, item_id)
    if not success:
        return {
            "success": False,
            "message": f"Cannot reload {target_item.name}: Missing '{target_item.type} magazine' in inventory!",
            "magazine_bullets": target_item.magazine_bullets,
            "inventory": [serialize_item(item, held_id=getattr(character.held_weapon, "item_id", None)) for item in character.inventory],
        }

    if game_started:
        next_id = advance_turn_if_game_active()

    msg = f"Reloaded {target_item.name} to {target_item.magazine_size} bullets!"

    return {
        "success": True,
        "message": msg,
        "magazine_bullets": target_item.magazine_bullets,
        "current_turn_character_id": current_turn_character_id,
        "inventory": [serialize_item(item, held_id=getattr(character.held_weapon, "item_id", None)) for item in character.inventory],
    }

@app.post("/api/characters/{char_id}/inventory/{item_id}/equip")
def equip_weapon(char_id: int, item_id: str):
    char_key = char_id if char_id in game.character_table else int(char_id)
    if char_key not in game.character_table:
        raise HTTPException(status_code=404, detail="Character not found")

    character: Character = game.character_table[char_key]
    target_item = None
    for it in character.inventory:
        if getattr(it, "item_id", None) == item_id:
            target_item = it
            break

    if not target_item:
        raise HTTPException(status_code=404, detail="Item not found in character inventory")

    if not isinstance(target_item, engine.items.Weapon):
        raise HTTPException(status_code=400, detail="Item is not a weapon")

    game.item_table[item_id] = target_item
    game.character_equip_weapon(char_key, item_id)

    if game_started:
        next_id = advance_turn_if_game_active()

    msg = f"'{target_item.name}' equipped!"

    return {
        "success": True,
        "message": msg,
        "held_weapon_id": item_id,
        "current_turn_character_id": current_turn_character_id,
        "character": serialize_character(character),
        "inventory": [serialize_item(item, held_id=item_id) for item in character.inventory],
    }

@app.post("/api/game/start")
def start_game(req: StartGameRequest = None):
    global game_started, current_turn_character_id
    if not game.character_table:
        raise HTTPException(status_code=400, detail="Cannot start game with no characters")

    init_vals = {}
    if req and req.initiative_values:
        for k, v in req.initiative_values.items():
            try:
                init_vals[int(k)] = v
            except ValueError:
                init_vals[k] = v

    game.round_table = []
    try:
        game.start_game(init_vals)
    except IndexError:
        # Engine start_game has a known bounds check bug when the last sorted character is down
        game.round_pointer = 0

    game_started = True

    active_id = advance_turn_if_game_active()

    return {
        "success": True,
        "game_started": game_started,
        "current_turn_character_id": active_id,
        "round_table": game.round_table,
    }

@app.post("/api/game/next-turn")
def next_turn():
    global current_turn_character_id
    if not game_started or not game.round_table:
        raise HTTPException(status_code=400, detail="Game has not started or no characters")

    active_id = advance_turn_if_game_active()
    if active_id is None:
        return {
            "game_over": True,
            "message": "All characters are down!",
            "current_turn_character_id": None
        }

    return {
        "success": True,
        "current_turn_character_id": active_id,
        "round_pointer": game.round_pointer,
    }

@app.post("/api/game/stop")
def stop_game():
    global game_started, current_turn_character_id
    game_started = False
    current_turn_character_id = None
    game.round_table = []
    game.round_pointer = 0
    return {
        "success": True,
        "message": "Game stopped.",
        "game_started": False,
        "current_turn_character_id": None,
        "round_table": []
    }

@app.post("/api/characters/{char_id}/attack")
def character_attack_endpoint(char_id: int, req: AttackRequest):
    char_key = char_id if char_id in game.character_table else int(char_id)
    if char_key not in game.character_table:
        raise HTTPException(status_code=404, detail="Attacker character not found")

    target_key = req.target_id if req.target_id in game.character_table else int(req.target_id)
    if target_key not in game.character_table:
        raise HTTPException(status_code=404, detail="Target character not found")

    attacker = game.character_table[char_key]
    defender = game.character_table[target_key]

    if is_character_down(attacker):
        raise HTTPException(status_code=400, detail=f"'{attacker.name}' is down and cannot attack!")

    if game_started and current_turn_character_id is not None and char_key != current_turn_character_id:
        raise HTTPException(status_code=400, detail="It is not this character's turn to attack!")

    if attacker.held_weapon is None:
        for it in attacker.inventory:
            if isinstance(it, engine.items.Weapon):
                attacker.equip_weapon(it)
                game.item_table[it.item_id] = it
                break

    if attacker.held_weapon is None:
        raise HTTPException(status_code=400, detail=f"'{attacker.name}' has no weapon to attack with!")

    if attacker.held_weapon.magazine_bullets is not None and attacker.held_weapon.magazine_bullets <= 0:
        return {
            "success": False,
            "hit": False,
            "damage_dealt": 0,
            "message": f"Cannot attack: '{attacker.held_weapon.name}' is out of ammo!",
            "attacker": serialize_character(attacker),
            "target": serialize_character(defender),
            "current_turn_character_id": current_turn_character_id
        }

    initial_defender_health = defender.health

    hit = game.character_attack(char_key, target_key, req.bodypart)

    damage_dealt = max(0, initial_defender_health - defender.health)

    if hit and damage_dealt > 0:
        msg = f"Attack hit {defender.name}'s {req.bodypart}! Dealt {damage_dealt} damage."
        if defender.health <= 0:
            msg += f" {defender.name} is down!"
    elif hit:
        msg = f"Attack hit {defender.name}'s {req.bodypart}, but didn't pierce cover"
    else:
        msg = f"Attack from {attacker.name} missed {defender.name}."

    if game_started:
        next_id = advance_turn_if_game_active()

    return {
        "success": True,
        "hit": hit,
        "damage_dealt": damage_dealt,
        "message": msg,
        "current_turn_character_id": current_turn_character_id,
        "attacker": serialize_character(attacker),
        "target": serialize_character(defender)
    }

@app.post("/api/game/save")
def save_game():
    try:
        game.save()
        return {"success": True, "message": "Game state successfully saved to database."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database save error: {str(e)}")
