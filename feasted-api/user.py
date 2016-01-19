import json

import rethinkdb as rdb
from tornado import gen
from tornado.web import Finish, HTTPError

from .handler import DefaultHandler


class UserHandler(DefaultHandler):
    @staticmethod
    def validate_json_for_user(string):
        try:
            user = json.loads(string)
        except json.JSONDecodeError:
            raise HTTPError(400, reason="Invalid JSON")
        # FIXME: validate the user here
        return user

    @gen.coroutine
    def delete(self):
        user_id = yield self.check_auth_for_user_id()
        resp = yield rdb.table("users"). \
            get(user_id). \
            update(
                {"is_active": False},
                durability='hard',
                return_changes=True). \
            run(self.db_conn)
        if resp.get('replaced', 0) == 1:
            self.set_status(200)
            self.write(resp.get('changes', {}).get('new_val', {}))
            raise Finish()
        else:
            raise HTTPError(500, reason="Database could not delete record")

    @gen.coroutine
    def get(self):
        user_id = yield self.check_auth_for_user_id()
        user = yield rdb.table("users").get(user_id).run(self.db_conn)
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
        # TODO: extract parts to generic update function
        user_id = yield self.check_auth_for_user_id()
        user = self.validate_json_for_user(self.request.body)
        resp = yield rdb.table("users"). \
            get(user_id). \
            update(user, durability='hard', return_changes=True). \
            run(self.db_conn)
        if resp.get('replaced', 0) == 1:
            self.set_status(200)
            self.write(resp.get('changes', {}).get('new_val', {}))
            raise Finish()
        else:
            raise HTTPError(500, reason="Database could not update record")

    def post(self):
        raise Finish()

    @gen.coroutine
    def put(self):
        # TODO: extract parts to generic update function
        user_id = yield self.check_auth_for_user_id()
        user = self.validate_json_for_user(self.request.body)
        resp = yield rdb.table("users"). \
            get(user_id). \
            update(user, durability='hard', return_changes=True). \
            run(self.db_conn)
        if resp.get('replaced', 0) == 1:
            self.set_status(200)
            self.write(resp.get('changes', {}).get('new_val', {}))
            raise Finish()
        else:
            raise HTTPError(500, reason="Database could not update record")

    @gen.coroutine
    def check_auth_for_user_id(self):
        # FIXME: find a better place to do this whole function
        # FIXME: this bearer string parse could be clearer
        token = self.request.headers.get('authorization', None). \
            lstrip('bearer'). \
            strip()
        user_id = yield rdb.table("bearer_tokens"). \
            get(token). \
            run(self.db_conn)
        if user_id:
            return user_id
        else:
            raise HTTPError(401, reason="Bearer token is invalid")


class UserByTokenHandler(DefaultHandler):
    pass
