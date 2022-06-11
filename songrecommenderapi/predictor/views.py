from datetime import time, timedelta
from fileinput import filename
import random
from django.shortcuts import render
from rest_framework import generics
from rest_framework import status, response
import joblib

from .models import SongData

from .serializers import PredictUserEmotionSerializer

class PredictUserEmotion(generics.GenericAPIView):
    filename = 'emotion_classifier_pipe_lr.sav'
    serializer_class = PredictUserEmotionSerializer

    def randomize_songs(self, songs):
        songList = []
        for song in songs:
            songList.append(song)
        
        random.shuffle(songList)
        return songList[0]

    def post(self, request):
        reqData = request.data
        #load model
        emotion_classifier = joblib.load(open('emotion_classifier_pipe_lr.sav', 'rb'))

        #predict Emotion using model
        pred_result = emotion_classifier.predict([reqData['xinput']])
        pred_emotion = pred_result[0]
        songs = SongData.objects.filter(EMOTIONS = pred_emotion)
        songToReturn = self.randomize_songs(songs)
        return response.Response({'emotion':pred_emotion, 'id':songToReturn.SID, 'song':songToReturn.name}, status=status.HTTP_200_OK)

    