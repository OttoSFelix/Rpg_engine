import unittest
from engine.engine import Game
from tests._base_unittest import DatabaseTestcase

class TestCharacter(DatabaseTestcase):
    def test_character_in_database(self):
        self.db.cursor.execute("INSERT INTO characters(id, name) VALUES(1, 'Jack');")
        
        self.db.cursor.execute("SELECT * FROM characters;")
        results = self.db.cursor.fetchall()
        
        self.assertEqual(len(results), 1)

    def test_character_correct_value(self):
        self.db.cursor.execute("INSERT INTO characters(id, name, strength, dexterity, toughness) VALUES(2, 'Morris', 5, 8, 2)")
        
        self.db.cursor.execute("SELECT id, name, strength, dexterity, toughness FROM characters;")
        results = self.db.cursor.fetchall()
        correct = [(2, 'Morris', 5, 8, 2)]

        self.assertEqual(correct, results)

    def test_character_in_table(self):
        game = Game()
        values = {
            'name': 'testcharacter',
            'strength': 4,
            'dexterity': 5,
            'toughness': 1,
            'perseverance': 9,
            'brilliance': 10,
            'senses': 5,
            'presence': 7,
            'sharpstrike': 1,
            'ravage': 2,
            'melee': 3,
            'special': 4,
            'stealth': 6,
            'hardware': 5,
            'ordnance': 3,
            'medical': 4
        }
        id = game.add_character(values)

        correct = [
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
            5,
            1,
            3,
            2,
            2,
            2,
            2,
            0,
            0,
            values['dexterity']
        ]

        result = [
            game.character_table[id].name,
            game.character_table[id].strength,
            game.character_table[id].dexterity,
            game.character_table[id].toughness,
            game.character_table[id].perseverance,
            game.character_table[id].brilliance,
            game.character_table[id].senses,
            game.character_table[id].presence,
            game.character_table[id].sharpstrike,
            game.character_table[id].ravage,
            game.character_table[id].melee,
            game.character_table[id].special,
            game.character_table[id].stealth,
            game.character_table[id].hardware,
            game.character_table[id].ordnance,
            game.character_table[id].medical,
            game.character_table[id].health,
            game.character_table[id].head,
            game.character_table[id].torso,
            game.character_table[id].right_arm,
            game.character_table[id].left_arm,
            game.character_table[id].right_leg,
            game.character_table[id].left_leg,
            game.character_table[id].mental,
            game.character_table[id].movement_stat,
            game.character_table[id].stamina,
        ]

        self.assertEqual(correct, result)

    def test_flush_character_values_dif3(self):
        game = Game()
        all_values = {n: None for n in range(100)}
        wrong_values = []
        for x in range(100):
            values = game.flush_character_traits(3)
            all_values[x] = values

        personal_traits = [
            "strength",
            "dexterity",
            "toughness",
            "perseverance",
            "brilliance",
            "senses",
            "presence",
        ]
        for x in range(100):
            for trait in personal_traits:
                value = all_values[x][trait]
                if value < 3 or value > 7:
                    wrong_values.append(value)

        self.assertEqual(len(wrong_values), 0)

    def test_flush_character_values_dif1(self):
        game = Game()
        all_values = {n: None for n in range(100)}
        wrong_values = []
        for x in range(100):
            values = game.flush_character_traits(1)
            all_values[x] = values

        personal_traits = [
            "strength",
            "dexterity",
            "toughness",
            "perseverance",
            "brilliance",
            "senses",
            "presence",
        ]
        for x in range(100):
            for trait in personal_traits:
                value = all_values[x][trait]
                if value < 1 or value > 5:
                    wrong_values.append(value)

        self.assertEqual(len(wrong_values), 0)

    
    def test_flush_character_values_dif5(self):
        game = Game()
        all_values = {n: None for n in range(100)}
        wrong_values = []
        for x in range(100):
            values = game.flush_character_traits(5)
            all_values[x] = values

        personal_traits = [
            "strength",
            "dexterity",
            "toughness",
            "perseverance",
            "brilliance",
            "senses",
            "presence",
        ]
        for x in range(100):
            for trait in personal_traits:
                value = all_values[x][trait]
                if value < 5 or value > 9:
                    wrong_values.append(value)

        self.assertEqual(len(wrong_values), 0)