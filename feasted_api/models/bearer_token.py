import base64
from collections import namedtuple
from typing import Optional, Dict

import rethinkdb as rdb
from Crypto import Random
from tornado import gen
from tornado.escape import to_unicode

BearerToken = namedtuple('BearerToken', [
    'token',
    'user_id',
])


def parse_rdb_bearer_token(dictionary: Optional[Dict]) -> Optional[BearerToken]:
    if dictionary is None:
        return None
    else:
        token = dictionary.get('id')
        user_id = dictionary.get('user_id')
        if token and user_id:
            return BearerToken(token, user_id)
        else:
            return None


@gen.coroutine
def create_bearer_token(token, user_id, db_conn) -> Optional[BearerToken]:
    resp = yield rdb.table('bearer_tokens'). \
        insert({'id': token, 'user_id': user_id},
               durability='hard', return_changes='always'). \
        run(db_conn)
    if resp.get('inserted', 0) == 1:
        changes = resp.get('changes', [])
        new_token = changes[0].get('new_val', None) if len(changes) == 1 else None
        return parse_rdb_bearer_token(new_token)
    else:
        return None


@gen.coroutine
def delete_bearer_token(token, db_conn) -> Optional[BearerToken]:
    resp = yield rdb.table('bearer_tokens'). \
        get(token). \
        delete(durability='hard', return_changes='always'). \
        run(db_conn)
    if resp.get('deleted', 0) == 1:
        changes = resp.get('changes', [])
        old_token = changes[0].get('old_val', None) if len(changes) == 1 else None
        return parse_rdb_bearer_token(old_token)
    else:
        return None


@gen.coroutine
def get_bearer_token(token, db_conn) -> Optional[BearerToken]:
    bearer_token = yield rdb.table('bearer_tokens'). \
        get(token). \
        run(db_conn)
    return parse_rdb_bearer_token(bearer_token)


def generate_bearer_token() -> str:
    return to_unicode(base64.b64encode(Random.get_random_bytes(64)))
