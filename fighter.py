import tcod

from game_messages import Message


class Fighter:

    def __init__(self, hp, defense, power, xp=0):
        self.base_max_hp = self.hp = hp
        self.base_defense = defense
        self.base_power = power
        self.xp = xp

    @property
    def max_hp(self):
        bonus = 0
        if self.owner and self.owner.equipment:
            bonus += self.owner.equipment.max_hp_bonus
        return self.base_max_hp + bonus

    @property
    def power(self):
        bonus = 0
        if self.owner and self.owner.equipment:
            bonus += self.owner.equipment.power_bonus
        return self.base_power + bonus

    @property
    def defense(self):
        bonus = 0
        if self.owner and self.owner.equipment:
            bonus += self.owner.equipment.defense_bonus
        return self.base_defense + bonus

    def take_damage(self, amount):
        results = []

        self.hp -= amount
        if self.hp <= 0:
            results.append({'dead': self.owner, 'xp': self.xp})

        return results

    def heal(self, amount):
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp

    def attack(self, target):
        results = []

        damage = self.power - target.fighter.defense

        if damage > 0:
            results.append({'message': Message(
                f"{self.owner.name.capitalize()} attacks {target.name}"
                f" for {damage} hit points.",
                tcod.white,
            )})
            results.extend(target.fighter.take_damage(damage))
        else:
            results.append({'message': Message(
                f"{self.owner.name.capitalize()} attacks {target.name}"
                f" but does no damage.",
                tcod.white,
            )})

        return results
