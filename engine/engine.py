from engine.character import Character
from engine.items import Item
import psycopg2
import os
import random

class Database:
    def __init__(self):
        self.user = os.environ.get('USER')
        self.password = os.environ.get('PASSWORD')
        print(f'user: {self.user}')
        print(f'password: {self.password}')
        
        self.conn = psycopg2.connect(
            dbname='appdb',
            user=self.user,
            password=self.password,
            host=os.environ.get('DB_HOST'),
            port=os.environ.get('DB_PORT')
        )

        self.cursor = self.conn.cursor()

    def init_database(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS characters (
            id SERIAL PRIMARY KEY,
            name VARCHAR(50),
            strength INTEGER,
            dexterity INTEGER,
            toughness INTEGER,
            perseverance INTEGER,
            brilliance INTEGER,
            senses INTEGER,
            presence INTEGER,
            sharpstrike INTEGER,
            ravage INTEGER,
            melee INTEGER,
            special INTEGER,
            stealth INTEGER,
            hardware INTEGER,
            ordnance INTEGER,
            medical INTEGER,
            health INTEGER,
            head INTEGER,
            torso INTEGER,
            right_arm INTEGER,
            left_arm INTEGER,
            right_leg INTEGER,
            left_leg INTEGER,
            mental INTEGER,
            movement_stat INTEGER,
            stamina INTEGER,
            cover INTEGER,
            status VARCHAR(50)
        );
        """)
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS items (
        item_id VARCHAR(16) UNIQUE,
        character_id INTEGER REFERENCES characters(id),
        name VARCHAR(50),
        weight INTEGER
        );
        """)
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS injuries (
        character_id INTEGER REFERENCES characters(id),
        head VARCHAR(50),
        torso VARCHAR(50),
        right_arm VARCHAR(50),
        left_arm VARCHAR(50),
        right_leg VARCHAR(50),
        left_leg VARCHAR(50)
        );
        """)
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS talents (
        character_id INTEGER REFERENCES characters(id),
        talent VARCHAR(50)
        );
        """)

        self.conn.commit()

    def test_database(self):
        self.cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_type = 'BASE TABLE';
        """)
        print(self.cursor.fetchall())

    def get_characters(self):
        query = """
        SELECT * FROM characters;
        """
        self.cursor.execute(query)

        results = self.cursor.fetchall()
        return results

    def get_items(self):
        query = """
        SELECT * FROM items;
        """
        self.cursor.execute(query)

        results = self.cursor.fetchall()
        return results



class Dice:
    def throw(self, dice: str):
        amount, sides = dice.split('d')
        result = []
        for d in range(int(amount)):
            n = random.randint(1, int(sides))
            result.append(n)
        return result


class Game:
    def __init__(self):
        self.round_table = []
        self.character_table = {}
        self.item_table = {}
        self.db = Database()

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
                cover=character[27]
            )

        gen_item = Item()
        for item in self.db.get_items():
            id = item[0]
            self.item_table[id] = gen_item.item_table[item[2]]


if __name__ == '__main__':
    d = Dice()
    print(d.throw('3d12'))
    # db = Database()
    # db.init_database()
    # db.test_database()