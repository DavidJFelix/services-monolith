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