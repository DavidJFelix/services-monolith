from tornado.web import Finish, RequestHandler


class DefaultHandler(RequestHandler):
    def data_received(self, chunk):
        # This is just here to satisfy pycharm
        super().data_received(chunk)

    def write_error(self, status_code, **kwargs):
        self.set_status(status_code)
        self.write({
            "error": status_code,
            "details": kwargs.get("reason", "")
        })

    @property
    def db_conn(self):
        return self.application.db_conn

    def delete(self, *args, **kwargs):
        self.set_status(405)
        raise Finish()

    def get(self, *args, **kwargs):
        self.set_status(405)
        raise Finish()

    def head(self, *args, **kwargs):
        self.set_status(405)
        raise Finish()

    def options(self, *args, **kwargs):
        self.set_status(405)
        raise Finish()

    def patch(self, *args, **kwargs):
        self.set_status(405)
        raise Finish()

    def post(self, *args, **kwargs):
        self.set_status(405)
        raise Finish()

    def put(self, *args, **kwargs):
        self.set_status(405)
        raise Finish()
