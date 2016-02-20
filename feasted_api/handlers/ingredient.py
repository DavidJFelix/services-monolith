#!/usr/bin/env python
import json

import rethinkdb as rdb
from tornado import gen
from tornado.web import Finish

from .base import DefaultHandler


@gen.coroutine
def get_ingredients(db_conn):
    try:
        ingredients = yield rdb.table('ingredients').order_by('ingredient').run(db_conn)
        return ingredients
    except rdb.RqlRuntimeError:
        print('error reading from table')
        return "[]"


class IngredientHandler(DefaultHandler):
    @gen.coroutine
    def get(self):
        db_conn = yield self.db_conn()
        ingredients = yield get_ingredients(db_conn)
        self.write(json.dumps(ingredients))
        self.set_status(200)
        raise Finish()
