from collections import namedtuple

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
    table_name = 'meals'
    required_fields = frozenset([
        'name',
        'description',
        'portions',
        # 'portions_available', # Uncomment me when the data is fixed
        'price',
        'location',
        'available_from',
        'available_to',
        'ingredients',
        'allergens',
        'image_url',
        'is_active',
    ])
    optional_fields = frozenset([
        'meal_id',
    ])

    @classmethod
    def from_rdb_response(cls, resp):
        # FIXME: actually build the dictionary
        resp_dict = {}
        return cls(**resp_dict)

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
