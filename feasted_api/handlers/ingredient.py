#!/usr/bin/env python
import json

from tornado import gen
from tornado.web import Finish, HTTPError

from .base import DefaultHandler
from ..models.ingredient import get_ingredients


class IngredientHandler(DefaultHandler):
    @gen.coroutine
    def get(self, ingredient_id=None):
        db_conn = yield self.db_conn()
        if ingredient_id:
            raise HTTPError(405, reason="Cannot GET on single ingredient id")
        else:
            ingredients = yield get_ingredients(db_conn)
            self.write(json.dumps(ingredients))
            self.set_status(200)
            raise Finish()
