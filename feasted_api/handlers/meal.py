#!/usr/bin/env python
from tornado import gen
from tornado.web import Finish, HTTPError
import json
from .base import DefaultHandler
import rethinkdb as rdb


@gen.coroutine
def get_meals(ll, radius, max_results, db_conn):
    meals_nearby = yield rdb.table('meals').get_nearest(ll, index = 'location', max_dist = radius,
                                                        max_results = max_results).run(db_conn)
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
        lat = float(self.get_query_argument("lat"))
        lng = float(self.get_query_argument("lng"))
        lng_lat = rdb.point(lng, lat)
        radius = int(self.get_query_argument("radius"))
        max_results = int(self.get_query_argument("max_results", 20))
        if max_results <= 0:
            max_results=20

        db_conn = yield self.db_conn()

        if lng_lat:
            meals_nearby = yield get_meals(lng_lat, radius, max_results, db_conn)
            self.set_status(200)
            self.write(json.dumps(meals_nearby))
            raise Finish()
        else:
            raise HTTPError(404, reason="Could not find find meals nearby")

    @gen.coroutine
    def post(self):
        meal = json.loads(self.request.body.decode('utf-8'))
        lat = float(meal['lat'])
        lng = float(meal['lng'])
        meal['location'] = rdb.point(lng, lat)
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