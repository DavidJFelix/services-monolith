#!/usr/bin/env python
from tornado.ioloop import IOLoop
from tornado.web import Application

from .api import APIHandler
from .user import UserHandler
from .address import AddressHandler
from .auth import AuthHandler
from .diag import HealthHandler, InfoHandler


class FeastedAPIApplication(Application):
    
    def __init__(self):
        routes = [
            (r'/', APIHandler),
            (r'/health', HealthHandler),
            (r'/info', InfoHandler),
            (r'/user', UserHandler),
            (r'/user/by-token', UserByTokenHandler),
            (r'/address', AddressHandler),
            (r'/auth/token-auth', AuthHandler),
        ]
        settings = {
        }
        # FIXME: this should change for python3 (lower verbosity)... I think
        super(Application, self).__init__(routes, **settings)
        # TODO: setup db here

def main():
    application = FeastedAPIApplication(routes)
    application.listen(5000)
    IOLoop.configure('tornado.platform.asyncio.AsyncIOLoop')
    IOLoop.current().start()


if __name__ == "__main__":
    main()
