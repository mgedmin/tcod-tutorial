import tcod

from components import Component
from entity import Entity
from game_messages import Message
from game_types import ActionResults


class Fighter(Component):

    def __init__(self, hp: int, defense: int, power: int, xp: int = 0):
        self.base_max_hp = self.hp = hp
        self.base_defense = defense
        self.base_power = power
        self.xp = xp

    @property
    def max_hp(self) -> int:
        bonus = 0
        if self.owner and self.owner.equipment:
            bonus += self.owner.equipment.max_hp_bonus
        return self.base_max_hp + bonus

    @property
    def power(self) -> int:
        bonus = 0
        if self.owner and self.owner.equipment:
            bonus += self.owner.equipment.power_bonus
        return self.base_power + bonus

    @property
    def defense(self) -> int:
        bonus = 0
        if self.owner and self.owner.equipment:
            bonus += self.owner.equipment.defense_bonus
        return self.base_defense + bonus

    def take_damage(self, amount: int) -> ActionResults:
        results = []

        self.hp -= amount
        if self.hp <= 0:
            results.append({'dead': self.owner, 'xp': self.xp})

        return results

    def heal(self, amount: int) -> None:
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp

    def attack(self, target: Entity) -> ActionResults:
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
