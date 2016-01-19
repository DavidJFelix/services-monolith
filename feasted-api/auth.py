from tornado.web import Finish

from .handler import DefaultHandler


class AuthHandler(DefaultHandler):
    def post(self):
        raise Finish()
