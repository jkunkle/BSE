from dataclasses import dataclass

@dataclass()
class Contract:

    id : int
    item_key : str
    amount : int
    # NOTE -- prices are stored here separately
    # of the configuration in order to allow
    # dynamic prices
    price : float


    def increase_amount(self) -> None:
        self.amount += 1
        if self.amount > 10:
            self.amount = 10

    def decrease_amount(self) -> None:
        self.amount -= 1
        if self.amount < 0:
            self.amount=0
