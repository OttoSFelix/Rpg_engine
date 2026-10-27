from engine.character import Character
from engine.items import Item
from engine.generator import Generator
from engine.database import Database
from time import sleep


class Game:
    def __init__(self):
        self.round_table = []
        self.character_table = {}
        self.item_table = {}
        self.db = Database()
        self.generator = Generator()
        self.character_count = 0

    def initialize(self):
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

        gen_item = Item()
        for item in self.db.get_items():
            item_object = gen_item.load_item(item[2], item[0])
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

    def add_character(self, values: dict):
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
            stamina=values['dexterity'],
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

        return id

    def flush_character_values(self, difficulty):
        values = self.generator.generate_character_traits()
        for trait, value in values.items():
            values[trait] += (-3 + difficulty)
        return values
        
    def save(self):
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
    