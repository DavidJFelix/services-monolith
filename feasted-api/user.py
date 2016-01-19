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
        

    def patch(self):
        raise Finish()
    
    
    def post(self):
        raise Finish()


    def put(self):
        raise Finish()
