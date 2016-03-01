from operator import xor
from typing import Optional, List

import rethinkdb as rdb
from tornado import gen

from ..models.base import BaseModel


@gen.coroutine
def from_delete(cls: BaseModel, model_id, db_conn) -> Optional[BaseModel]:
    resp = yield rdb.table(cls.table). \
        get(model_id). \
        delete(durability='hard', return_changes='always'). \
        run(db_conn)
    if resp.get("deleted", 0) == 1:
        changes = resp.get("changes", [])
        old_model = changes[0].get("old_val", None) if len(changes) == 1 else None
        return from_rethink(cls, old_model)
    else:
        return None


@gen.coroutine
def from_get(cls: BaseModel, model_id, db_conn) -> Optional[BaseModel]:
    resp = yield rdb.table(cls.table).get(model_id).run(db_conn)
    if resp:
        return from_rethink(cls, resp)
    else:
        return None


@gen.coroutine
def from_get_nearest(cls: BaseModel, db_conn, lng_lat=(-84.51, 39.10), max_dist=10,
                     units='mi', max_results=20) -> List[BaseModel]:
    resp = yield rdb.table(cls.table). \
        get_nearest(rdb.point(*lng_lat), max_dist=max_dist,
                    units=units, max_results=max_results). \
        run(db_conn)
    if len(resp) > 0:
        models = []
        for item in resp:
            doc = item.get('doc')
            if doc:
                models.append(from_rethink(cls, doc))
    else:
        return []


def from_rethink(cls: BaseModel, response) -> BaseModel:
    return cls.__init__(**response)


@gen.coroutine
def insert(model: BaseModel, db_conn) -> Optional[BaseModel]:
    resp = yield rdb.table(model.table). \
        insert(
            model.to_serializable(),
            durability='hard', return_changes='always'). \
        run(db_conn)

    if resp.get("inserted", 0) == 1:
        changes = resp.get('changes', [])
        new_model = changes[0].get('new_val', None) if len(changes) == 1 else None
        return from_rethink(model.__class__, new_model)
    else:
        return None


@gen.coroutine
def update(model: BaseModel, db_conn) -> Optional[BaseModel]:
    resp = yield rdb.table(model.table). \
        get(model.model_id). \
        update(model.to_serializable(), durability='hard', return_changes='always'). \
        run(db_conn)
    if xor((resp.get("replaced", 0) == 1), (resp.get("unchanged", 0) == 1)):
        changes = resp.get("changes", [])
        new_model = changes[0].get("new_val", None) if len(changes) == 1 else None
        return from_rethink(model.__class__, new_model)
    else:
        return None


@gen.coroutine
def upsert(model: BaseModel, db_conn) -> Optional[BaseModel]:
    resp = yield rdb.table(model.table). \
        insert(
            model.values,
            durability='hard', return_changes='always', conflict='update'). \
        run(db_conn)

    if resp.get("inserted", 0) == 1:
        changes = resp.get('changes', [])
        new_model = changes[0].get('new_val', None) if len(changes) == 1 else None
        return from_rethink(model.__class__, new_model)
    else:
        return None
