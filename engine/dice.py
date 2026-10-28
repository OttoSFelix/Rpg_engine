import random

class Dice:
    def throw(self, dice: str) -> list:
        amount, sides = dice.split('d')
        result = []
        for d in range(int(amount)):
            n = random.randint(1, int(sides))
            result.append(n)
        return result