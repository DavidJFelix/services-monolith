from tornado.web import Finish

from .handler import DefaultHandler


class UserHandler(DefaultHandler):

    def delete(self):
        # Get the user from the header and mark inactive
        raise Finish()

    
    def get(self):
        # Get the user from header and handle
        raise Finish()


    def head(self):
        raise Finish()


    def options(self):
        raise Finish()
        

    def patch(self):
        raise Finish()
    
    
    def post(self):
        raise Finish()


    def put(self):
        raise Finish()
