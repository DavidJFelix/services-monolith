from tornado import gen
from tornado.escape import to_unicode
from tornado.web import Finish, HTTPError

from .base import BaseBearerAuthHandler
from ..models.bearer_token import get_bearer_token
from ..models.user import (
    get_user,
    make_user_inactive,
    parse_user_from_json,
    update_user,
)


class MeHandler(BaseBearerAuthHandler):
    @gen.coroutine
    def delete(self):
        user_id = yield self.check_auth_for_user_id()
        conn = yield self.db_conn()
        user = yield make_user_inactive(user_id, conn)
        if user:
            self.set_status(200)
            self.write(user)
            raise Finish()
        else:
            raise HTTPError(500, reason="Database could not delete record")

    @gen.coroutine
    def get(self):
        user_id = yield self.check_auth_for_user_id()
        conn = yield self.db_conn()
        user = yield get_user(user_id, conn)
        if user:
            self.set_status(200)
            self.write(user)
            raise Finish()
        else:
            raise HTTPError(404, reason="Could not find user")

    @gen.coroutine
    def patch(self):
        user_id = yield self.check_auth_for_user_id()
        conn = yield self.db_conn()
        body = to_unicode(self.request.body)
        user = parse_user_from_json(body)
        if user is None:
            raise HTTPError(400, reason="Invalid JSON")
        new_user = yield update_user(user_id, user, conn)
        if new_user:
            self.set_status(200)
            self.write(new_user)
            raise Finish()
        else:
            raise HTTPError(500, reason="Database could not update record")

    @gen.coroutine
    def put(self):
        user_id = yield self.check_auth_for_user_id()
        conn = yield self.db_conn()
        body = to_unicode(self.request.body)
        user = parse_user_from_json(body)
        if user is None:
            raise HTTPError(400, reason="Invalid JSON")
        new_user = yield update_user(user_id, user, conn)
        if new_user:
            self.set_status(200)
            self.write(new_user)
            raise Finish()
        else:
            raise HTTPError(500, reason="Database could not update record")

    @gen.coroutine
    def check_auth_for_user_id(self):
        token = self.get_bearer_token()
        conn = yield self.db_conn()
        bearer_token = yield get_bearer_token(token, conn)
        if bearer_token is None:
            raise HTTPError(401, reason="Bearer token is invalid")

        return bearer_token.user_id


class MeByTokenHandler(BaseBearerAuthHandler):
    pass


class UserHandler(BaseBearerAuthHandler):
    pass
