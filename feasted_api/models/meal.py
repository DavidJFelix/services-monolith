from typing import Dict, Optional

from tornado import gen

from .base import BaseModel
from ..lib.rethinkdb import get


class Meal(BaseModel):
    fields = (
        'meal_id',
        'name',
        'description',
        'portions',
        'portions_available',
        'price',
        'location',
        'available_from',
        'available_to',
        'ingredients',
        'allergens',
        'preview_image_url',
        'images',
        'is_active',
    )
    table = 'meals'
    id_field = 'meal_id'

    def __init__(self, **field_values):
        # Handle a few of these fields specially
        new_field_values = field_values

        # Remove ugly rethink location properties
        location = new_field_values.pop('location', {})
        location.pop('$reql_type$', None)
        if location:
            self.values['location'] = location

        # call original constructor for the rest
        super().__init__(**new_field_values)


def from_rethink(response: Dict):
    return Meal(**response)


@gen.coroutine
def from_get(meal_id, db_conn) -> Optional[Meal]:
    resp = yield get(Meal.table, meal_id, db_conn)
    if resp:
        return from_rethink(resp)
    else:
        return None


@gen.coroutine
def from_get_nearest(lng_lat, db):
    pass

@gen.coroutine
def insert():
    pass