

class LogMiddleware:
    def __init__(self,get_response):
        self.get_response = get_response

    def __call__(self,req):
        print("Request Method: " + req.method+" " + req.path)

        resp = self.get_response(req)
        return resp