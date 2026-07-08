from dataclasses import dataclass
from model.recipe import RecipeTypeDefinition
from model.building import BuildingTypeDefinition

@dataclass(frozen=True)
class ConfigStore:
    recipes: dict[str, RecipeTypeDefinition]
    building_types: dict[str, BuildingTypeDefinition]
