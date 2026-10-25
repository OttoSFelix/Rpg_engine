from unicodedata import name
from engine.dice import Dice
from engine.character import Character, get_random_bodypart
import secrets

DICE = Dice()

class Item:
    RAVAGE_MISS_THRESHOLD = 7
    RAVAGE_HIT_THRESHOLD = 8
    RAVAGE_PRECISE_THRESHOLD = 12

    SHARPSTRIKE_MISS_THRESHOLD = 7
    SHARPSTRIKE_HIT_THRESHOLD = 8
    SHARPSTRIKE_PRECISE_THRESHOLD = 12

    def __init__(self):
        self.item_table = {
            "MXR-17": self.mxr_17(),
            "SP-R 208": self.spr_208(),
            "CODA-9": self.coda_9(),
            "test_item": self.test_item(),

        }

        self.difficulty_choise_table = {1: [], 2: [], 3: [], 4: [], 5: []}

    def load_item(self, name: str, id: str):
        item = self.item_table[name]
        item.item_id = id
        return item

    def mxr_17(self):
        id = secrets.token_hex(8)
        return Weapon(
            name='MXR-17',
            item_id=id,
            type='ravage',
            weight=10,
            precision=0,
            power=3,
            damage=3,
            damage_type='sharp',
            range=50,
            bullet_amount=None,
            miss_threshold=Item.RAVAGE_MISS_THRESHOLD,
            hit_threshold=Item.RAVAGE_HIT_THRESHOLD,
            precise_threshold=Item.RAVAGE_PRECISE_THRESHOLD
        )

    def spr_208(self):
        id = secrets.token_hex(8)
        return Weapon(
            name='SP-R 208',
            item_id=id,
            type='sharpstrike',
            weight=10,
            precision=1,
            power=2,
            damage=3,
            damage_type='sharp',
            range=100,
            bullet_amount=1,
            miss_threshold=Item.SHARPSTRIKE_MISS_THRESHOLD,
            hit_threshold=Item.SHARPSTRIKE_HIT_THRESHOLD,
            precise_threshold=Item.SHARPSTRIKE_PRECISE_THRESHOLD
        )

    def coda_9(self):
        id = secrets.token_hex(8)
        return Weapon(
            name='CODA-9',
            item_id=id,
            type='sharpstrike',
            weight=5,
            precision=1,
            power=1,
            damage=2,
            damage_type='sharp',
            range=50,
            bullet_amount=1,
            miss_threshold=Item.SHARPSTRIKE_MISS_THRESHOLD,
            hit_threshold=Item.SHARPSTRIKE_HIT_THRESHOLD,
            precise_threshold=Item.SHARPSTRIKE_PRECISE_THRESHOLD
        )


    def test_item(self):
        return Weapon(
            'test_item',
            '1',
            'ravage',
            7,
            10,
            2,
            2,
            'sharp',
            10,
            2,
            7,
            8,
            12
        )

class Weapon:
    def __init__(
        self,
        name: str,
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
        self.name = name
        
        self.magazine_bullets = 0
        self.miss_threshold = miss_threshold
        self.hit_threshold = hit_threshold
        self.precise_threshold = precise_threshold

    def attack(self, modifier: int):
        result = []
        throws = DICE.throw(f'{self.bullet_amount}d12')
        for throw in throws:
            result.append(throw + modifier + self.precision)
            if self.magazine_bullets - 1 < 0:
                break
            self.magazine_bullets -= 1
        return result

    def hit_table(self, throw: int, target: Character, bodypart: str) -> tuple:
        if throw <= self.miss_threshold:
            return 0, 'None'
        if throw >= self.hit_threshold and throw < self.precise_threshold:
            random_bodypart = get_random_bodypart()
            if self.power >= target.get_bodypart_cover(random_bodypart):
                return self.damage, random_bodypart
            else:
                return 0, random_bodypart

        return self.damage, bodypart


