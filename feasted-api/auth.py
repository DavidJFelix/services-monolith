import base64
from json import JSONDecodeError
from uuid import uuid4

import rethinkdb as rdb
from Crypto import Random
from tornado import gen
from tornado.escape import json_decode, utf8
from tornado.httpclient import AsyncHTTPClient
from tornado.web import Finish, HTTPError

from .handler import DefaultHandler
from .user import create_user


def pad_b64string(b64string):
    return b64string + b'=' * (4 - len(b64string) % 4)


@gen.coroutine
def create_google_oauth_claim(provider_uid, user_id, db_conn):
    resp = yield rdb.table("google_oauth_claim"). \
        insert(
            {"id": provider_uid, "user_id": user_id},
            durability='hard'). \
        run(db_conn)
    return resp


class GoogleAuthHandler(DefaultHandler):
    @gen.coroutine
    def get_google_certs(self):
        # TODO: move to config
        certs_uri = "https://www.googleapis.com/oauth2/v1/certs"
        http_client = AsyncHTTPClient()
        response = yield http_client.fetch(certs_uri)
        if response.code == 200:
            # TODO: this should check an on-disk to ensure it's up to date
            try:
                json_decode(response.body)
            except JSONDecodeError:
                raise HTTPError(500, reason="Google certificate was malformed")
        else:
            # FIXME: This should fallback to an on-disk
            raise HTTPError(503, reason="Could not reach Google certificate")

    @gen.coroutine
    def verify_auth(self):
        # TODO: move to config
        client_id = "531566137905-fhljh7kirg7v9kg4019qd6aaob57gd4s.apps.googleusercontent.com"
        google_cert = yield self.get_google_certs()
        token = utf8(self.request.body)
        # FIXME verify here
        return True

    @gen.coroutine
    def verify_for_uid(self):
        is_valid = yield self.verify_auth()
        if is_valid:
            return self.get_uid_from_jwt()
        else:
            raise HTTPError(401, reason="JWT Verification failed")

    def get_uid_from_jwt(self):
        jwt = utf8(self.request.body)

        # Extract the payload from the bytestring, then decode it to UTF string
        if jwt.count(b".") != 2:
            raise HTTPError(400, reason="Malformed JWT POST body")

        _, b64_payload, _ = jwt.split(b".")
        payload_b = base64.b64decode(pad_b64string(b64_payload))
        payload_s = payload_b.decode()

        # Attempt to parse UTF string as JSON
        try:
            payload_d = json_decode(payload_s)
        except JSONDecodeError:
            raise HTTPError(400, reason="Malformed JWT POST body")

        # Look for the uid in the JSON dictionary
        uid = payload_d.get("sub", None)
        if uid is not None:
            return uid
        else:
            raise HTTPError(400, reason="JWT did not have sub field")

    @gen.coroutine
    def get_user_id_for_uid(self, provider_uid):
        # Check for an existing claim
        claim = yield rdb.table("google_oauth_claims"). \
            get(provider_uid). \
            run(self.db_conn)

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
        user_id = uuid4()
        resp = yield create_user(user_id, self.db_conn)

        if resp.get("inserted", 0) != 1:
            raise HTTPError(500, "Could not create new user")

        resp = yield create_google_oauth_claim(provider_uid, user_id,
                                               self.db_conn)

        if resp.get("inserted", 0) != 1:
            raise HTTPError(500, "Could not create new claim")

        return user_id

    @gen.coroutine
    def post(self):
        provider_uid = yield self.verify_for_uid()
        user_id = yield self.get_user_id_for_uid(provider_uid)

        bearer_token = base64.b64encode(Random.get_random_bytes(256))
        resp = yield rdb.table("users"). \
            insert(
                {"id": user_id},
                durability='hard'). \
            run(self.db_conn)

        if resp.get("inserted", 0) != 1:
            raise HTTPError(500, "Could not create new user")

        resp = yield rdb.table("bearer_tokens"). \
            insert(
                {"id": bearer_token,
                 "user_id": user_id},
                durability='hard'). \
            run(self.db_conn)

        if resp.get("inserted", 0) != 1:
            raise HTTPError(500, "Could not create bearer token")

        token_container = {
            "type": "Bearer",
            "text": bearer_token,
        }
        self.set_status(200)
        self.write(token_container)
        raise Finish()


class FacebookAuthHandler(DefaultHandler):
    @gen.coroutine
    def post(self):
        pass
