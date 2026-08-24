from dice import Dice
import secrets

DICE = Dice()

class Item:
    def __init__(self):
        self.item_table = {
            "mk64": self.mk64()
        }

        self.choise_table = {1: [], 2: [], 3: []}

    def mk64(self):
        id = secrets.token_hex(16)
        print(id)
        # weapon = Weapon()

class Weapon:
    def __init__(
        self, 
        item_id: str, 
        type: str, 
        weight: int, 
        precision: int, 
        power: int, 
        damage: int,
        damage_type: str, 
        range: int, 
        bullet_amount: int, 
        miss_threshold: int,
        hit_threshold: int,
        precise_threshold: int):

        self.type = type
        self.weight = weight
        self.precision = precision
        self.power = power
        self.damage = damage
        self.damage_type = damage_type
        self.range = range
        self.bullet_amount = bullet_amount
        self.item_id = item_id

        self.miss_threshold = miss_threshold
        self.hit_threshold = hit_threshold
        self.precise_threshold = precise_threshold

    def attack(self, modifier):
        result = []
        throws = DICE.throw(f'{self.bullet_amount}d12')
        for throw in throws:
            result.append(throw + modifier + self.precision)
        return result

    def hit_table(self, throw, cover):
        if throw <= self.miss_threshold:
            return 0
        if throw >= self.hit_threshold and throw < self.precise_threshold:
            if self.power >= cover:
                return self.damage
        return self.damage


