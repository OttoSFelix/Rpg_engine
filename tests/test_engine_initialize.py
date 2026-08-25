import unittest
from engine.database import Database
from engine.engine import Game

class TestInit(unittest.TestCase):
    def setUp(self):
        self.db = Database()
        self.db.init_database()

    def tearDown(self):
        self.db.cursor.execute("""
            DELETE FROM items;
            DELETE FROM injuries;
            DELETE FROM talents;
            DELETE FROM characters;
        """)
        self.db.conn.commit()

    def test_characters_after_init(self):
        query = """
        INSERT INTO characters(id, name, strength, dexterity, toughness, perseverance)
        VALUES(1, 'Testihahmo1', 5, 7, 3, 6)
        """
        self.db.cursor.execute(query)

        query = """
        INSERT INTO characters(id, name, strength, dexterity, toughness, perseverance)
        VALUES(2, 'Testihahmo2', 2, 4, 5, 8)
        """
        self.db.cursor.execute(query)
        self.db.conn.commit()

        game = Game()
        game.initialize()

        correct = [[1, 'Testihahmo1', 5, 7, 3, 6], [2, 'Testihahmo2', 2, 4, 5, 8]]
        results = []
        for character in game.character_table.values():
            result_list = [character.id, character.name, character.strength, character.dexterity, character.toughness, character.perseverance]
            results.append(result_list)

        self.assertEqual(correct, results)

