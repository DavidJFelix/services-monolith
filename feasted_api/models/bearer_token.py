from collections import namedtuple
from typing import Optional, Dict

import rethinkdb as rdb
from tornado import gen

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
        new_token = resp.get('changes', {}).get('new_val', None)
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
        old_token = resp.get('changes', {}).get('old_val', None)
        return parse_rdb_bearer_token(old_token)
    else:
        return None


@gen.coroutine
def get_bearer_token(token, db_conn) -> Optional[BearerToken]:
    bearer_token = yield rdb.table('bearer_tokens'). \
        get(token). \
        run(db_conn)
    return parse_rdb_bearer_token(bearer_token)
