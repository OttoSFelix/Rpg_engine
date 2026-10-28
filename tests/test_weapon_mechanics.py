from unittest.mock import Mock
from engine.engine import Game
from engine.database import Database
from engine.character import Character
from tests._base_unittest import DatabaseTestcase
class TestWeaponMechanics(DatabaseTestcase):
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
        self.db.cursor.execute("INSERT INTO items(item_id, character_id, name, weight) VALUES('fas3y4', 1, 'test_item', 7)")
        self.db.cursor.execute("INSERT INTO items(item_id, character_id, name, weight) VALUES('24jh32', 1, 'ravage magazine', 3)")
        self.db.conn.commit()

        self.game = Game()
        self.game.initialize()

    def test_weapon_magazine_bullets(self):
        character: Character = self.game.character_table[1]
        target: Character = self.game.character_table[2]

        character.equip_weapon(self.game.item_table['fas3y4'])
        character.held_weapon.bullet_amount = 4

        initial_bullet_amount = character.held_weapon.magazine_bullets

        character.attack(target, 'head')

        after_bullet_amount = character.held_weapon.magazine_bullets

        self.assertEqual(after_bullet_amount, initial_bullet_amount - 4)

    def test_weapon_magazine_limit(self):
        character: Character = self.game.character_table[1]
        target: Character = self.game.character_table[2]

        character.equip_weapon(self.game.item_table['fas3y4'])
        character.held_weapon.bullet_amount = 4
        character.held_weapon.magazine_bullets = 3

        result = character.held_weapon.attack(0)
        
        self.assertEqual(3, len(result))

    def test_weapon_magazine_empty(self):
        character: Character = self.game.character_table[1]
        target: Character = self.game.character_table[2]

        character.equip_weapon(self.game.item_table['fas3y4'])
        character.held_weapon.bullet_amount = 4
        character.held_weapon.magazine_bullets = 3

        character.attack(target, 'torso')

        magazine_bullets = character.held_weapon.magazine_bullets

        self.assertEqual(0, magazine_bullets)

    def test_weapon_reload_with_spare_mag(self):
        character: Character = self.game.character_table[1]
        target: Character = self.game.character_table[2]

        character.equip_weapon(self.game.item_table['fas3y4'])
        character.held_weapon.magazine_bullets = 6

        character.attack(target, 'torso')

        character.held_weapon.reload(character)

        magazine_bullets = character.held_weapon.magazine_bullets

        self.assertEqual(12, magazine_bullets)

    def test_weapon_reload_without_spare_mag(self):
        character: Character = self.game.character_table[1]
        target: Character = self.game.character_table[2]

        character.equip_weapon(self.game.item_table['fas3y4'])
        character.delete_item('24jh32')
        character.held_weapon.magazine_bullets = 6

        character.attack(target, 'torso')

        character.held_weapon.reload(character)

        magazine_bullets = character.held_weapon.magazine_bullets

        self.assertEqual(4, magazine_bullets)
        
