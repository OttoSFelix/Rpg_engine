import unittest
from unittest.mock import Mock
from engine.engine import Game
from engine.database import Database
from engine.character import Character
from tests._base_unittest import DatabaseTestcase

class TestMechanics(DatabaseTestcase):
    def setUp(self):
        self.db = Database()
        self.db.init_database()

        self.addCleanup(self.clean_database)

        query = """
        INSERT INTO characters(id, name, strength, dexterity, toughness, perseverance, brilliance, senses, presence, sharpstrike, ravage, melee, special, stealth, hardware, ordnance, medical, health, head, torso, right_arm, left_arm, right_leg, left_leg, mental, movement_stat, stamina, full_cover, head_cover, torso_cover, right_arm_cover, left_arm_cover, right_leg_cover, left_leg_cover, status)
        VALUES(1, 'TestDummy', 5, 5, 4, 6, 7, 8, 3, 6, 3, 4, 6, 7, 2, 7, 6, 5, 1, 3, 2, 2, 2, 2, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 'None')
        """
        self.db.cursor.execute(query)
        query = """
        INSERT INTO characters(id, name, strength, dexterity, toughness, perseverance, brilliance, senses, presence, sharpstrike, ravage, melee, special, stealth, hardware, ordnance, medical, health, head, torso, right_arm, left_arm, right_leg, left_leg, mental, movement_stat, stamina, full_cover, head_cover, torso_cover, right_arm_cover, left_arm_cover, right_leg_cover, left_leg_cover, status)
        VALUES(2, 'TestTarget', 5, 5, 4, 6, 7, 8, 3, 6, 3, 4, 6, 7, 2, 7, 6, 5, 1, 3, 2, 2, 2, 2, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 'None')
        """
        self.db.cursor.execute(query)
        self.db.cursor.execute("INSERT INTO items(item_id, character_id, name, weight) VALUES('921234y4', 1, 'test_item', 7)")
        self.db.cursor.execute("INSERT INTO items(item_id, character_id, name, weight) VALUES('8283y4', 1, 'test_item', 7)")
        self.db.cursor.execute("INSERT INTO items(item_id, character_id, name, weight) VALUES('fas3y4', 1, 'test_item', 7)")
        self.db.cursor.execute("INSERT INTO items(item_id, character_id, name, weight) VALUES('fhiuwe', 1, 'test_item', 7)")
        self.db.cursor.execute("INSERT INTO items(item_id, character_id, name, weight) VALUES('089w7efygri', 1, 'test_item', 7)")
        self.db.conn.commit()

        self.game = Game()
        self.game.initialize()


    def test_move(self):
        character: Character = self.game.character_table[1]
        character.move(2)
        self.assertEqual(character.movement_stat, 2)

    def test_stamina(self):
        character: Character = self.game.character_table[1]
        stamina_before = character.stamina
        weight = character.get_inventory_weight()
        weight_modifier = character.get_weight_modifier(character.get_weight_statistic(weight))
        character.move(3)

        self.assertEqual(character.stamina, stamina_before - weight_modifier)

    def test_get_inventory_weight(self):
        character: Character = self.game.character_table[1]
        
        weight = character.get_inventory_weight()
        self.assertEqual(weight, 35)

    def test_get_inventory_items(self):
        character: Character = self.game.character_table[1]
        items = [item.item_id for item in character.get_inventory_items()]

        correct = [
            '921234y4',
            '8283y4',
            'fas3y4',
            'fhiuwe',
            '089w7efygri',
        ]
        
        self.assertEqual(correct, items)

    def test_mental_check_0(self):
        character: Character = self.game.character_table[1]
        throws = []
        for _ in range(100):
            throws.append(character.mental_check())

        self.assertEqual(throws, [True] * 100)

    def test_get_weight_modifier(self):
        character: Character = self.game.character_table[1]

        correct = [5, 4, 3, 2, 1, 0]
        results = []
        results.append(character.get_weight_modifier(5))
        results.append(character.get_weight_modifier(6))
        results.append(character.get_weight_modifier(14))
        results.append(character.get_weight_modifier(20))
        results.append(character.get_weight_modifier(22))
        results.append(character.get_weight_modifier(100))

        self.assertEqual(correct, results)

    def test_get_weight_statistic(self):
        character: Character = self.game.character_table[1]
        statistic = character.get_weight_statistic(character.get_inventory_weight())

        self.assertEqual(statistic, 15)

    def test_delete_item(self):
        character: Character = self.game.character_table[1]
        character.delete_item('fas3y4')
        items = [item.item_id for item in character.get_inventory_items()]

        correct = [
            '921234y4',
            '8283y4',
            'fhiuwe',
            '089w7efygri',
        ]

        self.assertEqual(correct, items)

    def test_add_item(self):
        character: Character = self.game.character_table[1]
        
        item = Mock()
        item.item_id = '839huj'
        item.name = 'test_item'
        item.weight = 3
        character.add_item(item)
        items = [i.item_id for i in character.get_inventory_items()]

        correct = [
            '921234y4',
            '8283y4',
            'fas3y4',
            'fhiuwe',
            '089w7efygri',
            '839huj',
        ]


        self.assertEqual(correct, items)

    def test_attack(self):
        character: Character = self.game.character_table[1]
        target: Character = self.game.character_table[2]
        character.equip_weapon(self.game.item_table['fas3y4'])

        before_health = target.health
        before_torso = target.torso

        character.attack(target, 'torso')

        valid = True
        if before_health <= target.health:
            valid = False
        if before_torso <= target.torso:
            valid = False

        self.assertEqual(True, valid)
        
    def test_stat_modifier(self):
        character: Character = self.game.character_table[1]
        
        stats = [5, 6, 1, 4, 8, 9, 7, 10, 3, 0]
        correct = [0, 1, -2, -1, 2, 2, 1, 3, -1, -3]
        result = []

        for s in stats:
            result.append(character.stat_modifier(s))
        
        self.assertEqual(correct, result)