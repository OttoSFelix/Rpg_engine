from engine.dice import Dice
DICE = Dice()

def get_random_bodypart() -> str:
        throw = DICE.throw('1d12')[0]

        if throw == 12:
            return 'head'
        if throw >= 10:
            return 'left_arm'
        if throw >= 8:
            return 'right_arm'
        if throw >= 5:
            return 'torso'
        if throw >= 3:
            return 'left_leg'
        return 'right_leg'

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
        full_cover: int,
        head_cover: int,
        torso_cover: int,
        right_arm_cover: int,
        left_arm_cover: int,
        right_leg_cover: int,
        left_leg_cover: int,
        status: str):

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
        self.full_cover = full_cover
        self.head_cover = head_cover
        self.torso_cover = torso_cover
        self.right_arm_cover = right_arm_cover
        self.left_arm_cover = left_arm_cover
        self.right_leg_cover = right_leg_cover
        self.left_leg_cover = left_leg_cover
        self.status = status

        self.effects = []

        self.injury = {'head': None, 'torso': None, 'right_arm': None, 'left_arm': None, 'right_leg': None, 'left_leg': None, 'general': []}

        self.inventory = []

        self.held_weapon = None

        self.statistic_lookup = {'strength': self.strength, 'dexterity': self.dexterity, 'toughness': self.toughness, 'perseverance': self.perseverance, \
        'brilliance': self.brilliance, 'senses': self.senses, 'presence': self.presence, 'mental': self.mental, 'sharpstrike': self.sharpstrike, 'ravage': self.ravage, \
        'melee': self.melee, 'special': self.special, 'stealth': self.stealth, 'hardware': self.hardware, 'ordnance': self.ordnance, 'medical': self.medical}

    def attack(self, target: 'Character', bodypart: str) -> bool:
        if self.is_down():
            return False

        if not self.mental_check():
            return False

        target_initial_bodypart_health = {
            'head': target.head,
            'torso': target.torso,
            'right_arm': target.right_arm,
            'left_arm': target.left_arm,
            'right_leg': target.right_leg,
            'left_leg': target.left_leg
            }

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

        modifier -= self.injury_attack_modifier()

        rolls = self.held_weapon.attack(modifier)

        total_damage = 0
        for r in rolls:
            damage, hit_bodypart = self.held_weapon.hit_table(r, target, bodypart)

            if damage <= 0:
                continue
            total_damage += damage
            target.bodypart_damage(hit_bodypart, damage)

        if total_damage > 0:
            target.health -= total_damage

            for part in target_initial_bodypart_health.keys():
                initial_health = target_initial_bodypart_health[part]
                current_health = target.get_bodypart_health(part)
                if current_health == 0 and initial_health != 0:
                    target.injure(part, initial_health - current_health, self.held_weapon.damage_type)

            return True
        return False

    def bodypart_damage(self, bodypart: str, damage: int) -> None:
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
        else:
            raise KeyError(f'Invalid bodypart in Character.bodypart_damage: {bodypart}')

    def move(self, amount: int, near_enemy: bool = False) -> bool:
        for injury in self.injury['general']:
            if type(injury) == str:
                if injury == 'blind':
                    if amount > 2:
                        return False
                    self.movement_stat = amount
                    return True

        if self.injury['right_leg'] == 'impact_stun' or self.injury['left_leg'] == 'impact_stun':
            adrenaline = False
            for effect in self.effects:
                if effect[0] == 'Hyposhot A':
                    adrenaline = True
            
            if not adrenaline:
                if amount > 1:
                    return False
                self.movement_stat = amount
                return True
            else:
                if amount == 3:
                    weight_modifier = self.get_weight_modifier(self.get_weight_statistic(self.get_inventory_weight()))
                    if self.stamina - weight_modifier < 0:
                        return False
                    self.movement_stat = amount
                    self.stamina -= weight_modifier
                    return True
                self.movement_stat = amount
                return True

        if self.injury['right_leg'] == 'fracture' or self.injury["left_leg"] == 'fracture':
            if amount > 1:
                return False
            self.movement_stat = amount 
            return True

        if amount == 3:
            weight_modifier = self.get_weight_modifier(self.get_weight_statistic(self.get_inventory_weight()))
            if self.stamina - weight_modifier < 0:
                return False
            self.movement_stat = amount
            self.stamina -= weight_modifier
            return True
        self.movement_stat = amount
        return True

    def medical_utility(self, item) -> bool:
        if self.mental_check():
            return item.use(self)
        return False

    def get_inventory_weight(self) -> int:
        total = 0

        for item in self.inventory:
            total += item.weight

        return total

    def get_inventory_items(self) -> list:
        return self.inventory[:]

    def is_in_inventory(self, id: 'str') -> bool:
        for item in self.inventory:
            if item.item_id == id:
                return True
        return False

    def equip_weapon(self, weapon) -> None:
        self.held_weapon = weapon

    def get_mental(self) -> int:
        mental = self.mental
        if self.injury['head'] == 'concussion':
            mental += 4

        return mental

    def mental_check(self) -> bool:
        roll = DICE.throw('1d12')[0]
        if roll + self.stat_modifier(self.perseverance) > self.get_mental():
            return True
        return False

    def get_weight_modifier(self, weight_statistic: int) -> int:
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

    def get_weight_statistic(self, weight: int) -> int:
        return (self.strength * 10) - weight

    def delete_item(self, id: str) -> None:
        pointer = 0
        for item in self.inventory:
            if item.item_id == id:
                self.inventory.pop(pointer)
                return
            pointer += 1

    def add_item(self, item) -> None:
        self.inventory.append(item)

    def is_injured(self, bodypart: str) -> bool:
        if self.injury[bodypart] != None:
            return True
        return False

    def injure(self, bodypart: str, damage: int, damage_type: str) -> None:
        throw = DICE.throw('1d12')[0] + damage - self.stat_modifier(self.toughness) 
        injury = self.injury_table(throw, bodypart, damage_type)

        if bodypart == 'general':
            self.injury[bodypart].append(injury)
        else:
            if bodypart == 'head' and injury == 'down':
                self.injury['general'].append(injury)
            else:
                self.injury[bodypart] = injury

    def cure(self, bodypart: str) -> None:
        self.injury[bodypart] = None

    def injury_table(self, throw: int, bodypart: str, damage_type: str) -> str:
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
                    float('inf'): 'fracture'
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

    def stat_modifier(self, value: int) -> int:
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

    def get_character_attributes(self) -> dict:
        values = {
            "id": self.id,
            "name": self.name,
            "strength": self.strength,
            "dexterity": self.dexterity,
            "toughness": self.toughness,
            "perseverance": self.perseverance,
            "brilliance": self.brilliance,
            "senses": self.senses,
            "presence": self.presence,
            "sharpstrike": self.sharpstrike,
            "ravage": self.ravage,
            "melee": self.melee,
            "special": self.special,
            "stealth": self.stealth,
            "hardware": self.hardware,
            "ordnance": self.ordnance,
            "medical": self.medical,
            "health": self.health,
            "head": self.head,
            "torso": self.torso,
            "right_arm": self.right_arm,
            "left_arm": self.left_arm,
            "right_leg": self.right_leg,
            "left_leg": self.left_leg,
            "mental": self.mental,
            "movement_stat": self.movement_stat,
            "stamina": self.stamina,
            "full_cover": self.full_cover,
            "head_cover": self.head_cover,
            "torso_cover": self.torso_cover,
            "right_arm_cover": self.right_arm_cover,
            "left_arm_cover": self.left_arm_cover,
            "right_leg_cover": self.right_leg_cover,
            "left_leg_cover": self.left_leg_cover,
            "status": self.status,
        }
        return values

    def get_bodypart_health(self, bodypart: str) -> int:
        if bodypart == 'head':
            return self.head
        if bodypart == 'left_arm':
            return self.left_arm
        if bodypart == 'right_arm':
            return self.right_arm
        if bodypart == 'torso':
            return self.torso
        if bodypart == 'left_leg':
            return self.left_leg
        if bodypart == 'right_leg':
            return self.right_leg
        if bodypart == 'full':
            return self.health

        return ValueError(f"Invalid bodypart in Character.get_bodypart_health: {bodypart}")

    def get_bodypart_cover(self, bodypart: str) -> int:
        if bodypart == 'head':
            return self.head_cover
        if bodypart == 'left_arm':
            return self.left_arm_cover
        if bodypart == 'right_arm':
            return self.right_arm_cover
        if bodypart == 'torso':
            return self.torso_cover
        if bodypart == 'left_leg':
            return self.left_leg_cover
        if bodypart == 'right_leg':
            return self.right_leg_cover
        if bodypart == 'health':
            return self.full_cover

        return ValueError(f"Invalid bodypart in Character.get_bodypart_cover: {bodypart}")

    def injury_attack_modifier(self) -> int:
        # ∀total_modifier >= 0
        total_modifier = 0

        wound_modifier = 1
        dislocation_modifier = 3
        stun_modifier = 4

        for effect in self.effects:
            if effect[0] == "Hyposhot A":
                wound_modifier = 0
                dislocation_modifier = 0
                stun_modifier = 0
            

        if self.held_weapon.two_handed:
            if self.injury['right_arm'] == 'fracture':
                total_modifier += 6
            if self.injury['left_arm'] == 'fracture':
                total_modifier += 6
            if self.injury['right_arm'] == 'wound':
                total_modifier += wound_modifier
            if self.injury['left_arm'] == 'wound':
                total_modifier += wound_modifier
            if self.injury['right_arm'] == 'dislocation':
                total_modifier += dislocation_modifier
            if self.injury['left_arm'] == 'dislocation':
                total_modifier += dislocation_modifier
            if self.injury['right_arm'] == 'impact_stun':
                total_modifier += stun_modifier
            if self.injury['left_arm'] == 'impact_stun':
                total_modifier += stun_modifier
        else:
            total_modifier += min(self.injury_modifier_value(self.injury['right_arm']), self.injury_modifier_value(self.injury['left_arm']))

        if self.injury['torso'] == 'fracture':
            total_modifier += 3
        if self.injury['torso'] == 'wound':
            total_modifier += wound_modifier
        if self.injury['torso'] == 'impact_stun':
            total_modifier += stun_modifier
        
        if self.injury['head'] == 'fracture':
            total_modifier += 6
        if self.injury['head'] == 'wound':
            total_modifier += wound_modifier
        if self.injury['head'] == 'concussion':
            total_modifier += 4

        for injury in self.injury['general']:
            if type(injury) == tuple:
                if injury[0] == 'suffocating':
                    total_modifier += injury[1]
            else:
                if injury == 'blind':
                    total_modifier += 8 - self.stat_modifier(self.senses)


        return total_modifier   

    def injury_modifier_value(self, value: str) -> int:
        if value == 'wound':
            return 1
        if value == 'fracture':
            return 6
        if value == 'dislocation':
            return 3
        if value == 'impact_stun':
            return 4
        return 0

    def reset_injuries(self) -> int:
        for part, injury in self.injury.items():
            self.injury[part] = None
        self.injury['general'] = []

    def is_down(self):
        for injury in self.injury['general']:
            if injury == 'down':
                return True
        if self.health <= 0:
            return True
        return False

    def __str__(self):
        string = ""
        string += self.name
        string += f" [{self.id}] "
        string += f"{self.health} HP "
        if self.status != None and self.status != 'None':
            string += f"({self.status})"
        return string