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
                                                        max_results=max_results,
                                                        unit='mi').run(db_conn)
    # FIXME: getttoooo powers activate
    meals = []
    for meal_obj in meals_nearby:
        meal = Meal(
                meal_id=meal_obj['doc']['id'],
                name=meal_obj['doc']['name'],
                description=meal_obj['doc']['description'],
                portions=meal_obj['doc']['portions'],
                price=meal_obj['doc']['price'],
                availableFrom=meal_obj['doc']['availableFrom'],
                availableTo=meal_obj['doc']['availableTo'],
                ingredients=meal_obj['doc']['ingredients'],
                allergens=meal_obj['doc']['allergens'],
                imageUrl=meal_obj['doc']['image_url'],
                isActive=meal_obj['doc']['isActive'],
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
