from tornado.web import Finish
from tornado.escape import json_encode

from .handler import DefaultHandler


class HealthHandler(DefaultHandler):
    def get_health(self):
        return {
            "status": "UP",
            "upSince": self.application.start_time.isoformat('T') + 'Z',
            "serverId": str(self.application.server_id),
        }

    def get(self):
        self.set_status(200)
        self.write(self.get_health())
        raise Finish()

    def head(self):
        self.set_status(204)
        self.set_header('content-length', len(json_encode(self.get_health())))
        raise Finish()

    def options(self):
        self.set_status(204)
        self.set_header('accept', 'GET, HEAD, OPTIONS')
        self.set_header('content-length', 0)
        raise Finish()


class InfoHandler(DefaultHandler):
    def get(self):
        raise Finish()

    def head(self):
        raise Finish()

    def options(self):
        raise Finish()
