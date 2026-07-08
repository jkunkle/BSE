
from dataclasses import dataclass

@dataclass(frozen=True)
class RecipeTypeDefinition:
    id: str
    name: str
    inputs: Dict[str, int]
    outputs: Dict[str, int]
    duration : float



