from tornado.web import Finish

from .handler import DefaultHandler


class AddressHandler(DefaultHandler):
    def delete(self, address_id=None):
        # Get the user from the header and mark inactive
        raise Finish()

    def get(self, address_id=None):
        # Get the user from header and handle
        raise Finish()

    def head(self, address_id=None):
        raise Finish()

    def options(self, address_id=None):
        raise Finish()

    def patch(self, address_id=None):
        raise Finish()

    def post(self, address_id=None):
        raise Finish()

    def put(self, address_id=None):
        raise Finish()
