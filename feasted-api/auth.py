import base64
from uuid import uuid4

import rethinkdb as rdb
from Crypto import Random
from tornado import gen
from tornado.web import Finish, HTTPError

from .handler import DefaultHandler


class GoogleAuthHandler(DefaultHandler):
    @gen.coroutine
    def post(self):
        # FIXME: verify and check for existing user
        user_id = uuid4()
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
