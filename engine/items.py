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

    RAVAGE_MAGAZINE_SIZE = 12
    SHARPSTRIKE_MAGAZINE_SIZE = 6
    SHOTGUN_MAGAZINE_SIZE = 6

    def __init__(self):
        self.item_table = {
            "MXR-17": self.mxr_17,
            "SP-R 208": self.spr_208,
            "CODA-9": self.coda_9,
            "C4": self.c4,
            "flash": self.flash,
            "Hyposhot Injector": self.hyposhot_injector,
            "Hyposhot A": self.hyposhot_a,
            "Hyposhot Z": self.hyposhot_z,
            "lockpick": self.lockpick,
            "test_item": self.test_item,

        }        

    def load_item(self, name: str, id: str):
        item = self.item_table[name]()
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
            magazine_size=Item.RAVAGE_MAGAZINE_SIZE,
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
            magazine_size=Item.SHARPSTRIKE_MAGAZINE_SIZE,
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
            magazine_size=Item.SHARPSTRIKE_MAGAZINE_SIZE,
            miss_threshold=Item.SHARPSTRIKE_MISS_THRESHOLD,
            hit_threshold=Item.SHARPSTRIKE_HIT_THRESHOLD,
            precise_threshold=Item.SHARPSTRIKE_PRECISE_THRESHOLD,
            two_handed=False
        )

    def hyposhot_injector(self):
        id = secrets.token_hex(8)
        return Stim(
            item_id=id,
            name='Hyposhot Injector',
            effect={},
            duration=0,
            weight=4
        )

    def hyposhot_a(self):
        id = secrets.token_hex(8)
        effect = {'senses': 1, 'mental': -2, 'toughness': 1, 'perseverance': 1}
        return Stim(
            item_id=id,
            name='Hyposhot A',
            effect=effect,
            duration=5,
            weight=2
        )

    def hyposhot_z(self):
        id = secrets.token_hex(8)
        effect = {'mental': -2}
        return Stim(
            item_id=id,
            name='Hyposhot Z',
            effect=effect,
            duration=float('inf'),
            weight=2
        )

    def c4(self):
        id = secrets.token_hex(8)
        return Ordnance(
            name='C4',
            item_id=id,
            damage=4,
            power=5,
            area_of_effect=1,
            weight=4
        )

    def flash(self):
        id = secrets.token_hex(8)
        return Ordnance(
            name='flash',
            item_id=id,
            damage=0,
            power=0,
            area_of_effect=5,
            weight=4,
            effect='blind'
        )

    def lockpick(self):
        id = secrets.token_hex(8)
        return Tool(
            name='lockpick',
            item_id=id,
            weight=2,
            check=['hardware'],
            success_threshold=8
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
            12,
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
        magazine_size: int, 
        miss_threshold: int,
        hit_threshold: int,
        precise_threshold: int,
        two_handed: bool = True):

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

        self.magazine_size = magazine_size
        
        self.magazine_bullets = magazine_size
        self.miss_threshold = miss_threshold
        self.hit_threshold = hit_threshold
        self.precise_threshold = precise_threshold
        
        self.two_handed = two_handed

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

    def __str__(self):
        return self.name



class Ordnance:
    def __init__(
        self,
        item_id: str,
        name: str,
        damage: int,
        power: int,
        area_of_effect: int,
        weight: int,
        effect: str = None):

        self.item_id = item_id
        self.name = name
        self.damage = damage
        self.power = power
        self.area_of_effect = area_of_effect
        self.weight = weight
        self.effect = effect

    def __str__(self):
        return self.name


class Stim:
    def __init__(
        self,
        item_id: str,
        name: str,
        effect: dict,
        duration: int,
        weight: int):

        self.item_id = item_id
        self.name = name
        self.effect = effect
        self.duration = duration
        self.weight = weight

    def use(self, character: Character):
        for stat, modifier in self.effect:
            character.statistic_lookup[stat] += modifier

    def undo(self, character: Character):
        for stat, modifier in self.effects:
            character.statistic_lookup[stat] -= modifier

    def __str__(self):
        return self.name


class Tool:
    def __init__(
        self,
        item_id: str,
        name: str,
        weight: int,
        check: list,
        success_threshold: int):

        self.item_id = item_id
        self.name = name
        self.weight = weight
        self.check = check
        self.success_threshold = success_threshold

    def use(self, character: Character):
        throw = DICE.throw('1d12')[0]

        for statistic in self.check:
            throw += character.statistic_lookup[statistic]

        if throw >= self.success_threshold:
            return True
        return False

    def __str__(self):
        return self.name
