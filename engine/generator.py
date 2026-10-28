import random
from engine.items import Item
from engine.dice import Dice
DICE = Dice()
class Generator:
    def __init__(self):

        self.weapon_choise_table = {1: [], 2: [], 3: ["MXR-17", "SP-R 208", "CODA-9"], 4: [], 5: []}
        self.tool_choise_table = {1: [], 2: [], 3: ['lockpick'], 4: [], 5: []}
        self.utility_choise_table = {1: [], 2: [], 3: ['C4', 'flash', 'Hyposhot Injector', 'Hyposhot A', 'Hyposhot Z'], 4: [], 5: []}
        self.item_gen = Item()

    def generate_character_traits(self, difficulty: int = 3) -> dict:
        personal_traits = [
            "strength",
            "dexterity",
            "toughness",
            "perseverance",
            "brilliance",
            "senses",
            "presence",
        ]

        skills = [
            "sharpstrike",
            "ravage",
            "melee",
            "special",
            "stealth",
            "hardware",
            "ordnance",
            "medical"
        ]

        values = {}

        throws = DICE.throw(f'{len(personal_traits)}d10')
        for trait, throw in zip(personal_traits, throws):
            if throw < 5:
                throw += 3
            elif throw > 5:
                throw -= 3
            values[trait] = throw + (-3 + difficulty)
        
        for skill in skills:
            values[skill] = 0

        for _ in range((difficulty * 3) - 6):
            random_skill = random.choice(skills)
            values[random_skill] = min(4, values[random_skill] + 1)

        return values

    def generate_inventory_items(self, character, difficulty: int = 3) -> list:
        inventory = []
        capacity = character.strength * 10
        weapon = self.item_gen.item_table[random.choice(self.weapon_choise_table[difficulty])]()
        capacity -= weapon.weight
        inventory.append(weapon)
        character.equip_weapon(weapon)



        if difficulty >= 3:
            tool_pool = self.tool_choise_table[difficulty][:]
            random.shuffle(tool_pool)
            for tool_name in tool_pool:
                tool = self.item_gen.item_table[tool_name]()
                if capacity - tool.weight > 0:
                    inventory.append(tool)
                    break

        random_capacity_floor = random.randint(5, 30)

        utility_pool = self.utility_choise_table[difficulty][:]
        utility_pool.remove('Hyposhot Injector')
        injector_owned = False

        while capacity > random_capacity_floor:
            random_utility_name = random.choice(utility_pool)

            if 'Hyposhot' in random_utility_name:
                if not injector_owned:
                    injector = self.item_gen.item_table['Hyposhot Injector']()
                    stim = self.item_gen.item_table[random_utility_name]()
                    if capacity - injector.weight - stim.weight > 0:
                        inventory.append(injector)
                        inventory.append(stim)
                        injector_owned = True
                        capacity -= injector.weight
                        capacity -= stim.weight
                    continue
                else:
                    stim = self.item_gen.item_table[random_utility_name]()
                    if capacity - stim.weight > 0:
                        inventory.append(stim)
                        capacity -= stim.weight
                    continue
            
            random_utility = self.item_gen.item_table[random_utility_name]()

            if capacity - random_utility.weight > 0:
                inventory.append(random_utility)
                capacity -= random_utility.weight

        return inventory

