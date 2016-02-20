#!/usr/bin/env python
import json

import rethinkdb as rdb
from tornado import gen
from tornado.web import Finish

from .base import DefaultHandler


@gen.coroutine
def get_allergens(db_conn):
    try:
        allergens = yield rdb.table('allergenss').order_by('allergen').run(db_conn)
        return allergens
    except rdb.ReqlRuntimeError:
        print('error reading from table')
        return "[]"


class AllergenHandler(DefaultHandler):
    @gen.coroutine
    def get(self):
        db_conn = yield self.db_conn()
        allergens = yield get_allergens(db_conn)
        self.write(json.dumps(allergens))
        self.set_status(200)
        raise Finish()
