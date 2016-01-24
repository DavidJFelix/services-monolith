#!/usr/bin/env python
import uuid
from datetime import datetime

import rethinkdb as rdb
from tornado import gen
from tornado.ioloop import IOLoop
from tornado.web import Application

from .address import AddressHandler
from .api import APIHandler
from .auth import FacebookAuthHandler, GoogleAuthHandler
from .diag import HealthHandler, InfoHandler
from .user import UserHandler, UserByTokenHandler


class FeastedAPIApplication(Application):
    def __init__(self):
        routes = [
            (r'/', APIHandler),
            (r'/health', HealthHandler),
            (r'/info', InfoHandler),
            (r'/user', UserHandler),
            (r'/user/by-token', UserByTokenHandler),
            (r'/address', AddressHandler),
            (r'/auth/google/jwt-auth', GoogleAuthHandler),
            (r'/auth/facebook/token-auth', FacebookAuthHandler),
        ]
        settings = {
        }
        super().__init__(handlers=routes, **settings)
        self.server_id = uuid.uuid4()
        self.start_time = datetime.utcnow()
        rdb.set_loop_type("tornado")

    @gen.coroutine
    def db_conn(self):
        # Tornado Future returned below
        conn = yield rdb.connect(host='localhost', port=28015, db='feasted')
        return conn


def main():
    application = FeastedAPIApplication()
    application.listen(5000)
    IOLoop.configure('tornado.platform.asyncio.AsyncIOLoop')
    IOLoop.current().start()


if __name__ == "__main__":
    main()
