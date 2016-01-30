from tornado import gen
from tornado.httpclient import HTTPError

from .base import DefaultHandler


class FacebookAuthHandler(DefaultHandler):
    @gen.coroutine
    def post(self):
        raise HTTPError(501, "Not yet implemented")
