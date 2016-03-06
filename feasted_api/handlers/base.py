from typing import Optional

from tornado import gen
from tornado.escape import to_unicode
from tornado.web import RequestHandler, HTTPError


class DefaultHandler(RequestHandler):
    """ DefaultHandler is a base handler that all of our handlers will inherit from.

    It sets up our desired error format, and a default policy for method response when handlers
    are hit with a method that they do not support.
    """

    def data_received(self, chunk):
        # This is just here to satisfy pycharm
        super().data_received(chunk)

    def write_error(self, status_code, **kwargs):
        reason = kwargs.get("reason", "")

        if 'exc_info' in kwargs:
            exception = kwargs['exc_info'][1]
            if isinstance(exception, HTTPError) and exception.reason:
                reason = exception.reason
            else:
                reason = "unexpected runtime exception"

        self.write({
            "error": status_code,
            "details": reason
        })

    def set_default_headers(self):
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Methods',
                        'DELETE, GET, HEAD, OPTIONS, PATCH, POST, PUT')
        request_headers = self.request.headers.get('Access-Control-Request-Headers', '')
        self.set_header('Access-Control-Allow-Headers', request_headers)

    @gen.coroutine
    def db_conn(self):
        conn = yield self.application.db_conn()
        return conn

    @gen.coroutine
    def delete(self, *args, **kwargs):
        raise HTTPError(405, reason="method not allowed")

    @gen.coroutine
    def get(self, *args, **kwargs):
        raise HTTPError(405, reason="method not allowed")

    @gen.coroutine
    def head(self, *args, **kwargs):
        raise HTTPError(405, reason="method not allowed")

    # FIXME: return default to a 405. For now, lie to bypasss CORS
    @gen.coroutine
    def options(self, *args, **kwargs):
        # raise HTTPError(405, reason="method not allowed")
        # LIE LIE LIE
        self.set_header("Allow", "DELETE, GET, HEAD, OPTIONS, PATCH, POST, PUT")

    @gen.coroutine
    def patch(self, *args, **kwargs):
        raise HTTPError(405, reason="method not allowed")

    @gen.coroutine
    def post(self, *args, **kwargs):
        raise HTTPError(405, reason="method not allowed")

    @gen.coroutine
    def put(self, *args, **kwargs):
        raise HTTPError(405, reason="method not allowed")


class BaseBearerAuthHandler(DefaultHandler):
    """BaseBearerAuthHandler is an extension of Default handler which is used when a handler needs
    to tie into the auth system.

    It provides utility functions to work with and validate auth headers and tokens.
    """
    def get_bearer_token(self) -> Optional[str]:
        auth_header = self.request.headers.get('authorization', None)
        if auth_header:
            token = auth_header.lstrip('Bbearer').strip()
            token = to_unicode(token)
            return token
        else:
            return None
