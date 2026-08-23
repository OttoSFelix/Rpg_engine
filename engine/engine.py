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


class Dice:
    def throw(self, dice: str):
        amount, sides = dice.split('d')
        result = []
        for d in range(amount):
            n = random.randint(1, sides)
            result.append(n)
        return result


if __name__ == '__main__':
    db = Database()
    db.init_database()
    db.test_database()