from django.db import models

class UserInfo(models.Model):
    username = models.CharField(max_length=64, unique=True)
    email = models.EmailField(null=True)
    password_hash = models.CharField(max_length=64, unique=True)
    daily_words_count = models.IntegerField(null=True,default=200)