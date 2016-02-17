#!/usr/bin/env python
import json

import rethinkdb as rdb
from tornado import gen
from tornado.web import Finish, HTTPError

@gen.coroutine
def get_ingredients(db_conn):
    ingredients = yield rdb.table('ingredients').order_by('ingredient').run(db_conn)
    print(ingredients)
    return ingredients


from .base import DefaultHandler

class IngredientsHandler(DefaultHandler):

    @gen.coroutine
    def get(self):
        db_conn = yield self.db_conn()
        ingredients = yield get_ingredients(db_conn)
        self.write(json.dumps(ingredients))
        self.set_status(200)
        raise Finish()
