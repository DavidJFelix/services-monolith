from collections import namedtuple
from typing import Optional, Dict
from uuid import uuid4

import rethinkdb as rdb
from tornado import gen

from ..models.user import create_user

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
def create_google_oauth_claim(provider_uid, user_id: str, db_conn) -> Optional[GoogleOauthClaim]:
    resp = yield rdb.table('google_oauth_claims'). \
        insert(
            {"id": provider_uid, "user_id": user_id},
            durability='hard', return_changes='always'). \
        run(db_conn)
    if resp.get('inserted', 0) == 1:
        changes = resp.get('changes', [])
        new_claim = changes[0].get('new_val', None) if len(changes) == 1 else None
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
        changes = resp.get('changes', [])
        old_claim = changes[0].get('old_val', None) if len(changes) == 1 else None
        return parse_rdb_google_oauth_claim(old_claim)
    else:
        return None


@gen.coroutine
def get_google_oauth_claim(provider_uid, db_conn) -> Optional[GoogleOauthClaim]:
    resp = yield rdb.table('google_oauth_claims'). \
        get(provider_uid). \
        run(db_conn)
    return parse_rdb_google_oauth_claim(resp)


@gen.coroutine
def get_or_create_user_id_from_uid(provider_uid, db_conn) -> Optional[GoogleOauthClaim]:
    # Check for an existing claim
    claim = yield get_google_oauth_claim(provider_uid, db_conn)

    # Return the user_id if the claim has it
    if claim is not None:
        return claim.user_id

    # TODO: condense db round trips here
    # When there's no claim, form one around a new user
    user_id = str(uuid4())
    did_insert = yield create_user(user_id, db_conn)

    if not did_insert:
        return None

    claim = yield create_google_oauth_claim(provider_uid, user_id, db_conn)

    if claim is None:
        return None

    return claim.user_id
