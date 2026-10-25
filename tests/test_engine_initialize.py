import unittest
from engine.engine import Game
from tests._base_unittest import DatabaseTestcase

class TestInit(DatabaseTestcase):
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


    def test_item_table_after_init(self):
        query = """
        INSERT INTO characters(id, name, strength, dexterity, toughness, perseverance)
        VALUES(1, 'Testihahmo1', 5, 7, 3, 6)
        """
        self.db.cursor.execute(query)

        self.db.cursor.execute("INSERT INTO items(item_id, character_id, name, weight) VALUES('921234y4', 1, 'test_item', 7)")
        self.db.cursor.execute("INSERT INTO items(item_id, character_id, name, weight) VALUES('8283y4', 1, 'test_item', 7)")
        self.db.cursor.execute("INSERT INTO items(item_id, character_id, name, weight) VALUES('fas3y4', 1, 'test_item', 7)")
        self.db.cursor.execute("INSERT INTO items(item_id, character_id, name, weight) VALUES('fhiuwe', 1, 'test_item', 7)")
        self.db.cursor.execute("INSERT INTO items(item_id, character_id, name, weight) VALUES('089w7efygri', 1, 'test_item', 7)")
        self.db.conn.commit()

        game = Game()
        game.initialize()

        correct = [
            '921234y4',
            '8283y4',
            'fas3y4',
            'fhiuwe',
            '089w7efygri'
        ]

        result = [item.item_id for item in game.item_table.values()]

        self.assertEqual(correct, result)

    def test_character_inventory_after_init(self):
        query = """
        INSERT INTO characters(id, name, strength, dexterity, toughness, perseverance)
        VALUES(1, 'Testihahmo1', 5, 7, 3, 6)
        """
        self.db.cursor.execute(query)

        self.db.cursor.execute("INSERT INTO items(item_id, character_id, name, weight) VALUES('921234y4', 1, 'test_item', 7)")
        self.db.cursor.execute("INSERT INTO items(item_id, character_id, name, weight) VALUES('8283y4', 1, 'test_item', 7)")
        self.db.cursor.execute("INSERT INTO items(item_id, character_id, name, weight) VALUES('fas3y4', 1, 'test_item', 7)")
        self.db.cursor.execute("INSERT INTO items(item_id, character_id, name, weight) VALUES('fhiuwe', 1, 'test_item', 7)")
        self.db.cursor.execute("INSERT INTO items(item_id, character_id, name, weight) VALUES('089w7efygri', 1, 'test_item', 7)")
        self.db.conn.commit()

        game = Game()
        game.initialize()

        inventory_size = len(game.character_table[1].inventory)

        self.assertEqual(5, inventory_size)