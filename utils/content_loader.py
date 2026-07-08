import json
from pathlib import Path
from types import MappingProxyType

from model.recipe import RecipeTypeDefinition
from model.building import BuildingTypeDefinition
from model.config_store import ConfigStore


def read_json_file(path: str) -> dict:

    opath = Path(path)

    if not opath.exists():
        raise FileNotFoundError(f'Content file not found: {path}')

    with opath.open('r', encoding='utf-8') as file:
        return json.load(file)


def freeze_mapping(data: dict[str, int]) -> MappingProxyType:
    '''
    Creates a read-only view of a dictionary.

    This prevents accidental modification like:
        recipe.inputs['wood'] = 999
    '''
    return MappingProxyType(dict(data))

def load_config(building_types_path: str, recipes_path: str):

    recipes = load_recipes(recipes_path)
    validate_recipes(recipes)

    building_types = load_building_types(building_types_path)

    validate_building_types(recipes, building_types)

    return ConfigStore(recipes, building_types)

def load_recipes(path: str) -> dict[str, RecipeTypeDefinition]:
    raw_data = read_json_file(path)

    if 'recipes' not in raw_data:
        raise ValueError(f'{path} must contain top-level key "recipes"')

    recipes: dict[str, RecipeTypeDefinition] = {}

    for recipe_key, recipe_data in raw_data['recipes'].items():
        recipes[recipe_key] = RecipeTypeDefinition(
            id=recipe_key,
            name=recipe_data['name'],
            inputs=freeze_mapping(recipe_data.get('inputs', {})),
            outputs=freeze_mapping(recipe_data.get('outputs', {})),
            duration=float(recipe_data['duration']),
        )

    return recipes


def load_building_types(path: Path) -> dict[str, BuildingTypeDefinition]:
    raw_data = read_json_file(path)

    if 'building_types' not in raw_data:
        raise ValueError(f'{path} must contain top-level key "building_types"')

    building_types: dict[str, BuildingTypeDefinition] = {}

    for building_type_key, building_data in raw_data['building_types'].items():
        size = building_data['size']

        if len(size) != 2:
            raise ValueError(
                f'Building type {building_type_key} must have size [x, y]'
            )


        building_types[building_type_key] = BuildingTypeDefinition(
            key=building_type_key,
            name=building_data['name'],
            x_size=int(size[0]),
            y_size=int(size[1]),
            capabilities=frozenset(building_data.get('capabilities', [])),
            workers=building_data.get('workers', 0),
            recipe_keys=tuple(building_data.get('recipes', [])),
            storage_limits=freeze_mapping(building_data.get('storage', {})),
        )

    return building_types


def validate_recipes(
    recipes: dict[str, RecipeTypeDefinition],
) -> None:
    for recipe_key, recipe in recipes.items():
        if recipe.duration <= 0:
            raise ValueError(f'Recipe "{recipe_key}" must have positive duration')

        for item_id, amount in recipe.inputs.items():
            if amount <= 0:
                raise ValueError(
                    f'Recipe {recipe_key} has non-positive input amount for {item_id}'
                )

        for item_id, amount in recipe.outputs.items():
            if amount <= 0:
                raise ValueError(
                    f'Recipe {recipe_key} has non-positive output amount for {item_id}'
                )


def validate_building_types(
    recipes: dict[str, RecipeTypeDefinition],
    building_types: dict[str, BuildingTypeDefinition],
) -> None:
    for building_type_id, building_type in building_types.items():
        if building_type.x_size <= 0 or building_type.y_size <= 0:
            raise ValueError(
                f'Building type {building_type_id} must have positive x_size and y_size'
            )

        for recipe_key in building_type.recipe_keys:
            if recipe_key not in recipes:
                raise ValueError(
                    f'Building type {building_type_id} references unknown recipe {recipe_key}'
                )

