import os
import psycopg2

class Database:
    def __init__(self):
        self.user = os.environ.get('USER')
        self.password = os.environ.get('PASSWORD')
        
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
            full_cover INTEGER,
            head_cover INTEGER,
            torso_cover INTEGER,
            right_arm_cover INTEGER,
            left_arm_cover INTEGER,
            right_leg_cover INTEGER,
            left_leg_cover INTEGER,
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

    def purge_database(self):
        self.cursor.execute("""
        DROP TABLE IF EXISTS characters, items, injuries, talents CASCADE
        """)
        self.conn.commit()

    def reset_database(self):
        self.cursor.execute("TRUNCATE TABLE characters, items, injuries, talents RESTART IDENTITY CASCADE")
        self.conn.commit()

    def test_database(self):
        self.cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_type = 'BASE TABLE';
        """)
        self.conn.commit()
        print(self.cursor.fetchall())

    def get_characters(self):
        query = """
        SELECT * FROM characters;
        """
        self.cursor.execute(query)

        results = self.cursor.fetchall()
        self.conn.commit()
        return results

    def get_items(self):
        query = """
        SELECT * FROM items;
        """
        self.cursor.execute(query)

        results = self.cursor.fetchall()
        self.conn.commit()
        return results

    def get_injuries(self):
        self.cursor.execute('SELECT * FROM injuries')
        results = self.cursor.fetchall()
        self.conn.commit()

        return results

    def save_character(self, values):
        query = """
            INSERT INTO characters (
                name,
                strength,
                dexterity,
                toughness,
                perseverance,
                brilliance,
                senses,
                presence,
                sharpstrike,
                ravage,
                melee,
                special,
                stealth,
                hardware,
                ordnance,
                medical,
                health,
                head,
                torso,
                right_arm,
                left_arm,
                right_leg,
                left_leg,
                mental,
                movement_stat,
                stamina,
                full_cover,
                head_cover,
                torso_cover,
                right_arm_cover,
                left_arm_cover,
                right_leg_cover,
                left_leg_cover,
                status
                )
            VALUES (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )
            """

        self.cursor.execute(query, (
            values['name'],
            values['strength'],
            values['dexterity'],
            values['toughness'],
            values['perseverance'],
            values['brilliance'],
            values['senses'],
            values['presence'],
            values['sharpstrike'],
            values['ravage'],
            values['melee'],
            values['special'],
            values['stealth'],
            values['hardware'],
            values['ordnance'],
            values['medical'],
            values['health'],
            values['head'],
            values['torso'],
            values['right_arm'],
            values['left_arm'],
            values['right_leg'],
            values['left_leg'],
            values['mental'],
            values['movement_stat'],
            values['stamina'],
            values['full_cover'],
            values['head_cover'],
            values['torso_cover'],
            values['right_arm_cover'],
            values['left_arm_cover'],
            values['right_leg_cover'],
            values['left_leg_cover'],
            values['status'],
        ))
        self.conn.commit()

    def save_item(self, values):
        query = """
        INSERT INTO items (
            item_id,
            character_id,
            name,
            weight
        )
        VALUES (
            %s,
            %s,
            %s,
            %s
        )
        """

        self.cursor.execute(query, (values['item_id'], values['character_id'], values['name'], values['weight']))
        self.conn.commit()

    def save_injuries(self, values):
        query = """
        INSERT INTO injuries (
            character_id,
            head,
            torso,
            right_arm,
            left_arm,
            right_leg,
            left_leg
        )
        VALUES (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        )
        """

        self.cursor.execute(query, (values['character_id'], values['head'], values['torso'], values['right_arm'], values['left_arm'], values['right_leg'], values['left_leg']))
        self.conn.commit()

    def clear_characters(self):
        self.cursor.execute("TRUNCATE TABLE characters RESTART IDENTITY CASCADE")
        self.conn.commit()

    def clear_items(self):
        self.cursor.execute("TRUNCATE TABLE items RESTART IDENTITY")
        self.conn.commit()

