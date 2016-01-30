import base64
import binascii
from json import JSONDecodeError
from uuid import uuid4

import rethinkdb as rdb
from tornado import gen
from tornado.escape import json_decode, utf8
from tornado.httpclient import AsyncHTTPClient
from tornado.web import HTTPError
from .models.user import create_user


def pad_b64string(b64string):
    return b64string + b'=' * (4 - len(b64string) % 4)


@gen.coroutine
def create_google_oauth_claim(provider_uid, user_id, db_conn):
    resp = yield rdb.table("google_oauth_claims"). \
        insert(
            {"id": provider_uid, "user_id": user_id},
            durability='hard'). \
        run(db_conn)
    return resp


@gen.coroutine
def create_bearer_token(bearer_token, user_id, db_conn):
    resp = yield rdb.table("bearer_tokens"). \
        insert(
            {"id": bearer_token, "user_id": user_id},
            durability='hard'). \
        run(db_conn)
    return resp


@gen.coroutine
def get_google_certs(certs_uri="https://www.googleapis.com/oauth2/v1/certs"):
    http_client = AsyncHTTPClient()
    response = yield http_client.fetch(certs_uri)
    if response.code == 200:
        try:
            json_decode(response.body)
        except JSONDecodeError:
            raise HTTPError(500, reason="Google certificate was malformed")
        else:
            raise HTTPError(503, reason="Could not reach Google certificate")


def get_uid_from_jwt(token):
    jwt = utf8(token)

    # Attempt to parse UTF string as JSON
    try:
        _, b64_payload, _ = jwt.split(b".")
        payload_b = base64.b64decode(pad_b64string(b64_payload))
        payload_s = payload_b.decode()

        payload_d = json_decode(payload_s)
    except (JSONDecodeError, binascii.Error, ValueError):
        raise HTTPError(400, reason="Malformed JWT POST body")

    # Look for the uid in the JSON dictionary
    uid = payload_d.get("sub", None)
    if uid is not None:
        return uid
    else:
        raise HTTPError(400, reason="JWT did not have sub field")


@gen.coroutine
def verify_google_auth(token):
    google_cert = yield get_google_certs()
    # FIXME verify here
    return True


@gen.coroutine
def verify_for_provider_uid(token):
    is_valid = yield verify_google_auth(token)
    if is_valid:
        return get_uid_from_jwt(token)
    else:
        raise HTTPError(401, reason="JWT Verification failed")


@gen.coroutine
def get_user_id_for_uid(provider_uid, db_conn):
    # Check for an existing claim
    claim = yield rdb.table("google_oauth_claims"). \
        get(provider_uid). \
        run(db_conn)

    # Return the user_id if the claim has it
    if claim is not None:
        user_id = claim.get("user_id", None)
        if user_id is not None:
            return user_id
        else:
            raise HTTPError(500,
                            "Database claim had no associated user id")

    # TODO: condense db round trips here
    # When there's no claim, form one around a new user
    user_id = str(uuid4())
    did_insert = yield create_user(user_id, db_conn)

    if not did_insert:
        raise HTTPError(500, "Could not create new user")

    resp = yield create_google_oauth_claim(provider_uid, user_id, db_conn)

    if resp.get("inserted", 0) != 1:
        raise HTTPError(500, "Could not create new claim")

    return user_id






