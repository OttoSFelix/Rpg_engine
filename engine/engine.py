from character import Character
from items import Item
from generator import Generator
from database import Database


class Game:
    def __init__(self):
        self.round_table = []
        self.character_table = {}
        self.item_table = {}
        self.db = Database()
        self.generator = Generator()

    def initialize(self):
        self.db.init_database()

        for character in self.db.get_characters():
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
                cover=character[27],
                status=character[28]
            )

        gen_item = Item()
        for item in self.db.get_items():
            id = item[0]
            self.item_table[id] = gen_item.item_table[item[2]]

    def add_character(self, values: dict):
        id = len(self.db.get_characters()) + 1
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
            cover=0,
            status='None',
        )
        self.character_table[id] = character

    def flush_character_values(self, difficulty):
        values = self.generator.generate_character_traits()
        for trait, value in values.items():
            values[trait] += (-3 + difficulty)
        return values
        



if __name__ == '__main__':
    db = Database()
    db.init_database()
    db.test_database()