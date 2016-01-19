from tornado import gen
from tornado.web import Finish
import rethinkdb as rdb

from .handler import DefaultHandler


class UserHandler(DefaultHandler):

    def delete(self):
        # Get the user from the header and mark inactive
        raise Finish()

    @gen.coroutine
    def get(self):
        user_id = yield self.check_auth_for_user_id()
        user = yield rdb.table("users").get(user_id).run(self.db_conn)
        if user:
            self.set_status(200)
            self.write(user)
        else:
            # TODO: extract
            self.set_status(404)
            self.write({})
        raise Finish()

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
        resp = yield rdb.table("users").\
            update(user, durability='hard', return_changes=True).\
            run(self.db_conn)
        if resp.get('replaced', 0) == 1:
            self.set_status(200)
            self.write(resp.get('changes', {}).get('new_val', {}))
        else:
            # TODO: extract to a 500 error
            self.set_status(500)
            self.write({})
        raise Finish()
    
    def post(self):
        raise Finish()

    @gen.coroutine
    def put(self):
        # TODO: extract parts to generic update function
        user_id = yield self.check_auth_for_user_id()
        user = self.validate_json_for_user(self.request.body)
        resp = yield rdb.table("users").\
            update(user, durability='hard', return_changes=True).\
            run(self.db_conn)
        if resp.get('replaced', 0) == 1:
            self.set_status(200)
            self.write(resp.get('changes', {}).get('new_val', {}))
        else:
            # TODO: extract to a 500 error
            self.set_status(500)
            self.write({})
        raise Finish()
