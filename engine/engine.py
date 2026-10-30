from engine.character import Character
from engine.items import ItemPool, Weapon
from engine.generator import Generator
from engine.database import Database
from engine.dice import Dice

DICE = Dice()

class Game:
    def __init__(self):
        self.round_table = []
        self.round_pointer = 0
        self.character_table = {}
        self.item_table = {}
        self.db = Database()
        self.generator = Generator()
        self.character_count = 0
        self.gen_item = ItemPool()

    def initialize(self) -> None:
        self.db.init_database()

        for character in self.db.get_characters():
            self.character_count += 1
            id = character[0]
            values = {
                'id': id,
                'name': character[1],
                'strength': character[2],
                'dexterity': character[3],
                'toughness': character[4],
                'perseverance': character[5],
                'brilliance': character[6],
                'senses': character[7],
                'presence': character[8],
                'sharpstrike': character[9],
                'ravage': character[10],
                'melee': character[11],
                'special': character[12],
                'stealth': character[13],
                'hardware': character[14],
                'ordnance': character[15],
                'medical': character[16],
                'health': character[17],
                'head': character[18],
                'torso': character[19],
                'right_arm': character[20],
                'left_arm': character[21],
                'right_leg': character[22],
                'left_leg': character[23],
                'mental': character[24],
                'movement_stat': character[25],
                'stamina': character[26],
                'full_cover': character[27],
                'head_cover': character[28],
                'torso_cover': character[29],
                'right_arm_cover': character[30],
                'left_arm_cover': character[31],
                'right_leg_cover': character[32],
                'left_leg_cover': character[33],
                'status': character[34]
            }

            self.add_character(values)

        for item in self.db.get_items():
            item_object = self.gen_item.load_item(item[2], item[0])
            self.item_table[item[0]] = item_object
            character_id = item[1]
            self.character_table[character_id].inventory.append(item_object)

        for injury in self.db.get_injuries():
            character_id = injury[0]
            self.character_table[character_id].injury['head'] = injury[1]
            self.character_table[character_id].injury['torso'] = injury[2]
            self.character_table[character_id].injury['right_arm'] = injury[3]
            self.character_table[character_id].injury['left_arm'] = injury[4]
            self.character_table[character_id].injury['right_leg'] = injury[5]
            self.character_table[character_id].injury['left_leg'] = injury[6]

    def add_character(self, values: dict) -> int:
        if values.get('id', None) != None:
            id = values['id']
        else:
            id = self.character_count + 1
            self.character_count += 1
        character = Character(
            id=id,
            name=values['name'],
            strength=values.get('strength', 5),
            dexterity=values.get('dexterity', 5),
            toughness=values.get('toughness', 5),
            perseverance=values.get('perseverance', 5),
            brilliance=values.get('brilliance', 5),
            senses=values.get('senses', 5),
            presence=values.get('presence', 5),
            sharpstrike=values.get('sharpstrike', 0),
            ravage=values.get('ravage', 0),
            melee=values.get('melee', 0),
            special=values.get('special', 0),
            stealth=values.get('stealth', 0),
            hardware=values.get('hardware', 0),
            ordnance=values.get('ordnance', 0),
            medical=values.get('medical', 0),
            health=values.get('health', 5),
            head=values.get('head', 1),
            torso=values.get('torso', 3),
            right_arm=values.get('right_arm', 2),
            left_arm=values.get('left_arm', 2),
            right_leg=values.get('right_leg', 2),
            left_leg=values.get('left_leg', 2),
            mental=values.get('mental', 0),
            movement_stat=values.get('movement_stat', 0),
            stamina=values.get('dexterity', 5),
            full_cover=values.get('full_cover', 0),
            head_cover=values.get('head_cover', 0),
            torso_cover=values.get('torso_cover', 0),
            right_arm_cover=values.get('right_arm_cover', 0),
            left_arm_cover=values.get('left_arm_cover', 0),
            right_leg_cover=values.get('right_leg_cover', 0),
            left_leg_cover=values.get('left_leg_cover', 0),
            status=values.get('status', 'None'),
        )
        self.character_table[id] = character

        self.character_inventory = values.get('inventory', [])

        self.round_table.append(character.id)

        return id

    def flush_character_traits(self, difficulty: int = 3) -> dict:
        values = self.generator.generate_character_traits(difficulty)

        return values

    def flush_character_inventory(self, character: Character, difficulty: int = 3) -> list:
        inventory = self.generator.generate_inventory_items(character, difficulty)

        return inventory

    def add_item_to_character_inventory(self, character_id: int, item_name: str) -> None:
        character: Character = self.character_table[character_id]
        item = self.gen_item.item_table[item_name]()
        character.add_item(item)

    def delete_item_from_character_inventory(self, character_id: str, item_id: str) -> None:
        character: Character = self.character_table[character_id]
        character.delete_item(item_id)

    def character_reload(self, character_id: str, item_id: str) -> bool:
        character: Character = self.character_table[character_id]
        item: Weapon = self.item_table.get(item_id)
        if item == None:
            return False
        return item.reload(character)

    def character_attack(self, character_id: int, target_id: int, bodypart: str) -> bool:
        character: Character = self.character_table[character_id]
        target: Character = self.character_table[target_id]

        return character.attack(target, bodypart)

    def character_equip_weapon(self, character_id: int, item_id: str) -> bool:
        character: Character = self.character_table[character_id]
        weapon: Weapon = self.item_table.get(item_id)
        if weapon == None:
            return False
        character.equip_weapon(weapon)
        return True

    def start_game(self, initiative_values) -> None:
        self.initiative_values = initiative_values
        for character_id in self.character_table.keys():
            self.round_table.append(character_id)

        self.round_table.sort(key=self.key_initiative_sort)
        self.round_pointer = 0
        while self.character_table[self.round_table[self.round_pointer]].is_down():
            if self.round_pointer >= len(self.round_table):
                return
            self.round_pointer += 1

    def next_turn(self) -> Character:
        while True:
            character_id = self.round_table[self.round_pointer]
            character: Character = self.character_table[character_id]

            if self.round_pointer >= len(self.round_table) - 1:
                self.round_pointer = 0
            else:
                self.round_pointer += 1

            if not character.is_down():
                break

        return character

    def end_turn(self, character_id: str) -> None:
        character = self.character_table[character_id]
        while True:
            pointer = 0
            for effect in character.effects:
                if effect[1] == 0:
                    character.effects.pop(pointer)
                    break
                pointer += 1
            break

        for effect in character.effects:
            effect[1] -= 1

    def return_game_state(self) -> dict:
        game_state = {}

        for character in self.character_table.values():
            game_state[character.id] = {
                'health': character.health,
                'head': character.head,
                'torso': character.torso,
                'right_arm': character.right_arm,
                'left_arm': character.left_arm,
                'right_leg': character.right_leg,
                'left_leg': character.left_leg,
                'head_cover': character.head_cover,
                'torso_cover': character.torso_cover,
                'right_arm_cover': character.right_arm_cover,
                'left_arm_cover': character.left_arm_cover,
                'right_leg_cover': character.right_leg_cover,
                'left_leg_cover': character.left_leg_cover,
                'inventory': character.inventory,
                'injuries': character.injury,
                'effects': character.effects,
                'mental': character.mental,
                'stamina': character.stamina,
            }

        return game_state

    def set_character_state(self, values) -> None:
        character = self.character_table[values['id']]

        character.name = values.get('name', character.name)
        character.health = values.get('health', character.health)
        character.head = values.get('head', character.head)
        character.torso = values.get('torso', character.torso)
        character.right_arm = values.get('right_arm', character.right_arm)
        character.left_arm = values.get('left_arm', character.left_arm)
        character.right_leg = values.get('right_leg', character.right_leg)
        character.left_leg = values.get('left_leg', character.left_leg)
        character.head_cover = values.get('head_cover', character.head_cover)
        character.torso_cover = values.get('torso_cover', character.torso_cover)
        character.right_arm_cover = values.get('right_arm_cover', character.right_arm_cover)
        character.left_arm_cover = values.get('left_arm_cover', character.left_arm_cover)
        character.right_leg_cover = values.get('right_leg_cover', character.right_leg_cover)
        character.left_leg_cover = values.get('left_leg_cover', character.left_leg_cover)
        character.inventory = values.get('inventory', character.inventory)
        character.injury = values.get('injury', character.injury)
        character.effects = values.get('effects', character.effects)
        character.strength = values.get('strength', character.strength)
        character.dexterity = values.get('dexterity', character.dexterity)
        character.toughness = values.get('toughness', character.toughness)
        character.perseverance = values.get('perseverance', character.perseverance)
        character.brilliance = values.get('brilliance', character.brilliance)
        character.senses = values.get('senses', character.senses)
        character.presence = values.get('presence', character.presence)
        character.sharpstrike = values.get('sharpstrike', character.sharpstrike)
        character.ravage = values.get('ravage', character.ravage)
        character.melee = values.get('melee', character.melee)
        character.special = values.get('special', character.special)
        character.stealth = values.get('stealth', character.stealth)
        character.hardware = values.get('hardware', character.hardware)
        character.ordnance = values.get('ordnance', character.ordnance)
        character.medical = values.get('medical', character.medical)
        character.health = values.get('health', character.health)
        character.head = values.get('head', character.head)
        character.torso = values.get('torso', character.torso)
        character.right_arm = values.get('right_arm', character.right_arm)
        character.left_arm = values.get('left_arm', character.left_arm)
        character.right_leg = values.get('right_leg', character.right_leg)
        character.left_leg = values.get('left_leg', character.left_leg)
        character.mental = values.get('mental', character.mental)
        character.movement_stat = values.get('movement_stat', character.movement_stat)
        character.stamina = values.get('stamina', character.stamina)
        character.full_cover = values.get('full_cover', character.full_cover)
        character.head_cover = values.get('head_cover', character.head_cover)
        character.torso_cover = values.get('torso_cover', character.torso_cover)
        character.right_arm_cover = values.get('right_arm_cover', character.right_arm_cover)
        character.left_arm_cover = values.get('left_arm_cover', character.left_arm_cover)
        character.right_leg_cover = values.get('right_leg_cover', character.right_leg_cover)
        character.left_leg_cover = values.get('left_leg_cover', character.left_leg_cover)
        character.status = values.get('status', character.status)

    def key_initiative_sort(self, id):
        character: Character = self.character_table[id]

        result = DICE.throw('1d12')[0] + character.stat_modifier(character.dexterity) + character.stat_modifier(character.senses)

        return self.initiative_values.get(id, result)

    def save(self) -> None:
        self.db.clear_items()
        self.db.clear_characters()

        for id, character in self.character_table.items():
            values = character.get_character_attributes()
            values['id'] = id
            self.db.save_character(values)

            for item in character.inventory:
                item_values = {}
                item_values['item_id'] = item.item_id
                item_values['character_id'] = id
                item_values['name'] = item.name
                item_values['weight'] = item.weight
                self.db.save_item(item_values)

            injury_values = {}
            injury_values['character_id'] = id
            injury_values['head'] = character.injury['head']
            injury_values['torso'] = character.injury['torso']
            injury_values['right_arm'] = character.injury['right_arm']
            injury_values['left_arm'] = character.injury['left_arm']
            injury_values['right_leg'] = character.injury['right_leg']
            injury_values['left_leg'] = character.injury['left_leg']

            self.db.save_injuries(injury_values)









if __name__ == '__main__':
    game = Game()
    gen = Generator()
    game.db.reset_database()

    values = game.flush_character_traits()
    values['name'] = 'Jackson'

    id = game.add_character(values)
    character: Character = game.character_table[id]

    character.inventory = game.flush_character_inventory(character)

    print(character)
    print('stats:')
    for stat, value in character.get_character_attributes().items():
        print(f'{stat}: {value}')
    print()
    print('inventory:')
    for item in character.inventory:
        print(item)
    print(f'inventory weight: {character.get_inventory_weight()}')