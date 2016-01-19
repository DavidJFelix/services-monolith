#!/usr/bin/env python
from tornado.ioloop import IOLoop
from tornado.web import Application

from .api import APIHandler
from .user import UserHandler
from .address import AddressHandler
from .auth import AuthHandler
from .diag import HealthHandler, InfoHandler


def main():
    routes = [
        (r'/', APIHandler),
        (r'/health', HealthHandler),
        (r'/info', InfoHandler),
        (r'/user', UserHandler),
        (r'/user/by-token', UserByTokenHandler),
        (r'/address', AddressHandler),
        (r'/auth/token-auth', AuthHandler),
    ]
    application = Application(routes)
    application.listen(5000)
    IOLoop.configure('tornado.platform.asyncio.AsyncIOLoop')
    IOLoop.current().start()


if __name__ == "__main__":
    main()
