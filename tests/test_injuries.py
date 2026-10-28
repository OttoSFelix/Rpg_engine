import unittest
from engine.engine import Game
from engine.database import Database
from engine.character import Character
from tests._base_unittest import DatabaseTestcase

class TestInjuries(DatabaseTestcase):
    def setUp(self):
        self.db = Database()
        self.db.init_database()

        self.addCleanup(self.clean_database)

        query = """
        INSERT INTO characters(id, name, strength, dexterity, toughness, perseverance, brilliance, senses, presence, sharpstrike, ravage, melee, special, stealth, hardware, ordnance, medical, health, head, torso, right_arm, left_arm, right_leg, left_leg, mental, movement_stat, stamina, full_cover, head_cover, torso_cover, right_arm_cover, left_arm_cover, right_leg_cover, left_leg_cover, status)
        VALUES(1, 'TestDummy', 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 1, 3, 0, 2, 2, 2, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 'None')
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

    def test_injury_in_database(self):
        character: Character = self.game.character_table[1]
        character.injure('right_arm', 1000, 'sharp')

        result = character.injury['right_arm']

        self.assertEqual(result, 'fracture')

    def test_is_injured(self):
        character: Character = self.game.character_table[1]
        character.injure('torso', 1000, 'sharp')

        result = character.is_injured('torso')

        self.assertEqual(True, result)

    def test_injury_table(self):
        character: Character = self.game.character_table[1]
        
        injuries = [[3, 'torso', 'sharp'], [5, 'left_leg', 'blunt'], [12, 'head', 'sharp'], [7, 'right_arm', 'blunt'], [9, 'right_leg', 'blunt'], [5, 'head', 'sharp']]
        correct = ['None', 'dislocation', 'down', 'impact_stun', 'internal_bleeding', 'wound']
        result = []

        for i in injuries:
            result.append(character.injury_table(i[0], i[1], i[2]))

        self.assertEqual(correct, result)

    def test_injury_attack_modifier(self):
        character: Character = self.game.character_table[1]
        character.equip_weapon(self.game.item_table['089w7efygri'])
        
        result = []

        character.injury['head'] = 'fracture'
        character.injury['torso'] = 'impact_stun'
        character.injury['right_arm'] = 'dislocation'

        result.append(character.injury_attack_modifier())

        character.reset_injuries()

        character.injury['head'] = 'concussion'
        character.injury['torso'] = 'wound'
        character.injury['right_arm'] = 'wound'
        character.injury['left_arm'] = 'wound'

        result.append(character.injury_attack_modifier())

        character.reset_injuries()

        character.injury['general'].append('blind')

        result.append(character.injury_attack_modifier())
        
        correct = [13, 7, 8]

        self.assertEqual(correct, result)

    def test_reset_injuries(self):
        character: Character = self.game.character_table[1]

        character.injury['head'] = 'concussion'
        character.injury['torso'] = 'wound'
        character.injury['right_arm'] = 'wound'
        character.injury['left_arm'] = 'wound'
        character.injury['general'].append('suffocating')

        character.reset_injuries()

        result = []

        result.append(character.injury['head'])
        result.append(character.injury['torso'])
        result.append(character.injury['right_arm'])
        result.append(character.injury['left_arm'] )
        result.append(character.injury['general'])

        correct = [None, None, None, None, []]

        self.assertEqual(correct, result)

    def test_movement_after_injury(self):
        character: Character = self.game.character_table[1]

        character.injury['right_leg'] = 'fracture'

        result = []
        result.append(character.movement_stat)
        result.append(character.move(3))
        result.append(character.move(2))
        result.append(character.move(1))
        result.append(character.movement_stat)

        correct = [0, False, False, True, 1]

        self.assertEqual(correct, result)