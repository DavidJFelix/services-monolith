from operator import xor
from typing import Optional, List, Dict, Tuple

import rethinkdb as rdb
from tornado import gen

from ..models.base import BaseModel


@gen.coroutine
def delete(table: str, model_id, db_conn) -> Optional[Dict]:
    resp = yield rdb.table(table). \
        get(model_id). \
        delete(durability='hard', return_changes='always'). \
        run(db_conn)
    if resp.get("deleted", 0) == 1:
        changes = resp.get("changes", [])
        return changes[0].get("old_val", None) if len(changes) == 1 else None
    else:
        return None


@gen.coroutine
def get(cls: BaseModel, model_id, db_conn) -> Optional[Dict]:
    resp = yield rdb.table(cls.table).get(model_id).run(db_conn)
    return resp if resp else None


@gen.coroutine
def get_nearest(table: str,
                db_conn,
                lng_lat: Tuple[float] = (-84.51, 39.10),
                max_dist: int = 10,
                units: str = 'mi',
                max_results: int = 20) -> List[Dict]:
    resp = yield rdb.table(table). \
        get_nearest(rdb.point(*lng_lat),
                    max_dist=max_dist,
                    units=units,
                    max_results=max_results). \
        run(db_conn)
    if len(resp) > 0:
        models = []
        for item in resp:
            doc = item.get('doc')
            if doc:
                models.append(doc)
    else:
        return []


@gen.coroutine
def insert(model: BaseModel, db_conn) -> Optional[Dict]:
    resp = yield rdb.table(model.table). \
        insert(
            model.to_serializable(),
            durability='hard', return_changes='always'). \
        run(db_conn)

    if resp.get("inserted", 0) == 1:
        changes = resp.get('changes', [])
        return changes[0].get('new_val', None) if len(changes) == 1 else None
    else:
        return None


@gen.coroutine
def update(model: BaseModel, db_conn) -> Optional[Dict]:
    resp = yield rdb.table(model.table). \
        get(model.model_id). \
        update(model.to_serializable(), durability='hard', return_changes='always'). \
        run(db_conn)
    if xor((resp.get("replaced", 0) == 1), (resp.get("unchanged", 0) == 1)):
        changes = resp.get("changes", [])
        return changes[0].get("new_val", None) if len(changes) == 1 else None
    else:
        return None


@gen.coroutine
def upsert(model: BaseModel, db_conn) -> Optional[Dict]:
    resp = yield rdb.table(model.table). \
        insert(
            model.values,
            durability='hard', return_changes='always', conflict='update'). \
        run(db_conn)

    if resp.get("inserted", 0) == 1:
        changes = resp.get('changes', [])
        return changes[0].get('new_val', None) if len(changes) == 1 else None
    else:
        return None
