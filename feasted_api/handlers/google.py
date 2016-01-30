import base64

from Crypto import Random
from tornado import gen
from tornado.escape import utf8
from tornado.httpclient import HTTPError
from tornado.web import Finish

from .base import DefaultHandler
from ..auth import (
    verify_for_provider_uid,
    get_user_id_for_uid,
    create_bearer_token
)


class GoogleAuthTokenHandler(DefaultHandler):
    @gen.coroutine
    def post(self):
        token = utf8(self.request.body)
        provider_uid = yield verify_for_provider_uid(token)
        conn = yield self.db_conn()
        user_id = yield get_user_id_for_uid(provider_uid, conn)

        # I had this at 256, but the maximum primary key size is 127 chars
        bearer_token = base64.b64encode(Random.get_random_bytes(64)).decode()
        resp = yield create_bearer_token(bearer_token, user_id, conn)

        if resp.get("inserted", 0) != 1:
            raise HTTPError(500, "Could not create bearer token")

        token_container = {
            "type": "Bearer",
            "data": bearer_token,
        }
        self.set_status(200)
        self.write(token_container)
        raise Finish()
