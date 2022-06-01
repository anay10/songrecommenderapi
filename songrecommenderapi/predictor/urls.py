from django.urls import path
from .views import PredictUserEmotion

urlpatterns = [
    path('emotion', PredictUserEmotion.as_view(), name='emotion')
]