
from dataclasses import dataclass

@dataclass(frozen=True)
class ItemDefinition:

    key: str
    name: str
    price: float
    
