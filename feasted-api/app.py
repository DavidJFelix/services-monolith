#!/usr/bin/env python
from tornado.ioloop import IOLoop
from tornado.web import Application


def main():
    routes = [
        (r'/', APIHandler),
        (r'/cards', CardHandler),
    ]
    application = Application(routes)
    application.listen(5000)
    IOLoop.configure('tornado.platform.asyncio.AsyncIOLoop')
    IOLoop.current().start()


if __name__ == "__main__":
    main()
