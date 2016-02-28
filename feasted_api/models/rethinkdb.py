from operator import xor
from typing import Optional, TypeVar

import rethinkdb as rdb
from tornado import gen

from .base import BaseModel

T = TypeVar('T')


class RDBModel(BaseModel):
    def __init__(self, table_name, **kwargs):
        self.table_name = table_name
        super().__init__(**kwargs)

    @gen.coroutine
    def delete(self, model_id, db_conn):
        resp = yield rdb.table(self.table_name). \
            get(model_id). \
            delete(durability='hard', return_changes='always'). \
            run(db_conn)
        if resp.get("deleted", 0) == 1:
            changes = resp.get("changes", [])
            old_model = changes[0].get("old_val", None) if len(changes) == 1 else None
            return self.from_rdb_response(old_model)
        else:
            return None

    @staticmethod
    @gen.coroutine
    def get(cls, table_name, model_id, db_conn):
        model = yield rdb.table(table_name).get(model_id).run(db_conn)
        return cls.from_rdb_response(cls, model)

    @classmethod
    def from_rdb_response(cls: T, response):
        raise NotImplementedError()

    @gen.coroutine
    def insert(self, db_conn) -> Optional[T]:
        resp = yield rdb.table(self.table_name). \
            insert(
                dict(self),
                durability='hard', return_changes='always'). \
            run(db_conn)

        if resp.get("inserted", 0) == 1:
            changes = resp.get('changes', [])
            new_model = changes[0].get('new_val', None) if len(changes) == 1 else None
            return self.from_rdb_response(new_model)
        else:
            return None

    @gen.coroutine
    def update(self, model_id, db_conn):
        resp = yield rdb.table("users"). \
            get(model_id). \
            update(dict(self), durability='hard', return_changes='always'). \
            run(db_conn)
        if xor((resp.get("replaced", 0) == 1), (resp.get("unchanged", 0) == 1)):
            changes = resp.get("changes", [])
            new_model = changes[0].get("new_val", None) if len(changes) == 1 else None
            return self.from_rdb_response(new_model)
        else:
            return None

    @gen.coroutine
    def upsert(self, db_conn):
        resp = yield rdb.table(self.table_name). \
            insert(
                dict(self),
                durability='hard', return_changes='always', conflict='update'). \
            run(db_conn)

        if resp.get("inserted", 0) == 1:
            changes = resp.get('changes', [])
            new_model = changes[0].get('new_val', None) if len(changes) == 1 else None
            return self.from_rdb_response(new_model)
        else:
            return None


class RDBTableMixin:
    def __init__(self, table_name):
        self.table_name = table_name

    @gen.coroutine
    def get_all(self, db_conn):
        pass
