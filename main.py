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

def serialize_item(item: Any) -> Dict[str, Any]:
    is_weapon = isinstance(item, engine.items.Weapon)
    data = {
        "item_id": getattr(item, "item_id", ""),
        "name": getattr(item, "name", ""),
        "weight": getattr(item, "weight", 0),
        "is_weapon": is_weapon,
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
    return {
        "id": c.id,
        "name": c.name,
        "side": side,
        "status": c.status,
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
        "inventory": [serialize_item(item) for item in c.inventory],
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


@app.get("/api/health")
def health_check():
    return {"status": "ok", "game_started": game_started}

@app.get("/api/items/pool")
def get_items_pool():
    return get_item_pool_list()

@app.get("/api/game/state")
def get_game_state():
    global current_turn_character_id
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

@app.post("/api/characters/{char_id}/inventory/{item_id}/reload")
def reload_weapon(char_id: int, item_id: str):
    if char_id not in game.character_table:
        raise HTTPException(status_code=404, detail="Character not found")

    character: Character = game.character_table[char_id]
    target_item = game.item_table[item_id]

    if not isinstance(target_item, engine.items.Weapon):
        raise HTTPException(status_code=400, detail="Item is not a weapon")

    success = game.character_reload(char_id, item_id)
    if not success:
        return {
            "success": False,
            "message": f"Cannot reload {target_item.name}: Missing '{target_item.type} magazine' in inventory!",
            "magazine_bullets": target_item.magazine_bullets,
            "inventory": [serialize_item(item) for item in character.inventory],
        }

    return {
        "success": True,
        "message": f"Successfully reloaded {target_item.name} to {target_item.magazine_size} bullets!",
        "magazine_bullets": target_item.magazine_bullets,
        "inventory": [serialize_item(item) for item in character.inventory],
    }

@app.post("/api/game/start")
def start_game(req: StartGameRequest = None):
    global game_started, current_turn_character_id
    if not game.character_table:
        raise HTTPException(status_code=400, detail="Cannot start game with no characters")

    init_vals = (req.initiative_values if req else None) or {}
    game.round_table = []
    game.start_game(init_vals)
    game_started = True

    if game.round_table:
        current_turn_character_id = game.round_table[game.round_pointer]
    else:
        current_turn_character_id = None

    return {
        "success": True,
        "game_started": game_started,
        "current_turn_character_id": current_turn_character_id,
        "round_table": game.round_table,
    }

@app.post("/api/game/next-turn")
def next_turn():
    global current_turn_character_id
    if not game_started or not game.round_table:
        raise HTTPException(status_code=400, detail="Game has not started or no characters")

    alive = [cid for cid in game.round_table if game.character_table[cid].health > 0]
    if not alive:
        return {
            "game_over": True,
            "message": "All characters are dead!",
            "current_turn_character_id": None
        }

    active_char = game.next_turn()
    current_turn_character_id = active_char.id
    return {
        "success": True,
        "current_turn_character_id": current_turn_character_id,
        "round_pointer": game.round_pointer,
    }

@app.post("/api/game/save")
def save_game():
    try:
        game.save()
        return {"success": True, "message": "Game state successfully saved to database."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database save error: {str(e)}")
