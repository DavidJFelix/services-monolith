from operator import xor
from typing import Optional, TypeVar

import rethinkdb as rdb
from tornado import gen

T = TypeVar('T')


class RethinkSingleMixin:
    rethink_table = None
    values = {}

    @gen.coroutine
    def delete(self, model_id, db_conn):
        resp = yield rdb.table(self.rethink_table). \
            get(model_id). \
            delete(durability='hard', return_changes='always'). \
            run(db_conn)
        if resp.get("deleted", 0) == 1:
            changes = resp.get("changes", [])
            old_model = changes[0].get("old_val", None) if len(changes) == 1 else None
            return self.from_rethink(old_model)
        else:
            return None

    @classmethod
    @gen.coroutine
    def from_get(cls: T, model_id, db_conn) -> T:
        model = yield rdb.table(cls.rethink_table).get(model_id).run(db_conn)
        return cls.from_rethink(model)

    @classmethod
    def from_rethink(cls: T, response) -> T:
        cls(**response)

    @gen.coroutine
    def insert(self, db_conn) -> Optional[T]:
        resp = yield rdb.table(self.rethink_table). \
            insert(
                self.values,
                durability='hard', return_changes='always'). \
            run(db_conn)

        if resp.get("inserted", 0) == 1:
            changes = resp.get('changes', [])
            new_model = changes[0].get('new_val', None) if len(changes) == 1 else None
            return self.from_rethink(new_model)
        else:
            return None

    @gen.coroutine
    def update(self, model_id, db_conn):
        resp = yield rdb.table(self.rethink_table). \
            get(model_id). \
            update(self.values, durability='hard', return_changes='always'). \
            run(db_conn)
        if xor((resp.get("replaced", 0) == 1), (resp.get("unchanged", 0) == 1)):
            changes = resp.get("changes", [])
            new_model = changes[0].get("new_val", None) if len(changes) == 1 else None
            return self.from_rethink(new_model)
        else:
            return None

    @gen.coroutine
    def upsert(self, db_conn):
        resp = yield rdb.table(self.rethink_table). \
            insert(
                self.values,
                durability='hard', return_changes='always', conflict='update'). \
            run(db_conn)

        if resp.get("inserted", 0) == 1:
            changes = resp.get('changes', [])
            new_model = changes[0].get('new_val', None) if len(changes) == 1 else None
            return self.from_rethink(new_model)
        else:
            return None


class RethinkCollectionMixin:
    def __init__(self, table_name):
        self.table_name = table_name

    @gen.coroutine
    def get_all(self, db_conn):
        pass


class RethinkLocationMixin:
    @classmethod
    def get_nearest(cls):
        pass
