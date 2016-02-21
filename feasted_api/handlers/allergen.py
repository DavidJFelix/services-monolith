#!/usr/bin/env python
import json

from tornado import gen
from tornado.web import Finish

from .base import DefaultHandler
from ..models.allergen import get_allergens


class AllergenHandler(DefaultHandler):
    @gen.coroutine
    def get(self):
        db_conn = yield self.db_conn()
        allergens = yield get_allergens(db_conn)
        self.write(json.dumps(allergens))
        self.set_status(200)
        raise Finish()
