from django.db import models

# Create your models here.

# 0 : neutral
# 1 : joy
# 2 : sadness
# 3 : fear
# 4 : surprise
# 5 : anger
# 6 : shame
# 7 : disgust

class SongData(models.Model):
    EMOTIONS = [
        ('neutral', 'neutral'),
        ('joy', 'joy'),
        ('sadness', 'sadness'),
        ('disgust', 'disgust'),
        ('fear', 'fear'),
        ('surprise', 'surprise'),
        ('anger', 'anger'),
        ('shame', 'shame'),
        ('disgust', 'disgust')
    ]

    name = models.CharField(max_length=255)
    EMOTIONS = models.CharField(choices=EMOTIONS, max_length=10)
    SID = models.CharField(max_length=255)