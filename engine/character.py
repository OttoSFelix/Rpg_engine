from engine.engine import Database, Dice
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
        self.preseverance = perseverance
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
        self.mental = mental,
        self.movement_stat = movement_stat
        self.stamina = stamina
        self.cover = cover
        self.status = status

        self.held_weapon = None

    def attack(self, target: 'Character', bodypart):
        if not self.mental_check():
            return False
        target_body = {"head": target.head, "torso": target.torso, "right arm": target.right_arm, "left arm": target.left_arm, "right leg": target.right_leg}
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
            try:
                target_body[bodypart] -= total_damage
            except KeyError:
                print(f'Insufficient bodypart paremeter: {bodypart}')
            return True
        return False

    def move(self, amount, near_enemy):
        if amount == 3:
            weight_modifier = self.get_weight_modifier(self.get_inventory_weight())
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

        return int(DATABASE.cursor.fetchall()[0])

    def get_inventory_items(self):
        query = """
        SELECT * FROM items WHERE character_id = %s;
        """
        DATABASE.cursor.execute(query, (self.id,))

        return DATABASE.cursor.fetchall()

    def is_in_inventory(self, item):
        query = """
        SELECT * FROM items WHERE character id = %s AND name = %s;
        """
        DATABASE.cursor.execute(query, (self.id, item))

        if len(DATABASE.cursor.fetchall()) > 0:
            return True
        return False

    def equip_weapon(self, weapon):
        self.held_weapon = weapon

    def mental_check(self):
        roll = DICE.throw('1d12')
        if roll > self.mental:
            return True
        return False

    def get_weight_modifier(self, weight):
        if weight <= 5:
            return 5
        elif weight <= 10:
            return 4
        elif weight <= 15:
            return 3
        elif weight <= 20:
            return 2
        elif weight <= 25:
            return 1
        return 0

    def delete_item(self, item):
        query = """
        DELETE FROM items WHERE item_id = %s;
        """
        DATABASE.cursor.execute(query, (item.id,))

    def add_item(self, item):
        query = """
        INSERT INTO items(item_id, character_id, name, weight)
        VALUES (%s, %s, %s, %s)
        """
        DATABASE.cursor.execute(query, (item.id, self.id, item.name, item.weight))

