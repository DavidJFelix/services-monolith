from collections import namedtuple

import rethinkdb as rdb
from tornado import gen

Meal = namedtuple('Meal', [
    'meal_id',
    'name',
    'description',
    'portions',
    'price',
    'location',
    'availableFrom',
    'availableTo',
    'ingredients',
    'allergens',
    'imageUrl',
    'isActive',
])

Location = namedtuple('Location', [
    'type',
    'coordinates',
])


@gen.coroutine
def get_meals(ll, radius, max_results, db_conn):
    meals_nearby = yield rdb.table('meals').get_nearest(ll, index='location', max_dist=radius,
                                                        max_results=max_results).run(db_conn)
    return {
        "meals": meals_nearby
    }


@gen.coroutine
def delete_meal(meal_id, db_conn):
    is_updated = yield rdb.table('meals').get(meal_id).update({'isActive': False}).run(db_conn)
    return is_updated


@gen.coroutine
def update_meal(meal_id, meal, db_conn):
    updated_meal = yield rdb.table('meals').get(meal_id).update(meal).run(db_conn)
    return updated_meal


@gen.coroutine
def add_meal(meal, db_conn):
    added_meal = yield rdb.table('meals').insert(meal).run(db_conn)
    return added_meal
