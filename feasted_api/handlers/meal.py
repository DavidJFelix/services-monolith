#!/usr/bin/env python
import json

import rethinkdb as rdb
from tornado import gen
from tornado.web import Finish, HTTPError

from .base import DefaultHandler
from ..models.meal import get_meals, add_meal, delete_meal, update_meal


class MealHandler(DefaultHandler):
    @staticmethod
    def validate_json_for_meal(string):
        try:
            meal = json.loads(string)
        except json.JSONDecodeError:
            raise HTTPError(400, reason="Invalid JSON")
        return meal

    @gen.coroutine
    def get(self, meal_id=None):
        lat = float(self.get_query_argument("lat"))
        lng = float(self.get_query_argument("lng"))
        lng_lat = rdb.point(lng, lat)
        radius = int(self.get_query_argument("radius"))
        max_results = int(self.get_query_argument("max_results", 20))
        if max_results <= 0:
            max_results = 20

        db_conn = yield self.db_conn()

        if lng_lat:
            meals_nearby = yield get_meals(lng_lat, radius, max_results, db_conn)
            self.set_status(200)
            self.write(json.dumps(meals_nearby))
            raise Finish()
        else:
            raise HTTPError(404, reason="Could not find find meals nearby")

    @gen.coroutine
    def post(self, meal_id=None):
        meal = json.loads(self.request.body.decode('utf-8'))
        lat = float(meal['lat'])
        lng = float(meal['lng'])
        meal['location'] = rdb.point(lng, lat)
        db_conn = yield self.db_conn()
        yield add_meal(meal, db_conn)
        self.set_status(200)
        raise Finish()

    @gen.coroutine
    def delete(self, meal_id=None):
        meal_id = self.get_query_argument("meal_id")
        db_conn = yield self.db_conn()
        yield delete_meal(meal_id, db_conn)
        self.set_status(200)
        raise Finish()

    @gen.coroutine
    def put(self, meal_id=None):
        meal_id = self.get_query_argument("meal_id")
        meal = self.get_query_argument("body")
        db_conn = yield self.db_conn()
        yield update_meal(meal_id, meal, db_conn)
        self.set_status(200)
        raise Finish()
