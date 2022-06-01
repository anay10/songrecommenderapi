from django.shortcuts import render
from rest_framework import generics
from rest_framework import status, response

from .serializers import PredictUserEmotionSerializer

class PredictUserEmotion(generics.GenericAPIView):
    serializer_class = PredictUserEmotionSerializer
    def post(self, request):
        reqData = request.data
        #predict Emotion using model

        return response.Response({'emotion':reqData['xinput']}, status=status.HTTP_200_OK)