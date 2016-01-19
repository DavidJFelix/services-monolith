from tornado.web import Finish, RequestHandler


class DefaultHandler(RequestHandler):
    
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
