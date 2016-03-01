from collections import namedtuple
from typing import Optional, Dict, List

import rethinkdb as rdb
from tornado import gen

Ingredient = namedtuple('Ingredient', [
    'ingredient_id',
    'name',
])

IngredientContainer = namedtuple('IngredientContainer', [
    'ingredients',
])


def parse_rdb_ingredient(dictionary: Optional[Dict]) -> Optional[Ingredient]:
    # FIXME: this boilerplate needs to go away
    if dictionary is None:
        return None
    else:
        ingredient_id = dictionary.get('ingredient_id')
        name = dictionary.get('name')
        if ingredient_id and name:
            return Ingredient(ingredient_id, name)
        else:
            return None


def parse_rdb_ingredient_container(ingredient_list: Optional[List[Dict]]) -> IngredientContainer:
    safe_ingredient_list = list(ingredient_list)
    ingredients = []

    for ingredient in safe_ingredient_list:
        ingredients.append(parse_rdb_ingredient(ingredient))

    return IngredientContainer(ingredients)


@gen.coroutine
def get_ingredients(db_conn) -> Optional[Ingredient]:
    ingredients = yield rdb.table('ingredients').order_by('ingredient').run(db_conn)
    return parse_rdb_ingredient_container(ingredients)


class IngredientCollection:
    pass

class Ingredient:
    pass
