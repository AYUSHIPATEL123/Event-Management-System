class ModelMiddleWare:
    def __init__(self,get_response):
        self.get_response = get_response

    def __call__(self,request):
        print("first middleware start")
        response = self.get_response(request)
        print("first middleware end")
        return response    

def Model2MiddleWare(get_response):
    def middleware(request):
        print("second middleware")
        response = get_response(request)
        print("second middleware end")
        return response
    return middleware