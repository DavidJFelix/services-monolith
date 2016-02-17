#!/usr/bin/env python
import json

import rethinkdb as rdb
from tornado import gen
from tornado.web import Finish, HTTPError

@gen.coroutine
def get_allergens(db_conn):
    allergens = yield rdb.table('allergens').order_by('allergen').run(db_conn)
    return allergens


from .base import DefaultHandler

class AllergenHandler(DefaultHandler):

    @gen.coroutine
    def get(self):
        db_conn = yield self.db_conn()
        allergens = yield get_allergens(db_conn)
        self.write(json.dumps(allergens))
        self.set_status(200)
        raise Finish()
