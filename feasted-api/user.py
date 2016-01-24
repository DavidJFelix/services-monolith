import json

import rethinkdb as rdb
from tornado import gen
from tornado.escape import to_unicode
from tornado.web import Finish, HTTPError

from .handler import DefaultHandler


@gen.coroutine
def create_user(user_id, db_conn):
    resp = yield rdb.table("users"). \
        insert(
            {"id": user_id, "is_active": False},
            durability='hard'). \
        run(db_conn)
    return resp


@gen.coroutine
def update_user(user_id, user, db_conn):
    resp = yield rdb.table("users"). \
        get(user_id). \
        update(user, durability='hard', return_changes=True). \
        run(db_conn)
    return resp


@gen.coroutine
def delete_user(user_id, db_conn):
    resp = yield update_user(user_id, {"is_active": False}, db_conn)
    return resp


class UserHandler(DefaultHandler):
    @staticmethod
    def validate_json_for_user(string):
        try:
            user = json.loads(string)
        except json.JSONDecodeError:
            raise HTTPError(400, reason="Invalid JSON")
        # FIXME: validate the user here
        return user

    def confirm_update_and_finish(self, update_response):
        if update_response.get('replaced', 0) == 1:
            self.set_status(200)
            self.write(update_response.get('changes', {}).get('new_val', {}))
            raise Finish()
        else:
            raise HTTPError(500, reason="Database could not update record")

    @gen.coroutine
    def delete(self):
        user_id = yield self.check_auth_for_user_id()
        conn = yield self.db_conn()
        resp = yield delete_user(user_id, conn)
        if resp.get('replaced', 0) == 1:
            self.set_status(200)
            self.write(resp.get('changes', {}).get('new_val', {}))
            raise Finish()
        else:
            raise HTTPError(500, reason="Database could not delete record")

    @gen.coroutine
    def get(self):
        user_id = yield self.check_auth_for_user_id()
        conn = yield self.db_conn()
        user = yield rdb.table("users").get(user_id).run(conn)
        if user:
            self.set_status(200)
            self.write(user)
            raise Finish()
        else:
            raise HTTPError(404, reason="Could not find user")

    def head(self):
        # TODO: extract get and implement head from extracted
        raise Finish()

    def options(self):
        raise Finish()

    @gen.coroutine
    def patch(self):
        user_id = yield self.check_auth_for_user_id()
        user = self.validate_json_for_user(self.request.body)
        resp = yield update_user(user_id, user, self.db_conn)
        self.confirm_update_and_finish(resp)

    def post(self):
        raise Finish()

    @gen.coroutine
    def put(self):
        user_id = yield self.check_auth_for_user_id()
        conn = yield self.db_conn()
        user = self.validate_json_for_user(self.request.body)
        resp = yield update_user(user_id, user, conn)
        self.confirm_update_and_finish(resp)

    @gen.coroutine
    def check_auth_for_user_id(self):
        # FIXME: find a better place to do this whole function
        # FIXME: this bearer string parse could be clearer
        token = self.request.headers.get('authorization', None). \
            lstrip('bearer'). \
            strip()
        token = to_unicode(token)
        conn = yield self.db_conn()
        user_id = yield rdb.table("bearer_tokens"). \
            get(token). \
            run(conn)
        if user_id:
            return user_id
        else:
            raise HTTPError(401, reason="Bearer token is invalid")


class UserByTokenHandler(DefaultHandler):
    pass
