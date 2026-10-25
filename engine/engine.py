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
        self.inventory_table = {}
        self.db = Database()
        self.generator = Generator()
        self.character_count = 0

    def initialize(self):
        self.db.init_database()

        for character in self.db.get_characters():
            self.character_count += 1
            id = character[0]
            self.character_table[id] = Character(
                id,
                name=character[1],
                strength=character[2],
                dexterity=character[3],
                toughness=character[4],
                perseverance=character[5],
                brilliance=character[6],
                senses=character[7],
                presence=character[8],
                sharpstrike=character[9],
                ravage=character[10],
                melee=character[11],
                special=character[12],
                stealth=character[13],
                hardware=character[14],
                ordnance=character[15],
                medical=character[16],
                health=character[17],
                head=character[18],
                torso=character[19],
                right_arm=character[20],
                left_arm=character[21],
                right_leg=character[22],
                left_leg=character[23],
                mental=character[24],
                movement_stat=character[25],
                stamina=character[26],
                full_cover=character[27],
                head_cover=character[28],
                torso_cover=character[29],
                right_arm_cover=character[30],
                left_arm_cover=character[31],
                right_leg_cover=character[32],
                left_leg_cover=character[33],
                status=character[34]
            )

        gen_item = Item()
        for item in self.db.get_items():
            id = item[0]
            self.item_table[id] = gen_item.item_table[item[2]]
            if self.inventory_table.get(item[1], None) == None:
                self.inventory_table[item[1]] = []
            self.inventory_table[item[1]].append(id)

    def add_character(self, values: dict):
        id = self.character_count + 1
        self.character_count += 1
        character = Character(
            id=id,
            name=values['name'],
            strength=values['strength'],
            dexterity=values['dexterity'],
            toughness=values['toughness'],
            perseverance=values['perseverance'],
            brilliance=values['brilliance'],
            senses=values['senses'],
            presence=values['presence'],
            sharpstrike=values['sharpstrike'],
            ravage=values['ravage'],
            melee=values['melee'],
            special=values['special'],
            stealth=values['stealth'],
            hardware=values['hardware'],
            ordnance=values['ordnance'],
            medical=values['medical'],
            health=5,
            head=1,
            torso=3,
            right_arm=2,
            left_arm=2,
            right_leg=2,
            left_leg=2,
            mental=0,
            movement_stat=0,
            stamina=values['dexterity'],
            full_cover=0,
            head_cover=0,
            torso_cover=0,
            right_arm_cover=0,
            left_arm_cover=0,
            right_leg_cover=0,
            left_leg_cover=0,
            status='None',
        )
        self.character_table[id] = character
        self.inventory_table[id] = []

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

        for character_id, item_list in self.inventory_table.items():
            for item in item_list:
                values = {}
                values['item_id'] = item.item_id
                values['character_id'] = character_id
                values['name'] = item.name
                values['weight'] = item.weight
                self.db.save_item(values)






if __name__ == '__main__':
    game = Game()
    gen = Generator()
    