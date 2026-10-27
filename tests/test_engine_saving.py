from engine.generator import Generator
from engine.engine import Game
from engine.items import Item
from tests._base_unittest import DatabaseTestcase

class TestSave(DatabaseTestcase):

    def test_characters_after_save(self):
        game = Game()
        gen = Generator()

        traits = gen.generate_character_traits()
        traits['id'] = 1
        traits['name'] = 'TestDummy1'
        game.add_character(traits)

        traits = gen.generate_character_traits()
        traits['id'] = 2
        traits['name'] = 'TestDummy2'
        game.add_character(traits)

        game.save()

        data = self.db.get_characters()

        result = [data[0][0], data[1][0]]
        correct = [1, 2]

        self.assertEqual(correct, result)

    def test_items_after_save(self):
        game = Game()
        gen = Generator()
        gen_item = Item()

        traits = gen.generate_character_traits()
        traits['id'] = 1
        traits['name'] = 'TestDummy1'
        game.add_character(traits)

        item1 = gen_item.load_item('SP-R 208', '2l3j4')
        item2 = gen_item.load_item('MXR-17', '5l6kj7')

        game.character_table[1].inventory.append(item1)
        game.character_table[1].inventory.append(item2)

        game.save()

        data = self.db.get_items()

        result = [data[0][0], data[1][0]]
        correct = ['2l3j4', '5l6kj7']

        self.assertEqual(correct, result)

    def test_injuries_after_save(self):
        game = Game()
        gen = Generator()

        traits = gen.generate_character_traits()
        traits['id'] = 1
        traits['name'] = 'TestDummy1'
        game.add_character(traits)

        game.character_table[1].injury['head'] = 'fracture'
        game.character_table[1].injury['left_leg'] = 'internal_bleeding'

        game.save()

        data = self.db.get_injuries()

        result = [data[0][1], data[0][2], data[0][6]]
        correct = ['fracture', None, 'internal_bleeding']

        self.assertEqual(correct, result)