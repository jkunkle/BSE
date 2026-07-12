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

