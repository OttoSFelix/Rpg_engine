import json
import urllib.request
import urllib.error

BASE_URL = "http://127.0.0.1:3000"

def request(method, path, body=None):
    url = f"{BASE_URL}{path}"
    data = json.dumps(body).encode('utf-8') if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    if body is not None:
        req.add_header('Content-Type', 'application/json')
    with urllib.request.urlopen(req) as resp:
        content = resp.read().decode('utf-8')
        return json.loads(content) if content else {}

def test_api():
    print("Testing API via Vite dev server proxy at http://127.0.0.1:3000...")

    # 1. Health check
    res = request("GET", "/api/health")
    assert res.get("status") == "ok", f"Health check failed: {res}"
    print("✓ Health check OK")

    # 2. Get state
    state = request("GET", "/api/game/state")
    assert "characters" in state
    assert "item_pool" in state
    print(f"✓ Game state OK: {len(state['characters'])} characters, {len(state['item_pool'])} items in pool")

    # 3. Create player
    player = request("POST", "/api/characters", {
        "name": "Commander Shepard",
        "side": "player",
        "difficulty": 3
    })
    pid = player["id"]
    assert player["name"] == "Commander Shepard"
    assert player["side"] == "player"
    print(f"✓ Create player OK: ID {pid}")

    # 4. Create enemy
    enemy = request("POST", "/api/characters", {
        "name": "Marauder Shield",
        "side": "enemy",
        "difficulty": 3
    })
    eid = enemy["id"]
    assert enemy["name"] == "Marauder Shield"
    assert enemy["side"] == "enemy"
    print(f"✓ Create enemy OK: ID {eid}")

    # 5. Inline edit traits
    updated = request("PUT", f"/api/characters/{pid}", {
        "strength": 9,
        "health": 3
    })
    assert updated["strength"] == 9
    assert updated["health"] == 3
    print("✓ Update character traits OK")

    # 6. Randomize character traits
    rand_char = request("POST", f"/api/characters/{pid}/randomize", {"difficulty": 4})
    assert rand_char["id"] == pid
    print("✓ Randomize traits OK")

    # 7. Add item to inventory
    inv = request("POST", f"/api/characters/{pid}/inventory/add", {"item_name": "sharpstrike magazine"})
    mag_item = next((it for it in inv if it["name"] == "sharpstrike magazine"), None)
    assert mag_item is not None
    print("✓ Add item to inventory OK")

    # 8. Reload weapon
    weapon_item = next((it for it in inv if it["is_weapon"]), None)
    if weapon_item:
        reload_res = request("POST", f"/api/characters/{pid}/inventory/{weapon_item['item_id']}/reload")
        print(f"✓ Reload weapon OK: {reload_res.get('message')}")

    # 9. Randomize inventory
    rand_inv = request("POST", f"/api/characters/{pid}/inventory/randomize", {"difficulty": 3})
    assert isinstance(rand_inv, list)
    print("✓ Randomize inventory OK")

    # 10. Delete item from inventory
    if len(rand_inv) > 0:
        to_del = rand_inv[0]["item_id"]
        after_del = request("DELETE", f"/api/characters/{pid}/inventory/{to_del}")
        assert isinstance(after_del, list)
        print("✓ Delete item OK")

    # 11. Start game and take turn
    start_info = request("POST", "/api/game/start")
    assert start_info["game_started"] is True
    print(f"✓ Start game OK: Turn is character {start_info['current_turn_character_id']}")

    turn_info = request("POST", "/api/game/next-turn")
    print(f"✓ Next turn OK: Current turn character {turn_info.get('current_turn_character_id')}")

    # 12. Save game
    save_res = request("POST", "/api/game/save")
    assert save_res.get("success") is True
    print(f"✓ Save game OK: {save_res.get('message')}")

    print("\nALL API TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_api()
