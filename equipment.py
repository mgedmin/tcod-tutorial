from typing import Dict, Iterable, Optional

from entity import Entity
from equipment_slots import EquipmentSlots
from game_types import ActionResults


class Equipment:

    def __init__(self) -> None:
        self.slots: Dict[EquipmentSlots, Optional[Entity]] = {}

    @property
    def main_hand(self) -> Optional[Entity]:
        return self.slots.get(EquipmentSlots.MAIN_HAND)

    @property
    def off_hand(self) -> Optional[Entity]:
        return self.slots.get(EquipmentSlots.OFF_HAND)

    @property
    def equipped_slots(self) -> Iterable[Entity]:
        return (
            slot
            for slot in self.slots.values()
            if slot and slot.equippable
        )

    @property
    def max_hp_bonus(self) -> int:
        return sum(
            slot.equippable.max_hp_bonus
            for slot in self.equipped_slots
        )

    @property
    def power_bonus(self) -> int:
        return sum(
            slot.equippable.power_bonus
            for slot in self.equipped_slots
        )

    @property
    def defense_bonus(self) -> int:
        return sum(
            slot.equippable.defense_bonus
            for slot in self.equipped_slots
        )

    def is_equipped(self, item: Entity) -> bool:
        return item in self.equipped_slots

    def where_equipped(self, item: Entity) -> Optional[EquipmentSlots]:
        for slot, equiped_item in self.slots.items():
            if equiped_item == item:
                return slot
        return None

    def toggle_equip(self, equippable_entity: Entity) -> ActionResults:
        results: ActionResults = []

        slot = equippable_entity.equippable.slot
        if equippable_entity == self.slots.get(slot):
            self.slots[slot] = None
            results.append({
                'dequipped': equippable_entity,
            })
        else:
            if self.slots.get(slot):
                results.append({
                    'dequipped': self.slots[slot],
                })
            self.slots[slot] = equippable_entity
            results.append({
                'equipped': equippable_entity,
            })

        return results
