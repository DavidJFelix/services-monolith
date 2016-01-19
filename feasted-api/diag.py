from tornado.web import Finish

from .handler import DefaultHandler


class InfoHandler(DefaultHandler):

    def get(self):
        # Get the user from header and handle
        raise Finish()


    def head(self):
        raise Finish()


    def options(self):
        raise Finish()
        


class HealthHandler(DefaultHandler):

    def get(self):
        # Get the user from header and handle
        raise Finish()


    def head(self):
        raise Finish()


    def options(self):
        raise Finish()

