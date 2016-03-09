import json

from tornado import gen
from tornado.web import Finish, HTTPError

from .base import DefaultHandler
from ..models.ingredient import get_ingredients


class IngredientsHandler(DefaultHandler):
    @gen.coroutine
    def get(self, ingredient_id=None):
        db_conn = yield self.db_conn()
        ingredients = yield get_ingredients(db_conn)
        self.write(ingredients)
        self.set_status(200)
        raise Finish()


class IngredientHandler(DefaultHandler):
    pass
