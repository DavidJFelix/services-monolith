from typing import Optional

from tornado import gen
from tornado.escape import to_unicode
from tornado.web import RequestHandler, HTTPError


class DefaultHandler(RequestHandler):
    def data_received(self, chunk):
        # This is just here to satisfy pycharm
        super().data_received(chunk)

    def write_error(self, status_code, **kwargs):
        reason = kwargs.get("reason", "")

        if 'exc_info' in kwargs:
            exception = kwargs['exc_info'][1]
            if isinstance(exception, HTTPError) and exception.reason:
                reason = exception.reason

        self.write({
            "error": status_code,
            "details": reason
        })

    @gen.coroutine
    def db_conn(self):
        conn = yield self.application.db_conn()
        return conn

    def delete(self, *args, **kwargs):
        raise HTTPError(405, reason="Method not allowed.")

    def get(self, *args, **kwargs):
        raise HTTPError(405, reason="Method not allowed.")

    def head(self, *args, **kwargs):
        raise HTTPError(405, reason="Method not allowed.")

    def options(self, *args, **kwargs):
        raise HTTPError(405, reason="Method not allowed.")

    def patch(self, *args, **kwargs):
        raise HTTPError(405, reason="Method not allowed.")

    def post(self, *args, **kwargs):
        raise HTTPError(405, reason="Method not allowed.")

    def put(self, *args, **kwargs):
        raise HTTPError(405, reason="Method not allowed.")


class BaseBearerAuthHandler(DefaultHandler):
    def get_bearer_token(self) -> Optional[str]:
        auth_header = self.request.headers.get('authorization', None)
        if auth_header:
            token = auth_header.lstrip('Bbearer').strip()
            token = to_unicode(token)
            return token
        else:
            return None
