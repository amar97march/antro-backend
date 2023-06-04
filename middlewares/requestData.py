import uuid
import json
from django.utils.deprecation import MiddlewareMixin

from users.models import RequestData
class RequestLogMiddleWare(MiddlewareMixin):
    # def __init__(self, get_response):
    #     self.get_response = get_response

    # def __call__(self, request):
    #     return self.get_response(request)
    # def __init__(self, get_response):
    #     self.get_response = get_response

    # def __call__(self, request):
    #     return self.get_response(request)
    #     WHITELISTED_URLS = [
    #         "/accounts/login/",
    #         "/your/custom/apis/urls",
    #     ]
    #     print(request.path)
    #     if request.path not in WHITELISTED_URLS:
    #         print(request.data)
    #         response = self.get_response(request)
    #         print(request.path)
    #         print(response)
    #         if request.user.is_authenticated and response:
    #             request_id = uuid.uuid4()
    #             print(request.path)
    #             RequestData.objects.create(request_id = request_id, data = response.data, user = request.user)

    #             # if isinstance(response, Response):
    #             #     response.data['detail'] = 'I have been edited'
    #             #     # you need to change private attribute `_is_render` 
    #             #     # to call render second time
    #             #     response._is_rendered = False 
    #             #     response.render()
    #             return {"request_id": request_id}
    #     else:
    #         return self.get_response(request)
        
    
    def process_response(self, request, response):
        print("sfag")
        response_data = json.loads(response.content)
        print(f"Response data: {response_data}")
        # return response
        WHITELISTED_URLS = [
            "/accounts/login/",
            "/your/custom/apis/urls",
        ]
        print(request.path, request.path not in WHITELISTED_URLS ,'data' in response_data, 'request_id' not in response_data)
        if request.path not in WHITELISTED_URLS and ('data' in response_data and 'request_id' not in response_data):
            # print(request.data)
            # response_data = self.get_response(request)
            print(request)
            print(response)
            if request.user.is_authenticated and response:
                request_id = uuid.uuid4()
                print(request.path)
                RequestData.objects.create(request_id = request_id, data = response_data, user = request.user)
                response.content = json.dumps({"request_id": str(request_id)})
                # if isinstance(response, Response):
                #     response.data['detail'] = 'I have been edited'
                #     # you need to change private attribute `_is_render` 
                #     # to call render second time
                #     response._is_rendered = False 
                #     response.render()
                return response
        else:
            return response