from dataclasses import dataclass
from model.recipe import RecipeTypeDefinition
from model.building import BuildingTypeDefinition
from model.item import ItemDefinition

@dataclass(frozen=True)
class ConfigStore:
    items: dict[str, ItemDefinition]
    recipes: dict[str, RecipeTypeDefinition]
    building_types: dict[str, BuildingTypeDefinition]
