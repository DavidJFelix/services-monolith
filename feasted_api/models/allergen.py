from tornado import gen
from ..lib.rethinkdb import (
    get_all_and_order_by
)

@gen.coroutine
def get_allergens(db_conn):
    allergens = yield get_all_and_order_by('allergens', 'name', db_conn)
    return {'allergens':allergens}

class AllergenCollection:
    pass
