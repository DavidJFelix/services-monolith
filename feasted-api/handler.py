from tornado.web import Finish, RequestHandler


class DefaultHandler(RequestHandler):
    
    def delete(self, *args, **kwargs):
        self.set_status(405)
        raise Finish()


    def get(self, *args, **kwargs):
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
