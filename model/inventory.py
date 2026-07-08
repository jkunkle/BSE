from typing import Mapping


class Inventory:

    def __init__(self, limits):
        self.amounts = {}
        self.limits = limits

        for key in self.limits.keys():
            self.amounts[key] = 0

    def __repr__(self):

        return str(self.amounts)

    def accepts_item(self, item_key: str) -> bool:
        return item_key in self.limits

    def get_amount(self, item_key: str) -> int:
        return self.amounts.get(item_key, 0)

    def get_limit(self, item_key: str) -> int:
        return self.limits.get(item_key, 0)

    def get_free_space(self, item_key: str) -> int:
        return self.get_limit(item_key) - self.get_amount(item_key)

    def can_add(self, item_key: str, amount: int) -> bool:
        if amount <= 0:
            return False

        if not self.accepts_item(item_key):
            return False

        return self.get_amount(item_key) + amount <= self.get_limit(item_key)

    def can_remove(self, item_key: str, amount: int) -> bool:
        if amount <= 0:
            return False

        return self.get_amount(item_key) >= amount

    def add(self, item_key: str, amount: int) -> None:
        if amount <= 0:
            raise ValueError("Amount must be positive")

        if not self.accepts_item(item_key):
            raise ValueError(f"Inventory does not accept item '{item_key}'")

        if not self.can_add(item_key, amount):
            raise ValueError(
                f"Not enough storage space for item '{item_key}': "
                f"amount={amount}, free_space={self.get_free_space(item_key)}"
            )

        self.amounts[item_key] = self.get_amount(item_key) + amount

    def remove(self, item_key: str, amount: int) -> None:
        if amount <= 0:
            raise ValueError("Amount must be positive")

        if not self.can_remove(item_key, amount):
            raise ValueError(
                f"Not enough item '{item_key}' to remove: "
                f"amount={amount}, available={self.get_amount(item_key)}"
            )

        self.amounts[item_key] = self.get_amount(item_key) - amount

    def can_add_items(self, items: Mapping[str, int]) -> bool:
        return all(
            self.can_add(item_key, amount)
            for item_key, amount in items.items()
        )

    def can_remove_items(self, items: Mapping[str, int]) -> bool:
        return all(
            self.can_remove(item_key, amount)
            for item_key, amount in items.items()
        )

    def add_items(self, items: Mapping[str, int]) -> None:
        if not self.can_add_items(items):
            raise ValueError(f"Cannot add items to inventory: {dict(items)}")

        for item_key, amount in items.items():
            self.add(item_key, amount)

    def remove_items(self, items: Mapping[str, int]) -> None:
        if not self.can_remove_items(items):
            raise ValueError(f"Cannot remove items from inventory: {dict(items)}")

        for item_key, amount in items.items():
            self.remove(item_key, amount)
