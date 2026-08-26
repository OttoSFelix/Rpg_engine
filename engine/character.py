from engine.database import Database
from engine.dice import Dice
DATABASE = Database()
DICE = Dice()

class Character:
    def __init__(
        self, 
        id: int,
        name: str, 
        strength: int, 
        dexterity: int, 
        toughness: int, 
        perseverance: int, 
        brilliance: int, 
        senses: int, 
        presence: int, 
        sharpstrike: int, 
        ravage: int, 
        melee: int, 
        special: int, 
        stealth: int, 
        hardware: int, 
        ordnance: int, 
        medical: int, 
        health: int,
        head: int,
        torso: int,
        right_arm: int,
        left_arm: int,
        right_leg: int,
        left_leg: int,
        mental: int,
        movement_stat: int,
        stamina: int,
        cover: int,
        status: int):

        self.id = id
        self.name = name
        self.strength = strength
        self.dexterity = dexterity
        self.toughness = toughness
        self.perseverance = perseverance
        self.brilliance = brilliance
        self.senses = senses
        self.presence = presence
        self.sharpstrike = sharpstrike
        self.ravage = ravage
        self.melee = melee
        self.special = special
        self.stealth = stealth
        self.hardware = hardware
        self.ordnance = ordnance
        self.medical = medical
        self.health = health
        self.head = head
        self.torso = torso
        self.right_arm = right_arm
        self.left_arm = left_arm
        self.right_leg = right_leg
        self.left_leg = left_leg
        self.mental = mental
        self.movement_stat = movement_stat
        self.stamina = stamina
        self.cover = cover
        self.status = status

        self.held_weapon = None

    def attack(self, target: 'Character', bodypart: str):
        if not self.mental_check():
            return False

        modifier = 0
        if self.held_weapon.type == "sharpstrike":
            modifier += self.sharpstrike
        elif self.held_weapon.type == "ravage":
            modifier += self.ravage
        elif self.held_weapon.type == "melee":
            modifier += self.melee
        elif self.held_weapon.type == "special":
            modifier += self.special

        modifier -= self.movement_stat
        modifier -= target.movement_stat

        rolls = self.held_weapon.attack(modifier)

        total_damage = 0
        for r in rolls:
            total_damage += self.held_weapon.hit_table(r, target.cover)

        if total_damage > 0:
            target.health -= total_damage
            target.bodypart_damage(bodypart, total_damage)
            return True
        return False

    def bodypart_damage(self, bodypart: str, damage: int):
        if bodypart == 'head':
            self.head = max(0, self.head - damage)
        elif bodypart == 'torso':
            self.torso = max(0, self.torso - damage)
        elif bodypart == 'right_arm':
            self.right_arm = max(0, self.right_arm - damage)
        elif bodypart == 'left_arm':
            self.left_arm = max(0, self.left_arm - damage)
        elif bodypart == 'right_leg':
            self.right_leg = max(0, self.right_leg - damage)
        elif bodypart == 'left_leg':
            self.left_leg = max(0, self.left_leg - damage)

    def move(self, amount: int, near_enemy: bool = False):
        if amount == 3:
            weight_modifier = self.get_weight_modifier(self.get_weight_statistic(self.get_inventory_weight()))
            if self.stamina - weight_modifier < 0:
                return False
            self.movement_stat = amount
            self.stamina -= weight_modifier
            return True
        self.movement_stat = amount
        return True

    def mecial_utility(self, item):
        item.use(self)

    def get_inventory_weight(self):
        query = """
        SELECT SUM(weight) FROM items WHERE character_id = %s;
        """
        DATABASE.cursor.execute(query, (self.id,))
        result = int(DATABASE.cursor.fetchall()[0][0])
        DATABASE.conn.commit()

        return result

    def get_inventory_items(self):
        query = """
        SELECT * FROM items WHERE character_id = %s;
        """
        DATABASE.cursor.execute(query, (self.id,))
        result = DATABASE.cursor.fetchall()
        DATABASE.conn.commit()

        return result

    def is_in_inventory(self, item: 'str'):
        query = """
        SELECT * FROM items WHERE character id = %s AND name = %s;
        """
        DATABASE.cursor.execute(query, (self.id, item))
        result = DATABASE.cursor.fetchall()
        DATABASE.conn.commit()

        if len(result) > 0:
            return True
        return False

    def equip_weapon(self, weapon):
        self.held_weapon = weapon

    def mental_check(self):
        roll = DICE.throw('1d12')
        if roll[0] > self.mental:
            return True
        return False

    def get_weight_modifier(self, weight_statistic: int):
        if weight_statistic <= 5:
            return 5
        elif weight_statistic <= 10:
            return 4
        elif weight_statistic <= 15:
            return 3
        elif weight_statistic <= 20:
            return 2
        elif weight_statistic <= 25:
            return 1
        return 0

    def get_weight_statistic(self, weight: int):
        return (self.strength * 10) - weight

    def delete_item(self, item: str):
        query = """
        DELETE FROM items WHERE item_id = %s;
        """
        DATABASE.cursor.execute(query, (item.id,))
        DATABASE.conn.commit()

    def add_item(self, item):
        query = """
        INSERT INTO items(item_id, character_id, name, weight)
        VALUES (%s, %s, %s, %s)
        """
        DATABASE.cursor.execute(query, (item.id, self.id, item.name, item.weight))
        DATABASE.conn.commit()

    def is_injured(self, bodypart: str):
        query = f"""
        SELECT {bodypart} FROM injuries WHERE character_id = %s;
        """
        DATABASE.cursor.execute(query, (self.id,))
        result = DATABASE.cursor.fetchall()
        DATABASE.conn.commit()
        if len(result) == 0 or result[0][0] == 'None':
            return False
        return True

    def injure(self, bodypart: str, damage: int, damage_type: str):
        query = f"""
        INSERT INTO injuries(character_id, {bodypart})
        VALUES(%s, %s);
        """
        throw = DICE.throw('1d12')[0] + damage - self.stat_modifier(self.toughness) 
        injury = self.injury_table(throw, bodypart, damage_type)
        DATABASE.cursor.execute(query, (self.id, injury))
        DATABASE.conn.commit()

    def injury_table(self, throw: int, bodypart: str, damage_type: str):
        table = {
            'head': {
                'sharp': {
                    5: 'wound',
                    9: 'fracture',
                    float('inf'): 'down'
                },
                'blunt': {
                    4: 'concussion',
                    8: 'knocked_out',
                    float('inf'): 'fracture'
                }
            },
            'torso': {
                'sharp': {
                    4: 'None',
                    10: 'wound',
                    1000: 'fracture'
                },
                'blunt': {
                    4: 'None',
                    7: 'impact_stun',
                    10: 'internal_bleeding',
                    float('inf'): 'fracture'
                }
            },
            'right_arm': {
                'sharp': {
                    4: 'None',
                    10: 'wound',
                    float('inf'): 'fracture'
                },
                'blunt': {
                    4: 'None',
                    6: 'dislocation',
                    8: 'impact_stun',
                    10: 'internal_bleeding',
                    float('inf'): 'fracture'
                }
            },
            'left_arm': {
                'sharp': {
                    4: 'None',
                    10: 'wound',
                    float('inf'): 'fracture'
                },
                'blunt': {
                    4: 'None',
                    6: 'dislocation',
                    8: 'impact_stun',
                    10: 'internal_bleeding',
                    float('inf'): 'fracture'
                }
            },
            'right_leg': {
                'sharp': {
                    4: 'None',
                    10: 'wound',
                    float('inf'): 'fracture'
                },
                'blunt': {
                    4: 'None',
                    6: 'dislocation',
                    8: 'impact_stun',
                    10: 'internal_bleeding',
                    float('inf'): 'fracture'
                }
            },
            'left_leg': {
                'sharp': {
                    4: 'None',
                    10: 'wound',
                    float('inf'): 'fracture'
                },
                'blunt': {
                    4: 'None',
                    6: 'dislocation',
                    8: 'impact_stun',
                    10: 'internal_bleeding',
                    float('inf'): 'fracture'
                }
            },
        }

        try:
            for threshold, injury in table[bodypart][damage_type].items():
                if throw <= threshold:
                    return injury
        except KeyError:
            print('Invalid bodypart or damage type in Character.injury_table')

    def stat_modifier(self, value: int):
        if value == 0:
            return -3
        elif value <= 2:
            return -2
        elif value <= 4:
            return -1
        elif value == 5:
            return 0
        elif value <= 7:
            return 1
        elif value <= 9:
            return 2
        elif value >= 10:
            return 3

