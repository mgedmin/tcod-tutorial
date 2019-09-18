from equipment_slots import EquipmentSlots


class Equippable:

    def __init__(self, slot: EquipmentSlots, power_bonus: int = 0,
                 defense_bonus: int = 0, max_hp_bonus: int = 0):
        self.slot = slot
        self.power_bonus = power_bonus
        self.defense_bonus = defense_bonus
        self.max_hp_bonus = max_hp_bonus
