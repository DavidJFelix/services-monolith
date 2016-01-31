from collections import namedtuple
from typing import Optional, Dict

import rethinkdb as rdb
from tornado import gen

GoogleOauthClaim = namedtuple('GoogleOauthClaim', [
    'provider_uid',
    'user_id',
])


def parse_rdb_google_oauth_claim(dictionary: Optional[Dict]) -> Optional[GoogleOauthClaim]:
    if dictionary is None:
        return None
    else:
        provider_uid = dictionary.get('id')
        user_id = dictionary.get('user_id')
        if provider_uid and user_id:
            return GoogleOauthClaim(provider_uid, user_id)
        else:
            return None


@gen.coroutine
def create_google_oauth_claim(provider_uid, user_id, db_conn) -> Optional[GoogleOauthClaim]:
    resp = yield rdb.table('google_oauth_claims'). \
        insert(
            {"id": provider_uid, "user_id": user_id},
            durability='hard', return_changes='always'). \
        run(db_conn)
    if resp.get('inserted', 0) == 1:
        new_claim = resp.get('changes', {}).get('new_val', None)
        return parse_rdb_google_oauth_claim(new_claim)
    else:
        return None


@gen.coroutine
def delete_google_oauth_claim(provider_uid, db_conn) -> Optional[GoogleOauthClaim]:
    resp = yield rdb.table('google_oauth_claims'). \
        get(provider_uid). \
        delete(durability='hard', return_changes='always'). \
        run(db_conn)
    if resp.get('deleted', 0) == 1:
        old_claim = resp.get('changes', {}).get('old_val', None)
        return parse_rdb_google_oauth_claim(old_claim)
    else:
        return None


@gen.coroutine
def get_google_oauth_claim(provider_uid, db_conn) -> Optional[GoogleOauthClaim]:
    resp = yield rdb.table('google_oauth_claims'). \
        get(provider_uid). \
        run(db_conn)
    return parse_rdb_google_oauth_claim(resp)
