from collections import namedtuple

import rethinkdb as rdb
from tornado import gen

Ingredient = namedtuple('Ingredient', [
    'ingredient_id',
    'name',
])


@gen.coroutine
def get_ingredients(db_conn):
    try:
        ingredients = yield rdb.table('ingredients').order_by('ingredient').run(db_conn)
        return ingredients
    except rdb.RqlRuntimeError:
        print('error reading from table')
        return "[]"
