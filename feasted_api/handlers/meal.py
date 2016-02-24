#!/usr/bin/env python
import json

import rethinkdb as rdb
from tornado import gen
from tornado.web import Finish, HTTPError

from .base import DefaultHandler
from ..models.meal import get_meals, add_meal, delete_meal, update_meal


class MealHandler(DefaultHandler):
    @gen.coroutine
    def get(self, meal_id=None):
        # Get query params for lat/lng
        lat_param = self.get_query_argument("lat", default=None)
        lng_param = self.get_query_argument("lng", default=None)
        if not (lat_param and lng_param):
            lat = 39.10
            lng = -84.51
        else:
            try:
                lat = float(lat_param)
                lng = float(lng_param)
            except ValueError:
                raise HTTPError(400, reason="lat and lng should be numbers")

        lng_lat = rdb.point(lng, lat)

        # Get query param for range
        radius_param = self.get_query_argument("radius", default="5")
        try:
            radius = int(radius_param)
        except ValueError:
            raise HTTPError(400, reason="radius should be an integer")

        # Get query param for limit
        limit_param = self.get_query_argument("max_results", default="20")
        try:
            limit = int(limit_param)
            if limit < 1:
                raise ValueError
        except ValueError:
            raise HTTPError(400, reason="limit must be an integer greater than 0")

        # Make request to database
        db_conn = yield self.db_conn()
        meals_nearby = yield get_meals(lng_lat, radius, limit, db_conn)
        if meals_nearby:
            self.set_status(200)
            self.write(meals_nearby)
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
