from collections import namedtuple

import rethinkdb as rdb
from tornado import gen

Allergen = namedtuple('Allergen', [
    'allergen_id',
    'user_id',
    'name',
])


@gen.coroutine
def get_allergens(db_conn):
    try:
        allergens = yield rdb.table('allergens').order_by('allergen').run(db_conn)
        return allergens
    except rdb.ReqlRuntimeError:
        print('error reading from table')
        return "[]"


class AllergenCollection:
    pass
