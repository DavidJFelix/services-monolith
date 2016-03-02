from tornado import gen
from tornado.escape import to_unicode
from tornado.web import Finish, HTTPError

from .base import DefaultHandler
from ..models.meal import Meal, from_get, from_get_nearest, from_insert


class MealsHandler(DefaultHandler):
    @gen.coroutine
    def get(self):
        # Get query params for lat/lng
        lat_param = self.get_query_argument("lat", default=None)
        lng_param = self.get_query_argument("lng", default=None)
        if not (lat_param and lng_param):
            # Cincinnati -- extract some time
            lat = 39.10
            lng = -84.51
        else:
            try:
                lat = float(lat_param)
                lng = float(lng_param)
            except ValueError:
                raise HTTPError(400, reason="lat and lng should be numbers")

        lng_lat = (lng, lat)

        # Get query param for range
        radius_param = self.get_query_argument("radius", default="10")
        try:
            radius = int(radius_param)
        except ValueError:
            raise HTTPError(400, reason="radius should be an integer")

        # Get query param for limit
        limit_param = self.get_query_argument("limit", default="20")
        try:
            limit = int(limit_param)
            if limit < 1:
                raise ValueError
        except ValueError:
            raise HTTPError(400, reason="limit must be an integer greater than 0")

        # Get query param for page
        page_param = self.get_query_argument("page", default="1")
        try:
            page = int(page_param)
            if page < 1:
                raise ValueError
        except ValueError:
            raise HTTPError(400, reason="page must be an integer greater than 0")

        # Make request to database
        db_conn = yield self.db_conn()
        meals_nearby = yield from_get_nearest(db_conn,
                                              lng_lat=lng_lat,
                                              max_dist=radius,
                                              max_results=limit)
        if meals_nearby:
            self.set_status(200)
            self.write({"meals": [meal.values for meal in meals_nearby]})
            raise Finish()
        else:
            raise HTTPError(404, reason="could not find find meals nearby")

    @gen.coroutine
    def post(self):
        db_conn = yield self.db_conn()

        # Validate POSTed JSON
        body = to_unicode(self.request.body)
        meal = Meal.from_json(body)
        if meal is None:
            # FIXME: validate here!
            raise HTTPError(400, reason="malformed meal object")

        # Write to the database
        new_meal = yield from_insert(meal, db_conn)
        if new_meal:
            self.set_status(201)
            self.write(meal.values)
            raise Finish()
        else:
            raise HTTPError(500, reason="could not write meal to database")


class MealHandler(DefaultHandler):
    @gen.coroutine
    def get(self, meal_id):
        db_conn = yield self.db_conn()
        meal = yield from_get(meal_id, db_conn)
        if meal:
            self.set_status(200)
            self.write(meal.values)
            raise Finish
        else:
            raise HTTPError(404, reason="could not find meal")
