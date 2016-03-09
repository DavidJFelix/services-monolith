import json

from tornado import gen
from tornado.web import Finish

from .base import DefaultHandler
from ..models.allergen import get_allergens


class AllergensHandler(DefaultHandler):
    @gen.coroutine
    def get(self, allergen_id=None):
        db_conn = yield self.db_conn()
        allergens = yield get_allergens(db_conn)
        self.write(allergens)
        self.set_status(200)
        raise Finish()


class AllergenHandler(DefaultHandler):
    pass
