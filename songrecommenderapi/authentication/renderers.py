from email import charset
from rest_framework import renderers
import json

#renderers are used to make responses more readable for front end by ensuring
#that errors are returned under keyword "error" and other data is returned
#under keyword "data"

class UserRenderer(renderers.JSONRenderer):
    charset = 'utf-8'

    #whenever drf returns responses, this function has to be called
    def render(self, data, accepted_media_type=None, renderer_context=None):
        #data: is the response we want to send back
        #we set this renderer for our authentication app in views file
        response = ''

        #check if response is sending errors
        if 'ErrorDetail' in str(data):
            response = json.dumps({'errors' : data})
        else:
            response = json.dumps({'data' : data})

        return response