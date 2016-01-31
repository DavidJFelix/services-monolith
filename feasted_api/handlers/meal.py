#!/usr/bin/env python
from tornado import gen
from tornado.web import Finish, HTTPError
import json
from .base import DefaultHandler
import rethinkdb as rdb


@gen.coroutine
def get_meals(ll, radius, db_conn):
    meals_nearby = yield rdb.table('meals').get_nearest(ll, index = 'location', max_dist = radius).run(db_conn)
    return meals_nearby

@gen.coroutine
def delete_meal(meal_id, db_conn):
    is_updated = yield rdb.table('meals').get(meal_id).update({"isActive": False}).run(db_conn)
    return is_updated

@gen.coroutine
def update_meal(meal_id,meal, db_conn):
    updated_meal = yield rdb.table('meals').get(meal_id).update(meal).run(db_conn)
    return updated_meal

@gen.coroutine
def add_meal(meal, db_conn):
    added_meal = yield rdb.table("meals").insert(meal).run(db_conn)
    return added_meal



class MealsHandler(DefaultHandler):
    @staticmethod
    def validate_json_for_meal(string):
        try:
            meal = json.loads(string)
        except json.JSONDecodeError:
            raise HTTPError(400, reason="Invalid JSON")
        return meal

    @gen.coroutine
    def get(self):
        long_lat_array = self.get_query_argument("ll").split(',')
        lat = float(long_lat_array[0])
        long = float(long_lat_array[1])
        ll = rdb.point(lat, long)
        radius = int(self.get_query_argument("radius"))
        db_conn = yield self.db_conn()

        if ll:
            meals_nearby = yield get_meals(ll, radius, db_conn)
            self.set_status(200)
            self.write(json.dumps(meals_nearby))
            raise Finish()
        else:
            raise HTTPError(404, reason="Could not find find meals nearby")

    @gen.coroutine
    def post(self):
        meal = json.loads(self.request.body.decode('utf-8'))
        long_lat_array = meal['location'].split(',')
        meal['location'] = rdb.point(float(long_lat_array[0]), float(long_lat_array[1]))
        db_conn = yield self.db_conn()
        yield add_meal(meal, db_conn)
        self.set_status(200)
        raise Finish()

    @gen.coroutine
    def delete(self):
        meal_id = self.get_query_argument("meal_id")
        db_conn = yield self.db_conn()
        yield delete_meal(meal_id, db_conn)
        self.set_status(200)
        raise Finish()


    def put(self):
        meal_id = self.get_query_argument("meal_id")
        meal = self.get_query_argument("body")
        db_conn = yield self.db_conn()
        yield update_meal(meal_id,meal, db_conn)
        self.set_status(200)
        raise Finish()