import json
from collections import namedtuple
from typing import Optional

import rethinkdb as rdb
from tornado import gen

from feasted_api.models.rethinkdb import RDBTableMixin
from .base import CollectionModel
from .rethinkdb import RDBModel

Meal = namedtuple('Meal', [
    'meal_id',
    'name',
    'description',
    'portions',
    'price',
    'location',
    'available_from',
    'available_to',
    'ingredients',
    'allergens',
    'image_url',
    'is_active',
])

Location = namedtuple('Location', [
    'type',
    'coordinates',
])


# Not yet being used. Ignore
class Meal2(RDBModel):
    required_fields = frozenset([
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
        'image_url',
        'is_active',
    ])

    @staticmethod
    def from_rdb_response(cls, resp):
        # FIXME: actually build the dictionary
        resp_dict = {}
        cls(**resp_dict)

    @staticmethod
    @gen.coroutine
    def from_get(meal_id, db_conn):
        meal = yield RDBModel.get(Meal2, 'meals', meal_id, db_conn)
        return meal


# Not yet being used. Ignore
class MealCollection(CollectionModel, RDBTableMixin):
    required_fields = frozenset([
        'meals',
    ])
    collection_of = Meal2


def parse_meal_from_json(string):
    try:
        meal = json.loads(string)
    except json.JSONDecodeError:
        return None
    return meal


@gen.coroutine
def get_meals(ll, radius, max_results, db_conn):
    meals_nearby = yield rdb.table('meals').get_nearest(ll, index='location', max_dist=radius,
                                                        max_results=max_results,
                                                        unit='mi').run(db_conn)
    # FIXME: getttoooo powers activate
    meals = []
    for meal_obj in meals_nearby:
        meal = Meal(
                meal_id=meal_obj['doc']['meal_id'],
                name=meal_obj['doc']['name'],
                description=meal_obj['doc']['description'],
                portions=meal_obj['doc']['portions'],
                price=meal_obj['doc']['price'],
                available_from=meal_obj['doc']['available_from'],
                available_to=meal_obj['doc']['available_to'],
                ingredients=meal_obj['doc']['ingredients'],
                allergens=meal_obj['doc']['allergens'],
                image_url=meal_obj['doc']['image_url'],
                is_active=meal_obj['doc']['is_active'],
                location=Location(
                        type=meal_obj['doc']['location']['type'],
                        coordinates={
                            "lng": meal_obj['doc']['location']['coordinates'][0],
                            "lat": meal_obj['doc']['location']['coordinates'][1]
                        }
                )._asdict())
        meals.append(meal._asdict())
    return {
        "meals": meals
    }


@gen.coroutine
def get_meal(meal_id, db_conn):
    pass


@gen.coroutine
def delete_meal(meal_id, db_conn):
    is_updated = yield rdb.table('meals').get(meal_id).update({'isActive': False}).run(db_conn)
    return is_updated


@gen.coroutine
def update_meal(meal_id, meal, db_conn):
    updated_meal = yield rdb.table('meals').get(meal_id).update(meal).run(db_conn)
    return updated_meal


@gen.coroutine
def create_meal(meal, db_conn):
    added_meal = yield rdb.table('meals').insert(meal).run(db_conn)
    return added_meal


@gen.coroutine
def create_meal(meal, db_conn) -> Optional[Meal]:
    resp = yield rdb.table('meal'). \
        insert(
            dict(meal),
            durability='hard', return_changes='always'). \
        run(db_conn)
    if resp.get("inserted", 0) == 1:
        changes = resp.get('changes', [])
        new_meal = changes[0].get('new_val', None) if len(changes) == 1 else None
        return parse_rdb_meal(new_meal)
    else:
        return None
