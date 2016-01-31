#!/usr/bin/env python
import uuid
from datetime import datetime

import rethinkdb as rdb
from tornado import gen
from tornado.ioloop import IOLoop
from tornado.web import Application

from .handlers import (
    AddressHandler,
    APIHandler,
    FacebookAuthHandler,
    GoogleAuthTokenHandler,
    HealthHandler,
    InfoHandler,
    MeByTokenHandler,
    MeHandler,
    UserHandler,
    MealsHandler,
)


class FeastedAPIApplication(Application):
    def __init__(self):
        routes = [
            (r'/', APIHandler),
            (r'/health', HealthHandler),
            (r'/info', InfoHandler),
            (r'/me', MeHandler),
            (r'/me/by-token', MeByTokenHandler),
            (r'/users', UserHandler),
            (r'/users/(?P<user_id>[^\/]+)', UserHandler),
            (r'/addresses', AddressHandler),
            (r'/addresses/(?P<address_id>[^\/]+)', AddressHandler),
            (r'/auth/google/jwt-auth', GoogleAuthTokenHandler),
            (r'/auth/facebook/token-auth', FacebookAuthHandler),
            (r'/meals', MealsHandler),
        ]
        settings = {
        }
        super().__init__(handlers=routes, **settings)
        self.server_id = uuid.uuid4()
        self.start_time = datetime.utcnow()
        self.client_id = "531566137905-fhljh7kirg7v9kg4019qd6aaob57gd4s.apps.googleusercontent.com"
        rdb.set_loop_type("tornado")

    @gen.coroutine
    def db_conn(self):
        # Tornado Future returned below
        conn = yield rdb.connect(host='10.0.0.94', port=28015, db='feasted')
        return conn


def main():
    application = FeastedAPIApplication()
    application.listen(5000)
    IOLoop.configure('tornado.platform.asyncio.AsyncIOLoop')
    IOLoop.current().start()


if __name__ == "__main__":
    main()
