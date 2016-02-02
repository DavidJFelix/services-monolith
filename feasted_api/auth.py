from uuid import uuid4

from tornado import gen
from tornado.web import HTTPError

from .models.google_oauth_claim import create_google_oauth_claim, get_google_oauth_claim
from .models.user import create_user


@gen.coroutine
def get_user_id_for_uid(provider_uid, db_conn):
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
        raise HTTPError(500, "Could not create new user")

    claim = yield create_google_oauth_claim(provider_uid, user_id, db_conn)

    if claim is None:
        raise HTTPError(500, "Could not create new claim")

    return user_id
