from items import Item
from engine import Dice

class Generator:
    DICE = Dice()
    def generate_character_traits(self):
        traits = [
            "strength",
            "dexterity",
            "toughness",
            "perseverance",
            "brilliance",
            "senses",
            "presence",
            "sharpstrike",
            "ravage",
            "melee",
            "special",
            "stealth",
            "hardware",
            "ordnance",
            "medical"
        ]

        values = {}

        throws = Dice.throw(f'{len(traits)}d10')
        for trait, throw in zip(traits, throws):
            if throw < 5:
                throw += 3
            elif throw > 5:
                throw -= 3
            values[trait] = throw
        
        return values

    