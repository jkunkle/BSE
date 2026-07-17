import json
from pathlib import Path
from types import MappingProxyType

from model.recipe import RecipeTypeDefinition
from model.building import BuildingTypeDefinition
from model.item import ItemDefinition
from model.worker import WorkerType, NeedType
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

def load_config(building_types_path: str, recipes_path: str, items_path: str, worker_types_path:str ):

    items = load_items(items_path)
    recipes = load_recipes(recipes_path)
    validate_recipes(recipes, items)

    building_types = load_building_types(building_types_path)

    validate_building_types(recipes, building_types, items)

    worker_types = load_worker_types(worker_types_path)

    return ConfigStore(items, recipes, building_types, worker_types)

def load_worker_types(path: str) -> dict[str, WorkerType]:
    raw_data = read_json_file(path)
    print (raw_data)

    if 'worker_types' not in raw_data:
        raise ValueError(f'{path} must contain top-level key "worker_types"')


    wtypes: dict[str, WorkerType] = {}

    for worker_key, worker_data in raw_data['worker_types'].items():
        need_rates = parse_need_rates(
            worker_data.get("need_rates", {})
        )

        wtypes[worker_key] = WorkerType(
            key=worker_key,
            name=worker_data['name'],
            price=worker_data['price'],
            need_rates=freeze_mapping(need_rates),
        )

    return wtypes


def parse_need_type(value: str) -> NeedType:
    try:
        return NeedType(value)
    except ValueError as error:
        valid_values = ", ".join(need_type.value for need_type in NeedType)
        raise ValueError(
            f"Unknown need type {value!r}. Valid values are: {valid_values}"
        ) from error

def parse_need_rates(raw_need_rates: dict[str, float]) -> dict[NeedType, float]:
    return {
        parse_need_type(need_type_key): float(rate)
        for need_type_key, rate in raw_need_rates.items()
    }
def load_items(path: str) -> dict[str, ItemDefinition]:
    raw_data = read_json_file(path)

    if 'items' not in raw_data:
        raise ValueError(f'{path} must contain top-level key "items"')

    items: dict[str, ItemDefinition] = {}

    for item_key, item_data in raw_data['items'].items():
        items[item_key] = ItemDefinition(
            key=item_key,
            name=item_data['name'],
            price=item_data['price'],
        )

    return items

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
            doors = building_data.get('doors', None),
            cost = building_data['cost'],
            workers=building_data.get('workers', 0),
            recipe_keys=tuple(building_data.get('recipes', [])),
            storage_limits=freeze_mapping(building_data.get('storage', {})),
            color=building_data.get('color', []),
            key_code=building_data['key_code']
        )

    return building_types


def validate_recipes(
    recipes: dict[str, RecipeTypeDefinition],
    items: dict[str, ItemDefinition],
) -> None:
    for recipe_key, recipe in recipes.items():
        if recipe.duration <= 0:
            raise ValueError(f'Recipe "{recipe_key}" must have positive duration')

        for item_id, amount in recipe.inputs.items():
            if item_id not in items:
                raise ValueError(
                    f'Recipe {recipe_key} inputs references a non-exisiting item : {item_id}'
                )


            if amount <= 0:
                raise ValueError(
                    f'Recipe {recipe_key} has non-positive input amount for {item_id}'
                )

        for item_id, amount in recipe.outputs.items():
            if item_id not in items:
                raise ValueError(
                    f'Recipe {recipe_key} outputs references a non-exisiting item : {item_id}'
                )
            if amount <= 0:
                raise ValueError(
                    f'Recipe {recipe_key} has non-positive output amount for {item_id}'
                )


def validate_building_types(
    recipes: dict[str, RecipeTypeDefinition],
    building_types: dict[str, BuildingTypeDefinition],
    items: dict[str, ItemDefinition],
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

        for item_key in list(building_type.storage_limits.keys()):
            if item_key not in items:
                raise ValueError(
                    f'Building type {building_type_id} storage references unknown item {item_key}'
                )
