from dataclasses import dataclass

@dataclass()
class BillItem:

    name : str
    amount : int
    price : float
    note : str | None = None

    def get_total(self):
        return self.price*self.amount


